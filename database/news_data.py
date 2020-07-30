from database import DataBase
from datetime import datetime, timedelta
import unittest
import logging
from util.common import LoggedTestCase
from database.source import SourceDB

logger = logging.getLogger("DataBase.NewsData")


class NewsDataDB(DataBase):

    def __init__(self):
        super(NewsDataDB, self).__init__("news_data")

    def get_latest_news(self, column=None, source=None):
        conditions = ["datetime BETWEEN '%(start_time)s' and '%(end_time)s'" %
                      {'start_time': datetime.strftime(datetime.now() - timedelta(hours=72), "%Y-%m-%d %H:%M:%S"),
                       'end_time': datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")}]
        if source and type(source) == type(0):  # is integer
            conditions.append("source_id = '%d'" % source)
        elif source:
            src = SourceDB()
            conditions.append("source_id = '%s'" % src.get_source_id_by_name(source))
        return self.fetch_db_records(column=column, condition=conditions)


class TestNewsDataDB(LoggedTestCase):

    def setUp(self):
        self.data = NewsDataDB()

    def _test_retrieve_all_records(self):
        columns = ["id", "headline_id", "datetime", "source_id", "heading", "url"]
        results = self.data.fetch_db_record(column=columns)
        self.assertGreater(len(results), 1)
        logger.info(results)

    def _test_retrieve_conditional_records(self):
        columns = ["id", "headline_id", "source_id", "heading", "url", "datetime", "link", "snippet", "image"]
        conditions = ["id > 10", "source_id = 1"]
        results_1 = self.data.fetch_db_records(column=columns)
        results_2 = self.data.fetch_db_records(column=columns, condition=conditions)
        self.assertGreater(len(results_1), len(results_2))
        for r in results_2:
            self.assertGreater(r[0], 10)
        logger.info(results_1)
        logger.info(results_2)


if __name__ == "__main__":
    unittest.main()
