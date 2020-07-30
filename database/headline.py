from database import DataBase
from datetime import datetime, timedelta
import unittest
import logging
from database.source import SourceDB
from util.common import LoggedTestCase

logger = logging.getLogger("Database.Headline")


class HeadlineDB(DataBase):

    def __init__(self):
        super(HeadlineDB, self).__init__("headline")

    def get_latest_news(self, column=None, source=None):
        conditions = ["datetime > '%s'" %
                      (datetime.strftime(datetime.now() - timedelta(hours=96), "%Y-%m-%d %H:%M:%S"))]
        if source and type(source) == type(0): # is integer
            conditions.append("source_id = '%d'" % source)
        elif source:
            src = SourceDB()
            conditions.append("source_id = '%s'" % src.get_source_id_by_name(source))
        return self.fetch_db_records(column=column, condition=conditions)

    def add_headline(self, record):
        self.insert_db_record(record=record)
        return self.db._cursor.lastrowid


class TestNewHeadlineDB(LoggedTestCase):

    def setUp(self):
        self.data = HeadlineDB()

    def test_get_latest_news(self):
        columns = ["id", "heading", "datetime", "source_id"]
        results = self.data.get_latest_news(column=columns)
        self.assertGreater(len(results), 0)
        first_news_date = results[0][2]
        start_date = datetime.now() - timedelta(hours=96)
        end_date = datetime.now()
        self.assertTrue(start_date <= first_news_date <= end_date)
        logger.info(results)

    def test_get_latest_news_from_source(self):
        results = self.data.get_latest_news(source=1)
        self.assertGreater(len(results), 0)
        results = self.data.get_latest_news(source="Reuters")
        self.assertGreater(len(results), 0)
        logger.info(results)


if __name__ == "__main__":

    unittest.main()