from database import DataBase
from datetime import datetime, timedelta
import unittest
import logging
from database.source import SourceDB
from database import MANDATORY, OPTIONAL
import time


logger = logging.getLogger("Database.Headline")


class HeadlineDB(DataBase):

    SELECT_COLUMN_CONSTRAINT = ["id", "uuid", "is_processed", "is_displayable", "duplicate_id", "source_id",
                      "image_id", "news_id", "heading", "url", "datetime", "snippet"]

    INSERT_COLUMN_CONSTRAINT = {
        "uuid": (str, MANDATORY),
        "is_processed": (int, OPTIONAL),
        "is_displayable": (int, OPTIONAL),
        "duplicate_id": (int, OPTIONAL),
        "source_id": (int, MANDATORY),
        "image_id": (int, OPTIONAL),
        "news_id": (int, OPTIONAL),
        "heading": (str, MANDATORY),
        "url": (str, MANDATORY),
        "datetime": (datetime, OPTIONAL),
        "snippet": (str, OPTIONAL),
        "quality": (int, OPTIONAL)}

    UPDATE_COLUMN_CONSTRAINT = {
        "is_processed": int,
        "is_displayable": int,
        "duplicate_id": int,
        "source_id": int,
        "image_id": int,
        "news_id": int,
        "heading": str,
        "url": str,
        "datetime": datetime,
        "snippet": str,
        "quality": int}

    def __init__(self, user=None, password=None, host=None, database=None):
        super(HeadlineDB, self).__init__("headline", user=user, password=password, host=host, database=database)

    def get_headline_by_id(self, id, column=None):
        if not column:
            column = self.SELECT_COLUMN_CONSTRAINT
        conditions = "id = %d" % id
        return self.fetch_record(column=column, condition=conditions)

    def get_headline_by_uuid(self, uuid, column=None):
        if not column:
            column = self.SELECT_COLUMN_CONSTRAINT
        conditions = "uuid = '%s'" % uuid
        return self.fetch_record(column=column, condition=conditions)

    def get_latest_headlines(self, column=None, condition=None):
        if not column:
            column = self.SELECT_COLUMN_CONSTRAINT
        conditions = ["datetime > '%s'" % (datetime.strftime(datetime.now() - timedelta(hours=96), "%Y-%m-%d %H:%M:%S"))]
        if isinstance(condition, str):
            conditions.append(condition)
        elif isinstance(condition, list):
            conditions.extend(condition)
        return self.fetch_records(column=column, condition=conditions)

    def get_latest_headlines_by_source(self, source, column=None):
        if not source or not (isinstance(source, int) or isinstance(source, str)):
            raise Exception("Please specify <source> to use get_latest_headlines_by_source method")
        source = SourceDB().get_source_id_by_name(source) if isinstance(source, str) else source
        conditions = ["source_id = %d" % source]
        return self.get_latest_headlines(column=column, condition=conditions)

    def add_headline(self, record):
        uid = self.generate_uuid()
        record["uuid"] = uid
        if self.insert_record(record=record):
            return self._db._cursor.lastrowid
        return 0

    def update_headline_by_id(self, id, record):
        return self.update_record(record=record, condition="id = %d" % id)

    def update_headline_by_uuid(self, uuid, record):
        return self.update_record(record=record, condition="uuid = '%s'" % uuid)


from util.config_util import Configure
from util.common import LoggedTestCase

config = Configure()

SANDBOX_USER = config.sandbox["db_user"]
SANDBOX_PASSWORD = config.sandbox["db_password"]
SANDBOX_HOST = config.sandbox["db_host"]
SANDBOX_DATABASE = config.sandbox["db_schema"]


class TestNewHeadlineDB(LoggedTestCase):

    def setUp(self):
        self.data = HeadlineDB(user=SANDBOX_USER, password=SANDBOX_PASSWORD, host=SANDBOX_HOST, database=SANDBOX_DATABASE)
        self.data.delete_records()
        self.data.add_headline(record=dict(source_id=1, url="http://www.reuters.com/news1", heading="News heading1"))
        self.data.add_headline(record=dict(source_id=2, url="http://www.ap.com/news2", heading="News heading2"))
        self.data.add_headline(record=dict(source_id=1, url="http://www.cnn.com/news3", heading="News heading3"))
        self.data.add_headline(record=dict(source_id=3, url="http://www.foxnews.com/news4", heading="News heading4"))
        time.sleep(1.0)

    def test_get_latest_headline(self):
        columns = ["id", "uuid", "datetime", "heading", "source_id"]
        results = self.data.get_latest_headlines(column=columns)
        self.assertEqual(len(results), 4)
        first_news_date = results[0][2]
        start_date = datetime.now() - timedelta(hours=96)
        end_date = datetime.now()
        self.assertTrue(start_date <= first_news_date <= end_date)

    def test_get_latest_headline_by_source(self):
        results = self.data.get_latest_headlines_by_source(source=1)
        self.assertEqual(len(results), 2)
        results = self.data.get_latest_headlines_by_source(source="AP")
        self.assertEqual(len(results), 1)

    def test_add_headline(self):
        record = dict(source_id=1, heading="H1", url="http://www.reuters.com/h1news")
        result = self.data.add_headline(record)
        self.assertGreater(result, 0)
        record = dict(source_id=1, url="http://www.reuters.com/h1news")
        result = self.data.add_headline(record)
        self.assertEqual(result, 0)

    def test_update_headline_by_id(self):
        columns = ["id", "uuid", "heading"]
        record = dict(heading="Heading123")
        id = self.data.fetch_record(column="id", condition="source_id=1")[0]
        self.data.update_headline_by_id(id=id, record=record)
        result = self.data.get_headline_by_id(id=id, column=columns)
        self.assertEqual(result[2], "Heading123")
        record = dict(heading="Heading456")
        uid = self.data.fetch_record(column="uuid", condition="source_id=1")[0]
        self.data.update_headline_by_uuid(uuid=uid, record=record)
        result = self.data.get_headline_by_uuid(uuid=uid, column=columns)
        self.assertEqual(result[2], "Heading456")


if __name__ == "__main__":

    unittest.main()