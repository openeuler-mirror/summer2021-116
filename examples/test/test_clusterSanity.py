#!/usr/bin/env python

'''
A simple sanity check test for cluster edition
'''

import unittest
from nestnet.util import pexpect

class clusterSanityCheck( unittest.TestCase ):

    prompt = 'nestnet>'

    def testClusterPingAll( self ):
        p = pexpect.spawn( 'python -m nestnet.examples.clusterSanity' )
        p.expect( self.prompt )
        p.sendline( 'py net.waitConnected()' )
        p.expect( self.prompt )
        p.sendline( 'pingall' )
        p.expect ( '(\d+)% dropped' )
        percent = int( p.match.group( 1 ) ) if p.match else -1
        self.assertEqual( percent, 0 )
        p.expect( self.prompt )
        p.sendline( 'exit' )
        p.wait()


if __name__  == '__main__':
    unittest.main()
