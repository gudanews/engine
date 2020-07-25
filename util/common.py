import unittest
import logging
import sys

class MetaClassSingleton(type):
    """
    Meta class implementation
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Override __call__ special method based on singleton pattern
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaClassSingleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]


class LoggedTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from util.config_util import Configure

        loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        for logger in loggers:
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(logging.Formatter("[%(asctime)s]\t%(name)-12s\t[%(levelname)s]\t%(message)s"))
            logger.setLevel(int(Configure().setting["logging_level"]))
            logger.addHandler(stream_handler)
            logger.propagate = False
