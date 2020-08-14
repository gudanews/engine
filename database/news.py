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
        "id": (MANDATORY, int, 32),
        "uuid": (MANDATORY, str, 36),
        "is_valid": (OPTIONAL, int, 1),
        "is_indexed": (OPTIONAL, int, 1),
        "url": (MANDATORY, str, 512),
        "topic_id": (OPTIONAL, int, 32),
        "category_id": (OPTIONAL, int, 16),
        "source_id": (MANDATORY, int, 16),
        "image_id": (OPTIONAL, int, 32),
        "title": (MANDATORY, str, 256),
        "snippet": (OPTIONAL, str, 512),
        "content": (OPTIONAL, str, 128),
        "author": (OPTIONAL, str, 64),
        "datetime_created": (OPTIONAL, datetime),
        "datetime_updated": (OPTIONAL, datetime),
        "translation_id": (OPTIONAL, int, 32),
        "views": (OPTIONAL, int, 24)
    }
    INSERT_COLUMN_CONSTRAINT = ["uuid", "is_valid", "is_indexed", "url", "topic_id", "category_id", "source_id",
                                "image_id", "title", "snippet", "content", "author", "datetime_created",
                                "datetime_updated", "translation_id", "views"]
    UPDATE_COLUMN_CONSTRAINT = ["id", "uuid", "is_valid", "is_indexed", "url", "topic_id", "category_id", "source_id",
                                "image_id", "title", "snippet", "content", "author", "datetime_created",
                                "datetime_updated", "translation_id", "views"]
    SELECT_COLUMN_CONSTRAINT = ["id", "uuid", "is_valid", "is_indexed", "url", "topic_id", "category_id", "source_id",
                                "image_id", "title", "snippet", "content", "author", "datetime_created",
                                "datetime_updated", "translation_id", "views"]


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
        conditions = ["datetime_created > '%s'" % (datetime.strftime(datetime.now() - timedelta(days=14), "%Y-%m-%d %H:%M:%S"))]
        if isinstance(condition, str):
            conditions.append(condition)
        elif isinstance(condition, list):
            conditions.extend(condition)
        limit = None
        if max_count:
            limit = max_count
        return self.fetch_records(column=column, condition=conditions, limit=limit)

    def get_latest_news_by_source_id(self, source_id, column=None, max_count=0):
        condition = ["source_id = %d" % source_id]
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

    def get_non_indexed_news_by_source_id(self, source_id, column=None, max_count=0):
        condition = ["source_id = %d" % source_id]
        return self.get_non_indexed_news(column=column, condition=condition, max_count=max_count)

    def get_news_by_topic_id(self, topic_id, column=None):
        if isinstance(topic_id, str): #uuid
            adv_query = "INNER JOIN topic ON topic.id = news.topic_id where topic.uuid='%s'" % topic_id
            return self.fetch_advanced_records(column=column, advanced=adv_query)
        else: #id
            conditions = "topic_id = %d" % topic_id
            return self.fetch_records(column=column, condition=conditions)

    def add_news_use_record(self, record, ignore_extra_keys=True):
        uid = self.generate_uuid()
        record["uuid"] = uid
        if self.insert_record(record=record, ignore_extra_keys=ignore_extra_keys):
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
        self.data.add_news_use_record(record=dict(source_id=1, uuid="1", url="http://www.reuters.com/news1", title="News title1"),
                                      datetime_created=datetime.now() - timedelta(days=28))
        self.data.add_news_use_record(record=dict(source_id=2, uuid="2", url="http://www.ap.com/news2", title="News title2"))
        self.data.add_news_use_record(record=dict(source_id=1, uuid="3", url="http://www.cnn.com/news3", title="News title3"))
        self.data.add_news_use_record(record=dict(source_id=3, uuid="4", url="http://www.foxnews.com/news4", title="News title4"))
        time.sleep(1.0)


    def test_get_latest_news(self):
        columns = ["id", "uuid", "datetime_created", "title", "source_id"]
        results = self.data.get_latest_news(column=columns)
        self.assertEqual(len(results), 3)
        first_news_date = results[0][2]
        start_date = datetime.now() - timedelta(days=14)
        end_date = datetime.now()
        self.assertTrue(start_date <= first_news_date <= end_date)

    def test_get_latest_news_by_source_id(self):
        results = self.data.get_latest_news_by_source_id(source_id=1)
        self.assertEqual(len(results), 2)

    def test_add_news(self):
        record = dict(source_id=1, uuid="5", title="H1", url="http://www.reuters.com/h1news")
        result = self.data.add_news_use_record(record)
        self.assertGreater(result, 0)
        record = dict(source_id=1, uuid="6", title="H1", url="http://www.reuters.com/h1news",
                      datetime_created=datetime.now() - timedelta(days=28))
        result = self.data.add_news_use_record(record)
        self.assertEqual(result, 0)

    def test_update_news_by_id(self):
        columns = ["id", "uuid", "title"]
        record = dict(title="Title123")
        id = self.data.fetch_record(column="id", condition="source_id=1")[0]
        result = self.data.get_news_by_id(id=id, column=columns)
        self.assertEqual(result[2], "Title123")


if __name__ == "__main__":
    unittest.main()
