from database import DataBase
from datetime import datetime, timedelta
import unittest
import logging
from database.source import SourceDB
from util.common import LoggedTestCase

logger = logging.getLogger("Database.Headline")


class NewsHeadlineDB(DataBase):

    def __init__(self):
        super(NewsHeadlineDB, self).__init__("news_headline")

    def get_latest_news(self, column=None, source=None):
        conditions = ["datetime BETWEEN '%(start_time)s' and '%(end_time)s'" %
                      {'start_time': datetime.strftime(datetime.now() - timedelta(hours=72), "%Y-%m-%d %H:%M:%S"),
                       'end_time': datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")}]
        if source and type(source) == type(0): # is integer
            conditions.append("source_id = '%d'" % source)
        elif source:
            src = SourceDB()
            conditions.append("source_id = '%s'" % src.get_source_id_by_name(source))
        return self.fetch_db_records(column=column, condition=conditions)


class TestNewHeadlineDB(LoggedTestCase):

    def setUp(self):
        self.data = NewsHeadlineDB()

    def test_get_latest_news(self):
        columns = ["id", "heading", "datetime", "source_id"]
        results = self.data.get_latest_news(column=columns)
        self.assertGreater(len(results), 0)
        first_news_date = results[0][2]
        start_date = datetime.now() - timedelta(hours=72)
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