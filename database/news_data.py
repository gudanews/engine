from database import DataBase
from datetime import datetime, timedelta
import unittest
import logging


class NewsDataDB(DataBase):

    def __init__(self):
        super(NewsDataDB, self).__init__("news_data")


class TestNewsDataDB(unittest.TestCase):

    def setUp(self):
        self.data = NewsDataDB()

    def _test_retrieve_all_records(self):
        columns = ["id", "headline_id", "datetime", "source_id", "heading", "url"]
        results = self.data.fetch_db_record(column=columns)
        self.assertGreater(len(results), 1)
        logging.info(results)

    def _test_retrieve_conditional_records(self):
        columns = ["id", "headline_id", "datetime", "source_id", "heading", "url"]
        conditions = ["id > 10", "source_id = 1"]
        results_1 = self.data.fetch_db_record(column=columns)
        results_2 = self.data.fetch_db_record(column=columns, condition=conditions)
        self.assertGreater(len(results_1), len(results_2))
        for r in results_2:
            self.assertGreater(r[0], 10)
        logging.info(results_1)
        logging.info(results_2)

if __name__ == "__main__":

    unittest.main()