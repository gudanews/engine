from database import DataBase
import unittest
import logging
from util.common import LoggedTestCase

logger = logging.getLogger("DataBase.Source")

class SourceDB(DataBase):

    def __init__(self):
        super(SourceDB, self).__init__("source")

    def get_source_id_by_name(self, name):
        result = self.fetch_db_record(column="id", condition=["name = '%s'" % name])
        return result[0] if result else 0

    def get_source_name_by_id(self, id):
        result = self.fetch_db_record(column="name", condition=["id = '%s'" % id])
        return result[0] if result else ""

class TestSourceData(LoggedTestCase):

    def setUp(self):
        self.data = SourceDB()

    def test_get_source_id_by_name(self):
        result = self.data.get_source_id_by_name("Reuters")
        self.assertEqual(result, 1)

    def test_get_non_exist_resource_id(self):
        id = self.data.get_source_id_by_name('does_not_exist')
        self.assertEqual(id, 0)
        logger.info("test_get_non_exist_resource_id: %s" % id)

if __name__ == "__main__":
    unittest.main()