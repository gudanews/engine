import inspect
import sys
from setuptools import find_packages
from pkgutil import iter_modules
import logging
from util.config_util import Configure
import random
import string
import os
from math import log, floor


config = Configure()
logging.basicConfig(level=int(config.setting["logging_level"]),
                    format='[%(asctime)s]  %(name)-12s\t[%(levelname)s]\t%(message)s',
                    datefmt='%m-%d %H:%M:%S')


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

def generate_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result

def create_parent_folders(path):
    folder = os.path.dirname(path)
    if not os.path.exists(folder):
        os.makedirs(folder)

def human_format(number):
    units = ['', 'K', 'M', 'G', 'T', 'P']
    k = 1024.0
    magnitude = int(floor(log(number, k)))
    return '%.2f%s' % (number / k**magnitude, units[magnitude])



