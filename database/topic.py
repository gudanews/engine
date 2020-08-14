from database import DataBase
from datetime import datetime, timedelta
import unittest
import logging
from database.source import SourceDB
from database import MANDATORY, OPTIONAL
import time


logger = logging.getLogger("Database.Topic")


class TopicDB(DataBase):

    COLUMN_CONSTRAINT = {
        "id": (MANDATORY, int, 32),
        "uuid": (MANDATORY, str, 36),
        "is_valid": (OPTIONAL, int, 1),
        "is_processed": (OPTIONAL, int, 1),
        "is_displayable": (OPTIONAL, int, 1),
        "category_id": (OPTIONAL, int, 16),
        "news_id": (MANDATORY, int, 32),
        "datetime_created": (OPTIONAL, datetime),
        "datetime_updated": (OPTIONAL, datetime),
        "quality": (OPTIONAL, int, 16)
    }
    INSERT_COLUMN_CONSTRAINT = ["uuid", "is_valid", "is_processed", "is_displayable", "category_id", "news_id",
                                "datetime_created", "datetime_updated", "quality"]
    UPDATE_COLUMN_CONSTRAINT = ["id", "uuid", "is_valid", "is_processed", "is_displayable", "category_id", "news_id",
                                "datetime_created", "datetime_updated", "quality"]
    SELECT_COLUMN_CONSTRAINT = ["id", "uuid", "is_valid", "is_processed", "is_displayable", "category_id", "news_id",
                                "datetime_created", "datetime_updated", "quality"]


    def __init__(self, user=None, password=None, host=None, database=None):
        super(TopicDB, self).__init__("topic", user=user, password=password, host=host, database=database)

    def get_topic_by_id(self, id, column=None):
        if not column:
            column = self.SELECT_COLUMN_CONSTRAINT
        conditions = "id = %d" % id
        return self.fetch_record(column=column, condition=conditions)

    def get_topic_by_uuid(self, uuid, column=None):
        if not column:
            column = self.SELECT_COLUMN_CONSTRAINT
        conditions = "uuid = '%s'" % uuid
        return self.fetch_record(column=column, condition=conditions)

    def get_latest_topics(self, column=None, condition=None, max_count=0):
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

    def add_topic(self, record):
        uid = self.generate_uuid()
        record["uuid"] = uid
        if self.insert_record(record=record, ignore_extra_keys=True):
            return self._db._cursor.lastrowid
        return 0

    def update_topic_by_id(self, id, record):
        return self.update_record(record=record, condition="id = %d" % id)

    def update_topic_by_uuid(self, uuid, record):
        return self.update_record(record=record, condition="uuid = '%s'" % uuid)


from util.config_util import Configure
from util.common import LoggedTestCase

config = Configure()

SANDBOX_USER = config.sandbox["db_user"]
SANDBOX_PASSWORD = config.sandbox["db_password"]
SANDBOX_HOST = config.sandbox["db_host"]
SANDBOX_DATABASE = config.sandbox["db_schema"]


class TestTopicDB(LoggedTestCase):

    def setUp(self):
        self.data = TopicDB(user=SANDBOX_USER, password=SANDBOX_PASSWORD, host=SANDBOX_HOST, database=SANDBOX_DATABASE)
        self.data.delete_records()
        self.data.add_topic(record=dict(news_id=1, datetime_created=datetime.now() - timedelta(days=28)))
        self.data.add_topic(record=dict(news_id=2, datetime_created=datetime.now() - timedelta(days=10)))
        self.data.add_topic(record=dict(news_id=3, datetime_created=datetime.now()))
        time.sleep(1.0)

    def test_get_latest_topics(self):
        columns = ["id", "uuid", "datetime_created", "news_id", "source_id"]
        results = self.data.get_latest_headlines(column=columns)
        self.assertEqual(len(results), 2)
        first_news_date = results[0][2]
        start_date = datetime.now() - timedelta(days=14)
        end_date = datetime.now()
        self.assertTrue(start_date <= first_news_date <= end_date)

    def test_add_topic(self):
        record = dict(news_id=1)
        result = self.data.add_topic(record)
        self.assertGreater(result, 0)

    def test_update_topic_by_id(self):
        columns = ["id", "uuid", "news_id"]
        record = dict(news_id=10)
        id = self.data.fetch_record(column="id")[0]
        self.data.update_topic_by_id(id=id, record=record)
        result = self.data.get_topic_by_id(id=id, column=columns)
        self.assertEqual(result[2], 10)
        record = dict(news_id=20)
        uid = self.data.fetch_record(column="uuid")[0]
        self.data.update_topic_by_uuid(uuid=uid, record=record)
        result = self.data.get_topic_by_uuid(uuid=uid, column=columns)
        self.assertEqual(result[2], 20)


if __name__ == "__main__":
    unittest.main()