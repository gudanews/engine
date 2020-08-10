from database import DataBase
import unittest
from datetime import datetime, timedelta
import logging
from database.source import SourceDB
from database import MANDATORY, OPTIONAL
import time


logger = logging.getLogger("DataBase.News")


class NewsDB(DataBase):

    COLUMN_CONSTRAINT = {
        "id": (int, MANDATORY),
        "uuid": (str, MANDATORY),
        "is_valid": (int, OPTIONAL),
        "is_indexed": (int, OPTIONAL),
        "headline_id": (int, OPTIONAL),
        "category_id": (int, OPTIONAL),
        "source_id": (int, MANDATORY),
        "image_id": (int, OPTIONAL),
        "author": (str, OPTIONAL),
        "heading": (str, MANDATORY),
        "snippet": (str, OPTIONAL),
        "url": (str, MANDATORY),
        "datetime": (datetime, OPTIONAL),
        "body_id": (int, OPTIONAL),
        "likes": (int, OPTIONAL)
    }
    INSERT_COLUMN_CONSTRAINT = ["uuid", "is_valid", "is_indexed", "headline_id", "category_id", "source_id",
                                "image_id", "author", "heading", "snippet", "url", "datetime", "body_id", "likes"]
    UPDATE_COLUMN_CONSTRAINT = ["id", "uuid", "is_valid", "is_indexed", "headline_id", "category_id", "source_id",
                                "image_id", "author", "heading", "snippet", "url", "datetime", "body_id", "likes"]
    SELECT_COLUMN_CONSTRAINT = ["id", "uuid", "is_valid", "is_indexed", "headline_id", "category_id", "source_id",
                                "image_id", "author", "heading", "snippet", "url", "datetime", "body_id", "likes"]


    def __init__(self, user=None, password=None, host=None, database=None):
        super(NewsDB, self).__init__("news", user=user, password=password, host=host, database=database)

    def get_news_by_id(self, id, column=None):
        if not column:
            column = self.SELECT_COLUMN_CONSTRAINT
        conditions = "id = %d" % id
        return self.fetch_record(column=column, condition=conditions)

    def get_news_by_uuid(self, uuid, column=None):
        if not column:
            column = self.SELECT_COLUMN_CONSTRAINT
        conditions = "uuid = '%s'" % uuid
        return self.fetch_record(column=column, condition=conditions)

    def get_latest_news(self, column=None, condition=None, max_count=0):
        if not column:
            column = self.SELECT_COLUMN_CONSTRAINT
        conditions = ["datetime > '%s'" % (datetime.strftime(datetime.now() - timedelta(days=14), "%Y-%m-%d %H:%M:%S"))]
        if isinstance(condition, str):
            conditions.append(condition)
        elif isinstance(condition, list):
            conditions.extend(condition)
        limit = None
        if max_count:
            limit = max_count
        return self.fetch_records(column=column, condition=conditions, limit=limit)

    def get_latest_news_by_source(self, source, column=None, max_count=0):
        if not source or not (isinstance(source, int) or isinstance(source, str)):
            raise Exception("Please specify <source> to use get_latest_news_by_source method")
        source = SourceDB().get_source_id_by_name(source) if isinstance(source, str) else source
        condition = ["source_id = %d" % source]
        return self.get_latest_news(column=column, condition=condition, max_count=max_count)

    def get_non_indexed_news(self, column=None, condition=None, max_count=0):
        if not column:
            column = ["id", "url"]
        conditions = ["is_indexed = 0"]
        if isinstance(condition, str):
            conditions.append(condition)
        elif isinstance(condition, list):
            conditions.extend(condition)
        limit = None
        if max_count:
            limit = max_count
        return self.fetch_records(column=column, condition=conditions, limit=limit)

    def get_non_indexed_news_by_source(self, source, column=None, max_count=0):
        if not source or not (isinstance(source, int) or isinstance(source, str)):
            raise Exception("Please specify <source> to use get_latest_news_by_source method")
        source = SourceDB().get_source_id_by_name(source) if isinstance(source, str) else source
        condition = ["source_id = %d" % source]
        return self.get_non_indexed_news(column=column, condition=condition, max_count=max_count)

    def get_news_by_headline(self, headline, column=None):
        if not headline or not (isinstance(headline, int) or isinstance(headline, str)):
            raise Exception("Please specify <headline> to use get_latest_news_by_source method")
        if isinstance(headline, str): #uuid
            adv_query = "INNER JOIN headline ON headline.id = news.headline_id where headline.uuid='%s'" % headline
            return self.fetch_advanced_records(column=column, advanced=adv_query)
        else: #id
            conditions = "headline_id = %d" % id
            return self.fetch_records(column=column, condition=conditions)

    def add_news(self, record):
        uid = self.generate_uuid()
        record["uuid"] = uid
        if self.insert_record(record=record):
            return self._db._cursor.lastrowid
        return 0

    def update_news_by_id(self, id, record):
        return self.update_record(record=record, condition="id = %d" % id)

    def update_news_by_uuid(self, uuid, record):
        return self.update_record(record=record, condition="uuid = '%s'" % uuid)


from util.config_util import Configure
from util.common import LoggedTestCase

config = Configure()

SANDBOX_USER = config.sandbox["db_user"]
SANDBOX_PASSWORD = config.sandbox["db_password"]
SANDBOX_HOST = config.sandbox["db_host"]
SANDBOX_DATABASE = config.sandbox["db_schema"]


class TestNewsDataDB(LoggedTestCase):

    def setUp(self):
        self.data = NewsDB(user=SANDBOX_USER, password=SANDBOX_PASSWORD, host=SANDBOX_HOST, database=SANDBOX_DATABASE)
        self.data.delete_records()
        self.data.add_news(record=dict(source_id=1, uuid="1", url="http://www.reuters.com/news1", heading="News heading1"))
        self.data.add_news(record=dict(source_id=2, uuid="2", url="http://www.ap.com/news2", heading="News heading2"))
        self.data.add_news(record=dict(source_id=1, uuid="3", url="http://www.cnn.com/news3", heading="News heading3"))
        self.data.add_news(record=dict(source_id=3, uuid="4", url="http://www.foxnews.com/news4", heading="News heading4"))
        time.sleep(1.0)


    def test_get_latest_news(self):
        columns = ["id", "uuid", "datetime", "heading", "source_id"]
        results = self.data.get_latest_news(column=columns)
        self.assertEqual(len(results), 4)
        first_news_date = results[0][2]
        start_date = datetime.now() - timedelta(hours=96)
        end_date = datetime.now()
        self.assertTrue(start_date <= first_news_date <= end_date)

    def test_get_latest_news_by_source(self):
        results = self.data.get_latest_news_by_source(source=1)
        self.assertEqual(len(results), 2)
        results = self.data.get_latest_news_by_source(source="AP")
        self.assertEqual(len(results), 1)

    def test_add_news(self):
        record = dict(source_id=1, uuid="5", heading="H1", url="http://www.reuters.com/h1news")
        result = self.data.add_news(record)
        self.assertGreater(result, 0)
        record = dict(source_id=1, uuid="6", url="http://www.reuters.com/h1news")
        result = self.data.add_news(record)
        self.assertEqual(result, 0)

    def _test_update_news_by_id(self):
        columns = ["id", "uuid", "heading"]
        record = dict(heading="Heading123")
        id = self.data.fetch_record(column="id", condition="source_id=1")[0]
        self.data.update_headline_by_id(id=id, record=record)
        result = self.data.get_headline_by_id(id=id, column=columns)
        self.assertEqual(result[2], "Heading123")
        record = dict(heading="Heading456")


if __name__ == "__main__":
    unittest.main()
