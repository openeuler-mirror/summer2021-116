import logging
import types
from logging import Logger

OUTPUT = 25

LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "output": OUTPUT,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

# change this to logging.INFO to get printouts when running unit tests
LOG_LEVEL_DEFAULT = OUTPUT

LOG_MSG_FORMAT = "%(message)s"


class Singleton(type):
    def __init__(cls, name, bases, dict_):
        super(Singleton, cls).__init__(name, bases, dict_)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instance


class StreamHandlerNoNewLine(logging.StreamHandler):
    """
    StreamHandler that doesn't print newlines by default.
    Since StreamHandler automatically adds newlines,
    define a mod to more easily support interactive mode when we want it,
    or errors-only logging for running unit tests.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a record.
        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline
        [ N.B. this may be removed depending on feedback ]. If exception
        information is present, it is formatted using traceback.printException and appended to the stream.
        :param record:
        :return:
        """
        try:
            msg = self.format(record)
            fs = "%s"
            if not hasattr(types, "UnicodeType"):
                # if no unicode support
                self.stream.write(fs % msg)
            else:
                try:
                    self.stream.write(fs % msg)
                except UnicodeError:
                    self.stream.write(fs % msg.encode("UTF-8"))
            self.flush()
        except(KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class NestNetLogger(Logger, object):
    """
    NestNet-specific logger
    Enable each NestNet .py file to with one import: from utils.log import [lg, info, error]
    to get a default logger that doesn't require one newline per logging call.
    Inherit from object to ensure that we have at least one new-style base class
    and can then use the __metaclass__ directive, to prevent this error:
    TypeError: Error when calling the metaclass bases
    a new-style class can't have only classic bases
    Use singleton pattern to ensure only one logger is ever created
    """
    __metaclass__ = Singleton

    def __init__(self):
        Logger.__init__(self, "NestNet")

        # create console handler
        ch = StreamHandlerNoNewLine()

        # create formatter
        formatter = logging.Formatter(LOG_MSG_FORMAT)

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to lg
        self.addHandler(ch)

        self.setLogLevel()

    def setLogLevel(self, level_name=None):
        """
        Setup loglevel.
        Convenience function to support lowercase names.
        levelName: level name from LEVELS.
        :param level_name: 
        :return: 
        """

        level = LOG_LEVEL_DEFAULT
        if level_name is not None:
            if level_name not in LEVELS:
                raise Exception("Unknown level name seen in setLogLevel")
            else:
                level = LEVELS.get(level_name, level)

        self.setLevel(level)
        self.handlers[0].setLevel(level)


lg = NestNetLogger()


def makeListCompatible(fn):
    """
    Return a new function allowing fn( "a 1 b" ) to be called as new fn( "a", 1, "b" )
    :param fn:
    :return:
    """
    def new_fn(*args):
        """
        Generated function. Closure-ish.
        :param args:
        :return:
        """
        if len(args) == 1:
            return fn(*args)
        args = " ".join(str(arg) for arg in args)
        return fn(args)


_loggers = lg.info, lg.output, lg.warning, lg.error, lg.debug
_loggers = tuple(makeListCompatible(logger) for logger in _loggers)
lg.info, lg.output, lg.warning, lg.error, lg.debug = _loggers
info, output, warn, error, debug = _loggers

setLogLevel = lg.setLogLevel
