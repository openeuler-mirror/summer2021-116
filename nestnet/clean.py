from __future__ import unicode_literals

try:
    from builtins import str
except ImportError:
    pass
from subprocess import (Popen, PIPE, check_output as co,
                        CalledProcessError)
from subprocess import call
import time
import os
import iptc
import ipaddress
import shlex
import isulapy.isula as isula

from nestnet.log import info
from nestnet.term import cleanUpScreens
from nestnet.util import decode
from nestnet.net import SAP_PREFIX


# noinspection PySingleQuotedDocstring
def sh(cmd):
    "Print a command and send it to the shell"
    info(cmd + '\n')
    result = Popen(['/bin/sh', '-c', cmd], stdout=PIPE).communicate()[0]
    return decode(result)


# noinspection PySingleQuotedDocstring
def killprocs(pattern):
    "Reliably terminate processes matching a pattern (including args)"
    sh('pkill -9 -f %s' % pattern)
    # Make sure they are gone
    while True:
        try:
            pids = co(['pgrep', '-f', pattern])
        except CalledProcessError:
            pids = ''
        if pids:
            sh('pkill -9 -f %s' % pattern)
            time.sleep(.5)
        else:
            break


class Cleanup(object):
    "Wrapper for cleanup()"

    callbacks = []

    @classmethod
    def cleanup(cls):
        """Clean up junk which might be left over from old runs;
           do fast stuff before slow dp and link removal!"""

        info("*** Removing excess controllers/ofprotocols/ofdatapaths/"
             "pings/noxes\n")
        zombies = ('controller ofprotocol ofdatapath ping nox_core'
                   'lt-nox_core ovs-openflowd ovs-controller'
                   'ovs-testcontroller udpbwtest nnexec ivs ryu-manager')
        # Note: real zombie processes can't actually be killed, since they
        # are already (un)dead. Then again,
        # you can't connect to them either, so they're mostly harmless.
        # Send SIGTERM first to give processes a chance to shutdown cleanly.
        sh('killall ' + zombies + ' 2> /dev/null')
        time.sleep(1)
        sh('killall -9 ' + zombies + ' 2> /dev/null')

        # And kill off sudo nnexec
        sh('pkill -9 -f "sudo nnexec"')

        info("*** Removing junk from /tmp\n")
        sh('rm -f /tmp/vconn* /tmp/vlogs* /tmp/*.out /tmp/*.log')

        info("*** Removing old X11 tunnels\n")
        cleanUpScreens()

        info("*** Removing excess kernel datapaths\n")
        dps = sh("ps ax | egrep -o 'dp[0-9]+' | sed 's/dp/nl:/'"
                 ).splitlines()
        for dp in dps:
            if dp:
                sh('dpctl deldp ' + dp)

        info("***  Removing OVS datapaths\n")
        dps = sh("ovs-vsctl --timeout=1 list-br").strip().splitlines()
        if dps:
            sh("ovs-vsctl " + " -- ".join("--if-exists del-br " + dp
                                          for dp in dps if dp))
        # And in case the above didn't work...
        dps = sh("ovs-vsctl --timeout=1 list-br").strip().splitlines()
        for dp in dps:
            sh('ovs-vsctl del-br ' + dp)

        info("*** Removing all links of the pattern foo-ethX\n")
        links = sh("ip link show | "
                   "egrep -o '([-_.[:alnum:]]+-eth[[:digit:]]+)'"
                   ).splitlines()
        # Delete blocks of links
        n = 1000  # chunk size
        for i in range(0, len(links), n):
            cmd = ';'.join('ip link del %s' % link
                           for link in links[i: i + n])
            sh('( %s ) 2> /dev/null' % cmd)

        if 'tap9' in sh('ip link show'):
            info("*** Removing tap9 - assuming it's from cluster edition\n")
            sh('ip link del tap9')

        info("*** Killing stale mininet node processes\n")
        killprocs('mininet:')

        info("*** Shutting down stale tunnels\n")
        killprocs('Tunnel=Ethernet')
        killprocs('.ssh/mn')
        sh('rm -f ~/.ssh/mn/*')

        # Call any additional cleanup code if necessary
        for callback in cls.callbacks:
            callback()

        # Nestnet should also cleanup pending Isula
        isula.clean()

        # cleanup any remaining iptables rules from external SAPs with NAT
        # we use iptc module to iterate through the loops, but due to a bug, we cannot use iptc to delete the rules
        # we rely on iptables CLI to delete the found rules
        info("***  Removing SAP NAT rules\n")
        table = iptc.Table(iptc.Table.NAT)
        chain = iptc.Chain(table, 'POSTROUTING')

        for rule in chain.rules:
            if SAP_PREFIX in str(rule.out_interface):
                src_CIDR = str(ipaddress.IPv4Network(u'{}'.format(str(rule.src))))
                rule0_ = "iptables -t nat -D POSTROUTING ! -o {0} -s {1} -j MASQUERADE". \
                    format(rule.out_interface.strip('!'), src_CIDR)
                p = Popen(shlex.split(rule0_))
                p.communicate()
                info("delete NAT rule from SAP: {1} - {0} - {2}\n".format(rule.out_interface, rule.in_interface,
                                                                          src_CIDR))

        table = iptc.Table(iptc.Table.FILTER)
        chain = iptc.Chain(table, 'FORWARD')
        for rule in chain.rules:
            src_CIDR = str(ipaddress.IPv4Network(u'{}'.format(str(rule.src))))
            if SAP_PREFIX in str(rule.out_interface):
                rule1_ = "iptables -D FORWARD -o {0} -j ACCEPT".format(rule.out_interface)
                p = Popen(shlex.split(rule1_))
                p.communicate()
                info("delete FORWARD rule from SAP: {1} - {0} - {2}\n".format(rule.out_interface, rule.in_interface,
                                                                              src_CIDR))

            if SAP_PREFIX in str(rule.in_interface):
                rule2_ = "iptables -D FORWARD -i {0} -j ACCEPT".format(rule.in_interface)
                p = Popen(shlex.split(rule2_))
                p.communicate()
                info("delete FORWARD rule from SAP: {1} - {0} - {2}\n".format(rule.out_interface, rule.in_interface,
                                                                              src_CIDR))

        info("*** Cleanup complete.\n")

    @classmethod
    def addCleanupCallback(cls, callback):
        """Add cleanup callback"""
        if callback not in cls.callbacks:
            cls.callbacks.append(callback)


cleanup = Cleanup.cleanup
addCleanupCallback = Cleanup.addCleanupCallback
