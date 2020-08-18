from database import DataBase
import unittest
from datetime import datetime, timedelta
import logging
from database.source import SourceDB
from database import MANDATORY, OPTIONAL
import time
from typing import List, Dict, Tuple, Optional, Any

logger = logging.getLogger("DataBase.News")


class NewsDB(DataBase):

    COLUMN_CONSTRAINT = {
        "id": (MANDATORY, int, 32),
        "uuid": (MANDATORY, str, 36),
        "debug": (OPTIONAL, bool),
        "is_valid": (OPTIONAL, bool),
        "is_indexed": (OPTIONAL, bool),
        "duplicate_id": (OPTIONAL, int, 32),
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
    INSERT_COLUMN_CONSTRAINT = ["uuid", "is_valid", "debug", "is_indexed", "duplicate_id", "url", "topic_id", "category_id",
                                "source_id", "image_id", "title", "snippet", "content", "author", "datetime_created",
                                "datetime_updated", "translation_id", "views"]
    UPDATE_COLUMN_CONSTRAINT = ["id", "uuid", "debug", "is_valid", "is_indexed", "duplicate_id", "url", "topic_id",
                                "category_id", "source_id", "image_id", "title", "snippet", "content", "author",
                                "datetime_created", "datetime_updated", "translation_id", "views"]
    SELECT_COLUMN_CONSTRAINT = ["id", "uuid", "debug", "is_valid", "is_indexed", "duplicate_id", "url", "topic_id",
                                "category_id", "source_id", "image_id", "title", "snippet", "content", "author",
                                "datetime_created", "datetime_updated", "translation_id", "views"]


    def __init__(self, user:str=None, password:str=None, host=None, database=None):
        # type: (Optional[str], Optional[str], Optional[str], Optional[str]) -> None
        super(NewsDB, self).__init__("news", user=user, password=password, host=host, database=database)

    def get_news_by_id(self, id, column=None, record_as_dict=False):
        # type: (int, Optional[List], Optional[bool]) -> Any
        if not column:
            column = self.SELECT_COLUMN_CONSTRAINT
        conditions = ["id = %d" % id]
        return self.fetch_record(column=column, condition=conditions, record_as_dict=record_as_dict)

    def get_news_by_uuid(self, uuid, column=None, record_as_dict=False):
        # type: (str, Optional[List], Optional[bool]) -> Any
        if not column:
            column = self.SELECT_COLUMN_CONSTRAINT
        conditions = ["uuid = '%s'" % uuid]
        return self.fetch_record(column=column, condition=conditions, record_as_dict=record_as_dict)

    def get_latest_news(self, column=None, condition=None, max_count=0, record_as_dict=False):
        # type: (Optional[List], Optional[List], Optional[int], Optional[bool]) -> List
        if not column:
            column = self.SELECT_COLUMN_CONSTRAINT
        conditions = ["datetime_created > '%s'" % (datetime.strftime(datetime.now() - timedelta(days=14), "%Y-%m-%d %H:%M:%S"))]
        if condition:
            conditions.extend(condition)
        return self.fetch_records(column=column, condition=conditions, limit=max_count, record_as_dict=record_as_dict)

    def get_latest_news_by_source_id(self, source_id, column=None, max_count=0, record_as_dict=False):
        # type: (int, Optional[List], Optional[int], Optional[bool]) -> List
        if not column:
            column = self.SELECT_COLUMN_CONSTRAINT
        condition = ["source_id = %d" % source_id]
        return self.get_latest_news(column=column, condition=condition, max_count=max_count,
                                    record_as_dict=record_as_dict)

    def get_non_indexed_news(self, column=None, condition=None, max_count=0, record_as_dict=True):
        # type: (Optional[List], Optional[List], Optional[int], Optional[bool]) -> List
        if not column:
            column = self.SELECT_COLUMN_CONSTRAINT
        conditions = ["NOT is_indexed", "is_valid", "NOT debug"]
        if condition:
            conditions.extend(condition)
        order_by = "datetime_created DESC"
        return self.fetch_records(column=column, condition=conditions, order_by=order_by,
                                  limit=max_count, record_as_dict=record_as_dict)

    def get_non_indexed_news_by_source_id(self, source_id, column=None, max_count=0, record_as_dict=True):
        # type: (int, Optional[List], Optional[int], Optional[bool]) -> List
        if not column:
            column = self.SELECT_COLUMN_CONSTRAINT
        condition = ["source_id = %d" % source_id]
        return self.get_non_indexed_news(column=column, condition=condition,
                                         max_count=max_count, record_as_dict=record_as_dict)

    def get_news_by_topic_uuid(self, topic_uuid, column=None, max_count=0, record_as_dict=True):
        # type: (str, Optional[List], Optional[int], Optional[bool]) -> List
        if not column:
            column = self.SELECT_COLUMN_CONSTRAINT
        adv_query = "INNER JOIN topic ON topic.id = news.topic_id where topic.uuid='%s'" % topic_uuid
        return self.fetch_advanced_records(column=column, advanced=adv_query,
                                           max_count=max_count, record_as_dict=record_as_dict)

    def get_news_by_topic_id(self, topic_id, column=None, max_count=0, record_as_dict=True):
        # type: (int, Optional[List], Optional[int], Optional[bool]) -> List
        if not column:
            column = self.SELECT_COLUMN_CONSTRAINT
        conditions = ["topic_id = %d" % topic_id]
        return self.fetch_records(column=column, condition=conditions,
                                  max_count=max_count, record_as_dict=record_as_dict)

    def add_news_use_record(self, record, ignore_extra_keys=True):
        # type: (Dict, Optional[bool]) -> int
        uid = self.generate_uuid()
        record["uuid"] = uid
        if self.insert_record(record=record, ignore_extra_keys=ignore_extra_keys):
            return self._db._cursor.lastrowid
        return 0

    def update_news_by_id(self, id, record, ignore_extra_keys=True):
        # type: (int, Dict) -> bool
        return self.update_record(record=record, condition=["id = %d" % id], ignore_extra_keys=ignore_extra_keys)

    def update_news_by_uuid(self, uuid, record, ignore_extra_keys=True):
        # type: (str, Dict) -> bool
        return self.update_record(record=record, condition=["uuid = '%s'" % uuid], ignore_extra_keys=ignore_extra_keys)


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
        self.data.add_news_use_record(record=dict(source_id=1, uuid="1", url="http://www.reuters.com/news1", title="News title1",
                                      datetime_created=datetime.now() - timedelta(days=28)))
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
        self.assertEqual(len(results), 1)

    def test_add_news(self):
        record = dict(source_id=1, uuid="5", title="H1", url="http://www.reuters.com/h1news")
        result = self.data.add_news_use_record(record)
        self.assertGreater(result, 0)
        record = dict(source_id=1, uuid="6", title="H1", url="http://www.reuters.com/h1news",
                      datetime_created=datetime.now() - timedelta(days=28))
        result = self.data.add_news_use_record(record)
        self.assertGreater(result, 0)

    def test_update_news_by_id(self):
        columns = ["id", "uuid", "title"]
        record = dict(title="Title123")
        id = self.data.fetch_record(column=["id"], condition=["source_id=2"])[0]
        self.data.update_news_by_id(id, record)
        title = self.data.fetch_record(column=["title"], condition=["id=%d" % id])[0]
        self.assertEqual(title, "Title123")


if __name__ == "__main__":
    unittest.main()
