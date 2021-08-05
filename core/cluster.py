import os


def findUser():
    """
    Try to return logged-in (usually non-root) user
    :return:
    """
    return (
            # If we're running sudo
            os.environ.get("SUDO_USER", False) or
            # Logged-in user (if we have a tty)
            (quietRun('who am i').split() or [False])[0] or
            # Give up and return effective user
            quietRun('whoami').strip())


class ClusterCleanup(object):
    """
    Cleanup callback
    """

    inited = False
    server_user = {}

    @classmethod
    def add(cls, server, user=""):
        """
        Add an entry to server: user dict
        :param server:
        :param user:
        :return:
        """
        if not cls.inited:
            addCleanupCallback(cls.cleanup)
        if not user:
            user = findUser()
        cls.server_user[server] = user

    @classmethod
    def cleanup(cls):
        "Clean up"
        info('*** Cleaning up cluster\n')
        for server, user in list(cls.server_user.items()):
            if server == 'localhost':
                # Handled by nestnet.clean.cleanup()
                continue
            else:
                cmd = ['su', user, '-c',
                       'ssh %s@%s sudo mn -c' % (user, server)]
                info(cmd, '\n')
                info(quietRun(cmd))