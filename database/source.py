from database import DataBase
import unittest
import logging
from util import LoggedTestCase

logger = logging.getLogger("DataBase.Source")

class SourceDB(DataBase):

    def __init__(self):
        super(SourceDB, self).__init__("source")

    def get_source_id_by_name(self, name):
        return self.fetch_db_record(column="id", condition=["name = '%s'" % name])


class TestSourceData(LoggedTestCase):

    def setUp(self):
        self.data = SourceDB()

    def test_get_source_id_by_name(self):
        result = self.data.get_source_id_by_name("Reuters")
        self.assertEqual(result[0], 1)

    def test_get_non_exist_resource_id(self):
        id = self.data.get_source_id_by_name('does_not_exist')
        self.assertIsNone(id)
        logger.info(id)

if __name__ == "__main__":
    unittest.main()