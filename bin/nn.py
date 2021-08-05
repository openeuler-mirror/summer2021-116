from core.utils.log import lg, LEVELS, info, debug, warn, error, output


class NestNetRunner(object):
    def __init__(self):
        self.args = None
        self.parseArgs()
        self.setup()

    def parseArgs(self):
        """
        Use argparse library.
        Parse command-line args and return args object.
        :return:
        """
        pass

    def setup(self):
        """
        Setup and validate environment.
        :return:
        """
        if LEVELS[self.args.verbosity] > LEVELS["output"]:
            warn("*** WARNING: selected verbosity level (%s) will hide CLI output!\n"
                 "Please restart NestNet with -v [debug, info, output].\n")
        lg.setLogLevel(self.args.verbosity)


    def begin(self):
        """
        Create and run nestnet.
        :return:
        """
        global CLI

        args = self.args

        if args.cluster:
            servers = args.cluster.split(",")
            for server in servers:
                ClusterCleanup.add(server)

if __name__ == '__main__':
    try:
        NestNetRunner()
