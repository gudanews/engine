import sys
from setuptools import find_packages
from pkgutil import iter_modules

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
            public_classes[dir_name] = dir_obj
    return public_classes