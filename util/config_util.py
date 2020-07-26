import os
from configparser import RawConfigParser
from util.common import MetaClassSingleton
import logging
from util.common import LoggedTestCase
import unittest


logger = logging.getLogger("Until.Config")

CONFIG_FILE = os.environ.get("CONFIG_FILE", os.path.abspath(os.path.dirname(__file__) + "/../gudanews.cfg"))
ENVIRONMENT = os.environ.get("ENVIRONMENT", "SANDBOX")

class Configure:

    __metaclass__ = MetaClassSingleton

    def __init__(self, file=CONFIG_FILE):
        if not os.path.exists(file):
            raise Exception("Cannot find configure file located at [%s]" % file)
        self._parser = RawConfigParser()
        self._parser.read(file)
        self._production = None
        self._sandbox = None
        self._default = None

    def get(self, section, option):
        return self._parser.get(section, option)

    @property
    def sections(self):
        return self._parser.sections()

    @property
    def production(self):
        if not self._production:
            if not self._parser.has_section("PRODUCTION"):
                raise Exception("Configure file doesn't contain section [PRODUCTION]")
            self._production = dict(self._parser["PRODUCTION"])
        return self._production

    @property
    def sandbox(self):
        if not self._sandbox:
            if not self._parser.has_section("SANDBOX"):
                raise Exception("Configure file doesn't contain section [SANDBOX]")
            self._sandbox = dict(self._parser["SANDBOX"])
        return self._sandbox

    @property
    def setting(self):
        if ENVIRONMENT == "PRODUCTION":
            return self.production
        elif ENVIRONMENT == "SANDBOX":
            return self.sandbox
        else:
            raise Exception("ENVIRONMENT must be either [PRODUCTION] or [SANDBOX], but receive [%s]" % ENVIRONMENT)


class TestConfigParser(LoggedTestCase):

    def setUp(self):
        self.cfg = Configure()

    def test_default_config(self):
        self.assertTrue("PRODUCTION" in self.cfg.sections)
        self.assertTrue("SANDBOX" in self.cfg.sections)
        self.assertGreater(len(self.cfg.sections), 0)

    def test_non_exist_config_file(self):
        self.assertRaises(Exception, Configure, "does_not_exist")

    def test_default_values(self):
        global ENVIRONMENT
        ENVIRONMENT = "PRODUCTION"
        self.assertDictEqual(self.cfg.setting, self.cfg.production)
        ENVIRONMENT = "SANDBOX"
        self.assertDictEqual(self.cfg.setting, self.cfg.sandbox)

    def test_production_values(self):
        self.assertEqual(self.cfg.production["db_user"], "gudaman")

    def test_sandbox_values(self):
        self.assertEqual(self.cfg.sandbox["db_user"], "gudaboy")


if __name__ == '__main__':
    unittest.main()