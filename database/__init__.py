from util.mysql_util import MySQLDB
import logging
import unittest
from util.config_util import Configure
import uuid


logger = logging.getLogger("Database")
config = Configure()

DEFAULT_USER = config.setting["db_user"]
DEFAULT_PASSWORD = config.setting["db_password"]
DEFAULT_HOST = config.setting["db_host"]
DEFAULT_DATABASE = config.setting["db_schema"]

MANDATORY = 0
OPTIONAL = 1


class DataBase:

    SELECT_COLUMN_CONSTRAINT = []
    INSERT_COLUMN_CONSTRAINT = {}
    UPDATE_COLUMN_CONSTRAINT = {}
    SPECIAL_MYSQL_KEYWORDS = ["COUNT", "DISTINCT", "LENGTH"]

    def __init__(self, table, user=None, password=None, host=None, database=None):
        user = user or DEFAULT_USER
        password = password or DEFAULT_PASSWORD
        host = host or DEFAULT_HOST
        database = database or DEFAULT_DATABASE
        self._db = MySQLDB(user=user,password=password,host=host,database=database)
        self.table = table
        self._table_schema = None

    @property
    def table_schema(self):
        if not self._table_schema:
            self._table_schema= self._db.get_table_schema(self.table)
        return self._table_schema

    def generate_uuid(self):
        uid = uuid.uuid4()
        return str(uid)

    def validate_insert_record(self, record):
        if not self.INSERT_COLUMN_CONSTRAINT:
            raise Exception("Please define INSERT_COLUMN_CONSTRAINT before proceed")
        extra_keys = set(record.keys()) - set(self.INSERT_COLUMN_CONSTRAINT.keys())
        if extra_keys:
            logger.warning("Unexpected columns %s insert to database <%s>" % (list(extra_keys), self.table))
            return False
        for k, v in self.INSERT_COLUMN_CONSTRAINT.items():
            if not k in record and v[1] == MANDATORY:
                logger.warning("Missing mandatory column [%s] insert to database <%s>" % (k, self.table))
                return False
            elif k in record and not isinstance(record[k], v[0]):
                logger.warning("Invalid column [%s = %s] insert to database <%s>" % (k, record[k], self.table))
                return False
        return True

    def validate_update_record(self, record):
        if not self.UPDATE_COLUMN_CONSTRAINT:
            raise Exception("Please define UPDATE_COLUMN_CONSTRAINT before proceed")
        extra_keys = set(record.keys()) - set(self.UPDATE_COLUMN_CONSTRAINT.keys())
        if extra_keys:
            logger.warning("Unexpected columns %s update database <%s>" % (list(extra_keys), self.table))
            return False
        for k, v in self.UPDATE_COLUMN_CONSTRAINT.items():
            if k in record and not isinstance(record[k], v):
                logger.warning("Invalid column [%s = %s] update database <%s>" % (k, record[k], self.table))
                return False
        return True

    def validate_select_record(self, column):
        if not self.SELECT_COLUMN_CONSTRAINT:
            raise Exception("Please define SELECT_COLUMN_CONSTRAINT before proceed")
        if isinstance(column, str):
            column = [column]
        extra_keys = set(column) - set(self.SELECT_COLUMN_CONSTRAINT)
        for key in extra_keys:
            if not any([k in key for k in self.SPECIAL_MYSQL_KEYWORDS]):
                logger.warning("Unexpected column %s select database <%s>" % (list(extra_keys), self.table))
                return False
        return True

    def count_records(self, condition=None):
        column = "COUNT(*)"
        count = self.fetch_record(column=column,condition=condition)
        return count[0]

    def insert_record(self, record):
        if self.validate_insert_record(record):
            self._db.insert_table_record(self.table, record)
            return True
        return False

    def update_record(self, record, condition=None):
        if self.validate_update_record(record):
            self._db.update_table_record(self.table, record, condition)
            return True
        return False

    def fetch_records(self, column=None, condition=None, group_by=None, order_by=None, limit=None):
        if not column or self.validate_select_record(column):
            return self._db.fetch_table_records(table=self.table, column=column, condition=condition,
                                                group_by=group_by, order_by=order_by, limit=limit)
        return None

    def fetch_advanced_records(self, column=None, advanced=None):
        if not column or self.validate_select_record(column):
            return self._db.fetch_advanced_table_records(table=self.table, column=column, advanced=advanced)
        return None

    def fetch_record(self, column=None, condition=None, group_by=None, order_by=None):
        if not column or self.validate_select_record(column):
            return self._db.fetch_table_record(table=self.table, column=column, condition=condition,
                                               group_by=group_by, order_by=order_by)
        return None

    def fetch_advanced_record(self, column=None, advanced=None):
        if not column or self.validate_select_record(column):
            return self._db.fetch_advanced_table_record(table=self.table, column=column, advanced=advanced)
        return None

    def delete_records(self, condition=None):
        return self._db.delete_table_record(self.table, condition)


from util.common import LoggedTestCase
from datetime import datetime
import time

SANDBOX_USER = config.sandbox["db_user"]
SANDBOX_PASSWORD = config.sandbox["db_password"]
SANDBOX_HOST = config.sandbox["db_host"]
SANDBOX_DATABASE = config.sandbox["db_schema"]

class TestBaseData(LoggedTestCase):

    def setUp(self):
        self.data = DataBase("headline",user=SANDBOX_USER,password=SANDBOX_PASSWORD,host=SANDBOX_HOST,database=SANDBOX_DATABASE)
        self.data.SELECT_COLUMN_CONSTRAINT = ["id", "is_processed", "is_displayable", "duplicate_id", "source_id",
                                    "image_id", "news_id", "heading", "url", "datetime", "snippet"]

        self.data.INSERT_COLUMN_CONSTRAINT = {
            "id": (str, MANDATORY),
            "source_id": (int, MANDATORY),
            "image_id": (int, OPTIONAL),
            "news_id": (str, OPTIONAL),
            "heading": (str, MANDATORY),
            "url": (str, MANDATORY),
            "datetime": (datetime, OPTIONAL),
            "snippet": (str, OPTIONAL)}

        self.data.UPDATE_COLUMN_CONSTRAINT = {
            "id": str,
            "source_id": int,
            "image_id": int,
            "news_id": str,
            "heading": str,
            "url": str,
            "datetime": datetime,
            "snippet": str}

        self.data.delete_records()
        self.data.insert_record(record=dict(id="120", source_id=1, url="http://www.reuters.com/news1", heading="News heading1"))
        self.data.insert_record(record=dict(id="121", source_id=2, url="http://www.ap.com/news2", heading="News heading2"))
        self.data.insert_record(record=dict(id="122", source_id=1, url="http://www.cnn.com/news3", heading="News heading3"))
        self.data.insert_record(record=dict(id="123", source_id=3, url="http://www.foxnews.com/news4", heading="News heading4"))
        time.sleep(1.0)


    def test_retrieve_record(self):
        # Test single record
        columns = ["id", "heading", "datetime", "source_id"]
        result = self.data.fetch_record(column=columns)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 4)
        # Test multiple record
        results = self.data.fetch_records(column=columns)
        self.assertGreater(len(results), 1)
        self.assertEqual(len(results[0]), 4)
        # Test retrieval partial record
        conditions = ["source_id = 1"]
        results_1 = self.data.fetch_records(column=columns)
        results_2 = self.data.fetch_records(column=columns, condition=conditions)
        self.assertGreater(len(results_1), len(results_2))
        # Test retrieval non exist record
        results = self.data.fetch_records(column=columns, condition="source_id = 999")
        self.assertEqual(len(results), 0)
        # Test retrieve with non-existing column
        columns = ["id", "headings", "datetime", "source_id"]
        results = self.data.fetch_records(column=columns)
        self.assertIsNone(results)
        # Test retrieve with extra column
        columns = ["id", "heading", "datetime", "source_id", "extra"]
        results = self.data.fetch_records(column=columns)
        self.assertIsNone(results)

    def test_count_records(self):
        results = self.data.count_records()
        self.assertEqual(results, 4)
        results = self.data.count_records(condition="source_id = 1")
        self.assertEqual(results, 2)
        results = self.data.count_records(condition="source_id = 999")
        self.assertEqual(results, 0)

    def test_insert_record(self):
        columns = ["id", "heading", "datetime", "source_id"]
        # with mandatory column
        record = dict(id="124", source_id=1, url="http://www.foxnews.com/news5", heading="News heading5")
        self.assertTrue(self.data.insert_record(record=record))
        result = self.data.fetch_record(column=columns, condition="id = 124")
        self.assertEqual(result[0], 124)
        # missing mandatory column
        record = dict(id="125", url="http://www.foxnews.com/news5", heading="News heading5")
        self.assertFalse(self.data.insert_record(record=record))
        result = self.data.fetch_record(column=columns, condition="id = 125")
        self.assertIsNone(result)
        # extra column
        record = dict(id="126", source_id=1, url="http://www.foxnews.com/news5", heading="News heading5", extra="Extra")
        self.assertFalse(self.data.insert_record(record=record))
        results = self.data.fetch_records(column=columns, condition="id = 126")
        self.assertEqual(len(results), 0)


    def test_update_record(self):
        columns = ["id", "heading", "datetime", "source_id"]
        conditions = ["id = 121"]
        record = dict(source_id=5, url="http://www.foxnews.com/news5", heading="News heading5")
        self.assertTrue(self.data.update_record(record=record, condition="id = 121"))
        result = self.data.fetch_record(column=columns, condition=conditions)
        self.assertEqual(result[3], 5)
        # extra column
        record = dict(source_id=6, url="http://www.foxnews.com/news5", heading="News heading5", extra="Extra")
        results = self.data.update_record(record=record, condition=conditions)
        self.assertFalse(results)
        self.assertNotEqual(result[3], 6)


if __name__ == '__main__':
    unittest.main()