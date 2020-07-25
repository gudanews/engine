import os
from configparser import ConfigParser
from util import MetaClassSingleton
import logging
from util import LoggedTestCase
import unittest


logger = logging.getLogger("Until.Config")

CONFIG_FILE = os.environ.get("CONFIG_FILE", "gudanews.cfg")

class Configure(metaclass=MetaClassSingleton):
    config = None
    def retriev(self):
        if self.config is None:
            self.config = ConfigParser()
            self.config.read(CONFIG_FILE)
        return self.config


def get_configure(section, item):
    pass


class TestConfigParser(LoggedTestCase):

    def test_config(self):
        pass

if __name__ == '__main__':
    unittest.main()