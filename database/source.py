from database import DataBase
import unittest
import logging
from database import MANDATORY, OPTIONAL
from typing import List, Dict, Tuple, Optional, Any


logger = logging.getLogger("DataBase.Source")

class SourceDB(DataBase):

    COLUMN_CONSTRAINT = {
        "id": (MANDATORY, int, 16),
        "short_name": (MANDATORY, str, 8),
        "full_name": (OPTIONAL, str, 32),
        "color": (OPTIONAL, str, 8),
        "image_id": (OPTIONAL, int, 32),
        "website": (OPTIONAL, str, 128),
        "bias": (OPTIONAL, int, 8),
        "quality": (OPTIONAL, int, 16),
        "popularity": (OPTIONAL, float)
    }
    INSERT_COLUMN_CONSTRAINT = ["short_name", "full_name", "color", "image_id", "website", "bias", "quality", "popularity"]
    UPDATE_COLUMN_CONSTRAINT = ["id", "short_name", "full_name", "color", "image_id", "website", "bias", "quality", "popularity"]
    SELECT_COLUMN_CONSTRAINT = ["id", "short_name", "full_name", "color", "image_id", "website", "bias", "quality", "popularity"]

    def __init__(self, user=None, password=None, host=None, database=None):
        # type: (Optional[str], Optional[str], Optional[str], Optional[str]) -> None
        super(SourceDB, self).__init__("source", user=user, password=password, host=host, database=database)

    def get_source_id_by_name(self, name):
        # type: (str) -> int
        result = self.fetch_record(column=["id"], condition=["short_name = '%s'" % name])
        return result[0] if result else 0

    def get_source_name_by_id(self, id):
        # type: (int) -> str
        result = self.fetch_record(column=["short_name"], condition=["id = %d" % id])
        return result[0] if result else None


from util.config_util import Configure
from util.common import LoggedTestCase

config = Configure()

SANDBOX_USER = config.sandbox["db_user"]
SANDBOX_PASSWORD = config.sandbox["db_password"]
SANDBOX_HOST = config.sandbox["db_host"]
SANDBOX_DATABASE = config.sandbox["db_schema"]


class TestSourceData(LoggedTestCase):

    def setUp(self):
        self.data = SourceDB(user=SANDBOX_USER, password=SANDBOX_PASSWORD, host=SANDBOX_HOST, database=SANDBOX_DATABASE)

    def test_get_source_id_by_name(self):
        result = self.data.get_source_id_by_name("REU")
        self.assertEqual(result, 1)

    def test_get_non_exist_resource_id(self):
        id = self.data.get_source_id_by_name('does_not_exist')
        self.assertEqual(id, 0)
        logger.info("test_get_non_exist_resource_id: %s" % id)


if __name__ == "__main__":
    unittest.main()