from database import DataBase
from datetime import datetime, timedelta
import unittest
import logging

class SourceDB(DataBase):

    def __init__(self):
        super(SourceDB, self).__init__("source")

    def get_source_id_by_name(self, name):
        result = self.fetch_db_record(column="id", condition=["name = '%s'" % name])
        return result[0] if result else None


class TestSourceData(unittest.TestCase):

    def setUp(self):
        self.data = SourceDB()

    def test_get_source_id_by_name(self):
        result = self.data.get_source_id_by_name("Reuters")
        self.assertEqual(result[0], 1)

    def test_get_non_exist_resource_id(self):
        id = self.data.get_source_id_by_name('does_not_exist')
        self.assertIsNone(id)
        logging.info(id)

if __name__ == "__main__":

    unittest.main()