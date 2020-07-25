import difflib as dl
import inspect
import sys
from setuptools import find_packages
from pkgutil import iter_modules
import unittest
import logging


def find_modules(path):
    modules = set()
    for pkg in find_packages(path):
        modules.add(pkg)
        pkgpath = path + '/' + pkg.replace('.', '/')
        if sys.version_info.major == 2 or (sys.version_info.major == 3 and sys.version_info.minor < 6):
            for _, name, ispkg in iter_modules([pkgpath]):
                if not ispkg:
                    modules.add(pkg + '.' + name)
        else:
            for info in iter_modules([pkgpath]):
                if not info.ispkg:
                    modules.add(pkg + '.' + info.name)
    else:
        if sys.version_info.major == 2 or (sys.version_info.major == 3 and sys.version_info.minor < 6):
            for _, name, ispkg in iter_modules([path]):
                if not ispkg:
                    modules.add(name)
        else:
            for info in iter_modules([path]):
                if not info.ispkg:
                    modules.add(info.name)

    return modules

def find_public_classes(module):
    public_classes = {}
    exec('import ' + module)
    obj = sys.modules[module]
    for dir_name in dir(obj):
        if not dir_name.startswith('_'):
            dir_obj = getattr(obj, dir_name)
            if inspect.isclass(dir_obj):
                public_classes[dir_name] = dir_obj
    return public_classes


def checksimilarity(a, b):
    sim = dl.get_close_matches

    s = 0
    wa = a.split()
    wb = b.split()

    for i in wb:
        if sim(i, wa):
            s += 1

    n = float(s) / float(len(wb))
    return n


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

    loggingLevel = logging.INFO

    @classmethod
    def setUpClass(cls):
        loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        for logger in loggers:
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(logging.Formatter("[%(asctime)s]\t%(name)-12s\t[%(levelname)s]\t%(message)s"))
            logger.setLevel(cls.loggingLevel)
            logger.addHandler(stream_handler)
            logger.propagate = False

