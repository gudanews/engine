from util.mysql_util import MySQLDB
import logging
import unittest
from datetime import datetime, timedelta

class DataBase:
    def __init__(self, table):
        self.db = MySQLDB(user="gudaman", password= "GudaN3w2", host="192.168.1.49", database= "gudanews")
        self.table = table
        self._table_schema = None

    @property
    def table_schema(self):
        if not self._table_schema:
            self._table_schema= self.db.get_table_schema(self.table)
        return self._table_schema

    def insert_db_record(self, record):
        return self.db.insert_table_record(self.table, record)

    def fetch_db_records(self, column=None, condition=None, order_by=None):
        return self.db.fetch_table_records(self.table, column, condition, order_by)

    def fetch_db_record(self, column=None, condition=None, order_by=None):
        return self.db.fetch_table_record(self.table, column, condition, order_by)


class TestBaseData(unittest.TestCase):

    def setUp(self):
        self.data = DataBase("news_headline")

    def test_retrieve_one_record(self):
        columns = ["id", "heading", "datetime", "source_id"]
        result = self.data.fetch_db_record(column=columns)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 4)
        logging.info(result)

    def test_retrieve_all_records(self):
        columns = ["id", "heading", "datetime", "source_id"]
        results = self.data.fetch_db_records(column=columns)
        self.assertGreater(len(results), 1)
        self.assertEqual(len(results[0]), 4)
        logging.info(results)

    def test_retrieve_conditional_records(self):
        columns = ["id", "heading", "datetime", "source_id"]
        conditions = ["id > 10", "source_id = 1"]
        results_1 = self.data.fetch_db_record(column=columns)
        results_2 = self.data.fetch_db_record(column=columns, condition=conditions)
        self.assertGreater(len(results_1), len(results_2))
        for r in results_2:
            self.assertGreater(r[0], 10)
        logging.info(results_1)
        logging.info(results_2)

if __name__ == '__main__':
    unittest.main()