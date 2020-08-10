from database import DataBase
import unittest
import logging
from database import MANDATORY, OPTIONAL

logger = logging.getLogger("DataBase.Source")

class SourceDB(DataBase):

    COLUMN_CONSTRAINT = {
        "id": (int, MANDATORY),
        "is_crawling": (int, OPTIONAL),
        "crawling_url": (str, OPTIONAL),
        "name": (str, MANDATORY),
        "display_name": (str, OPTIONAL),
        "image_id": (str, OPTIONAL),
        "host": (str, OPTIONAL),
        "bias": (int, OPTIONAL),
        "quality": (int, OPTIONAL)
    }
    INSERT_COLUMN_CONSTRAINT = ["is_crawling", "crawling_url", "name", "display_name", "image_id", "host", "bias", "quality"]
    UPDATE_COLUMN_CONSTRAINT = ["id", "is_crawling", "crawling_url", "name", "display_name", "image_id", "host", "bias", "quality"]
    SELECT_COLUMN_CONSTRAINT = ["id", "is_crawling", "crawling_url", "name", "display_name", "image_id", "host", "bias", "quality"]

    def __init__(self, user=None, password=None, host=None, database=None):
        super(SourceDB, self).__init__("source", user=user, password=password, host=host, database=database)

    def get_source_id_by_name(self, name):
        result = self.fetch_record(column="id", condition=["name = '%s'" % name])
        return result[0] if result else 0

    def get_source_name_by_id(self, id):
        result = self.fetch_record(column="name", condition=["id = %d" % id])
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
        result = self.data.get_source_id_by_name("RUT")
        self.assertEqual(result, 1)

    def test_get_non_exist_resource_id(self):
        id = self.data.get_source_id_by_name('does_not_exist')
        self.assertEqual(id, 0)
        logger.info("test_get_non_exist_resource_id: %s" % id)


if __name__ == "__main__":
    unittest.main()