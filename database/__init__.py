from util.mysql_util import MySQLDB
import logging
import unittest
from util.config_util import Configure
import uuid
from typing import List, Dict, Tuple, Optional, Any


logger = logging.getLogger("Database")
config = Configure()

DEFAULT_USER = config.setting["db_user"]
DEFAULT_PASSWORD = config.setting["db_password"]
DEFAULT_HOST = config.setting["db_host"]
DEFAULT_DATABASE = config.setting["db_schema"]

MANDATORY = 0
OPTIONAL = 1


class DataBase:

    COLUMN_CONSTRAINT = {}
    INSERT_COLUMN_CONSTRAINT = {}
    UPDATE_COLUMN_CONSTRAINT = []
    SELECT_COLUMN_CONSTRAINT = []
    SPECIAL_MYSQL_KEYWORDS = ["COUNT", "DISTINCT", "LENGTH"]

    def __init__(self, table, user=None, password=None, host=None, database=None):
        # type: (str, Optional[str], Optional[str], Optional[str], Optional[str]) -> None
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
        # type: () -> str
        uid = uuid.uuid4()
        return str(uid)

    def validate_insert_record(self, record, ignore_extra_keys=False):
        # type: (Dict, Optional[bool]) -> bool
        if not self.INSERT_COLUMN_CONSTRAINT:
            raise Exception("Please define INSERT_COLUMN_CONSTRAINT before proceed")
        extra_keys = set(record.keys()) - set(self.INSERT_COLUMN_CONSTRAINT)
        if extra_keys:
            if not ignore_extra_keys:
                logger.warning("Unexpected columns %s insert to database <%s>" % (list(extra_keys), self.table))
                return False
            else:
                for k in extra_keys:
                    record.pop(k, None)
        for k in self.INSERT_COLUMN_CONSTRAINT:
            if not (k in record and record[k]) and self.COLUMN_CONSTRAINT[k][0] == MANDATORY:
                logger.warning("Missing mandatory column [%s] when insert to database <%s>" % (k, self.table))
                return False
            elif k in record and record[k]:
                if not isinstance(record[k], self.COLUMN_CONSTRAINT[k][1]):
                    logger.warning("Invalid column type [%s = %s] when insert to database <%s>" % (k, record[k], self.table))
                    return False
                elif len(self.COLUMN_CONSTRAINT[k]) > 2:
                    if isinstance(record[k], str) and len(record[k]) > self.COLUMN_CONSTRAINT[k][2]:
                        record[k] = record[k][:self.COLUMN_CONSTRAINT[k][2]]
                    elif isinstance(record[k], int) and record[k] >= 2 ** self.COLUMN_CONSTRAINT[k][2]:
                        logger.warning("Out of bound column value [%d = %d] when insert to database <%s>" % (k, record[k], self.table))
                        return False
        return True

    def validate_update_record(self, record, ignore_extra_keys=False):
        # type: (Dict, Optional[bool]) -> bool
        if not self.UPDATE_COLUMN_CONSTRAINT:
            raise Exception("Please define UPDATE_COLUMN_CONSTRAINT before proceed")
        extra_keys = set(record.keys()) - set(self.UPDATE_COLUMN_CONSTRAINT)
        if extra_keys:
            if not ignore_extra_keys:
                logger.warning("Unexpected columns %s update database <%s>" % (list(extra_keys), self.table))
                return False
            else:
                for k in extra_keys:
                    record.pop(k, None)
        for k in self.UPDATE_COLUMN_CONSTRAINT:
            if k in record:
                if not record[k] and self.COLUMN_CONSTRAINT[k][0] == MANDATORY:
                    logger.warning("Try to remove manadatory field [%s] when update database <%s>" % (k, self.table))
                    return False
                elif record[k]:
                    if not isinstance(record[k], self.COLUMN_CONSTRAINT[k][1]):
                        logger.warning("Invalid column type [%s = %s] when update database <%s>" % (k, record[k], self.table))
                        return False
                    elif len(self.COLUMN_CONSTRAINT[k]) > 2:
                        if isinstance(record[k], str) and len(record[k]) > self.COLUMN_CONSTRAINT[k][2]:
                            record[k] = record[k][:self.COLUMN_CONSTRAINT[k][2]]
                        elif isinstance(record[k], int) and record[k] >= 2 ** self.COLUMN_CONSTRAINT[k][2]:
                            logger.warning("Out of bound column value [%d = %d] when update to database <%s>" % (k, record[k], self.table))
                            return False
        return True

    def validate_select_record(self, column):
        # type: (List) -> bool
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
        # type: (Optional[List]) -> int
        column = ["COUNT(*)"]
        count = self.fetch_record(column=column,condition=condition)
        return count[0]

    def insert_record(self, record, ignore_extra_keys=False):
        # type: (Dict, Optional[bool]) -> bool
        if self.validate_insert_record(record, ignore_extra_keys=ignore_extra_keys):
            self._db.insert_table_record(self.table, record)
            return True
        return False

    def update_record(self, record, condition=None, ignore_extra_keys=False):
        # type: (Dict, Optional[List], Optional[bool]) -> bool
        if self.validate_update_record(record, ignore_extra_keys=ignore_extra_keys):
            self._db.update_table_record(self.table, record, condition)
            return True
        return False

    def fetch_records(self, column=None, condition=None, group_by=None, order_by=None,
                      limit=None, record_as_dict=False):
        # type: (Optional[List], Optional[List], Optional[str], Optional[str], Optional[int], Optional[bool]) -> List
        if not column or self.validate_select_record(column):
            return self._db.fetch_table_records(table=self.table, column=column, condition=condition, group_by=group_by,
                                                order_by=order_by, limit=limit, record_as_dict=record_as_dict)
        return None

    def fetch_advanced_records(self, column=None, advanced=None, record_as_dict=False):
        # type: (Optional[List], Optional[List], Optional[str], Optional[str], Optional[int], Optional[bool]) -> List
        if not column or self.validate_select_record(column):
            return self._db.fetch_advanced_table_records(table=self.table, column=column, advanced=advanced,
                                                         record_as_dict=record_as_dict)
        return None

    def fetch_record(self, column=None, condition=None, group_by=None, order_by=None,
                     record_as_dict=False):
        # type: (Optional[List], Optional[List], Optional[str], Optional[str], Optional[int], Optional[bool]) -> List
        if not column or self.validate_select_record(column):
            return self._db.fetch_table_record(table=self.table, column=column, condition=condition,
                                               group_by=group_by, order_by=order_by, record_as_dict=record_as_dict)
        return None

    def fetch_advanced_record(self, column=None, advanced=None, record_as_dict=False):
        # type: (Optional[List], Optional[List], Optional[str], Optional[str], Optional[int], Optional[bool]) -> List
        if not column or self.validate_select_record(column):
            return self._db.fetch_advanced_table_record(table=self.table, column=column, advanced=advanced,
                                                        record_as_dict=record_as_dict)
        return None

    def delete_records(self, condition=None):
        # type: (Optional[List]) -> bool
        try:
            self._db.delete_table_record(self.table, condition)
            return True
        except:
            return False


from util.common import LoggedTestCase
from datetime import datetime
import time

SANDBOX_USER = config.sandbox["db_user"]
SANDBOX_PASSWORD = config.sandbox["db_password"]
SANDBOX_HOST = config.sandbox["db_host"]
SANDBOX_DATABASE = config.sandbox["db_schema"]

class TestBaseData(LoggedTestCase):

    def setUp(self):
        self.data = DataBase("topic",user=SANDBOX_USER,password=SANDBOX_PASSWORD,host=SANDBOX_HOST,database=SANDBOX_DATABASE)

        self.data.COLUMN_CONSTRAINT = {
            "id": (MANDATORY, int,),
            "uuid": (MANDATORY, str, 36),
            "is_valid": (OPTIONAL, int),
            "is_processed": (OPTIONAL, int),
            "is_displayable": (OPTIONAL, int),
            "category_id": (OPTIONAL, int),
            "news_id": (MANDATORY, int),
            "datetime_created": (OPTIONAL, datetime),
            "datetime_updated": (OPTIONAL, datetime),
            "quality": (OPTIONAL, int)
        }
        self.data.INSERT_COLUMN_CONSTRAINT = ["id", "uuid", "is_valid", "is_processed", "is_displayable", "category_id",
                                              "news_id", "datetime_created", "datetime_updated", "quality"]
        self.data.UPDATE_COLUMN_CONSTRAINT = ["id", "uuid", "is_valid", "is_processed", "is_displayable", "category_id",
                                              "news_id", "datetime_created", "datetime_updated", "quality"]
        self.data.SELECT_COLUMN_CONSTRAINT = ["id", "uuid", "is_valid", "is_processed", "is_displayable", "category_id",
                                              "news_id", "datetime_created", "datetime_updated", "quality"]


        self.data.delete_records()
        self.data.insert_record(record=dict(id=120, uuid="120", news_id=1))
        self.data.insert_record(record=dict(id=121, uuid="121", news_id=2))
        self.data.insert_record(record=dict(id=122, uuid="122", news_id=1))
        self.data.insert_record(record=dict(id=123, uuid="123", news_id=3))
        time.sleep(1.0)


    def test_retrieve_record(self):
        # Test single record
        columns = ["id", "news_id", "datetime_created", "category_id"]
        result = self.data.fetch_record(column=columns)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 4)
        # Test multiple record
        results = self.data.fetch_records(column=columns)
        self.assertGreater(len(results), 1)
        self.assertEqual(len(results[0]), 4)
        # Test retrieval partial record
        conditions = ["news_id = 1"]
        results_1 = self.data.fetch_records(column=columns)
        results_2 = self.data.fetch_records(column=columns, condition=conditions)
        self.assertGreater(len(results_1), len(results_2))
        # Test retrieval non exist record
        results = self.data.fetch_records(column=columns, condition=["news_id = 999"])
        self.assertEqual(len(results), 0)
        # Test retrieve with non-existing column
        columns = ["id", "uuids", "datetime_created", "news_id"]
        results = self.data.fetch_records(column=columns)
        self.assertIsNone(results)

    def test_count_records(self):
        results = self.data.count_records()
        self.assertEqual(results, 4)
        results = self.data.count_records(condition=["news_id = 1"])
        self.assertEqual(results, 2)
        results = self.data.count_records(condition=["news_id = 999"])
        self.assertEqual(results, 0)

    def test_insert_record(self):
        columns = ["id", "uuid", "datetime_created", "news_id"]
        # with mandatory column
        record = dict(id=124, uuid="124", news_id=1)
        self.assertTrue(self.data.insert_record(record=record))
        result = self.data.fetch_record(column=columns, condition=["id = 124"])
        self.assertEqual(result[0], 124)
        # missing mandatory column
        record = dict(id=125, uuid="125")
        self.assertFalse(self.data.insert_record(record=record))
        result = self.data.fetch_record(column=columns, condition=["id = 125"])
        self.assertIsNone(result)
        # extra column
        record = dict(id=126, uuid="126", news_id=1, extra="Extra")
        self.assertFalse(self.data.insert_record(record=record))
        results = self.data.fetch_records(column=columns, condition=["id = 126"])
        self.assertEqual(len(results), 0)
        # ignore extra column
        record = dict(id=127, uuid="127", news_id=1, extra="Extra")
        self.assertTrue(self.data.insert_record(record=record, ignore_extra_keys=True))
        results = self.data.fetch_records(column=columns, condition=["id = 127"])
        self.assertEqual(len(results), 1)


    def test_update_record(self):
        columns = ["id", "uuid", "datetime_created", "news_id"]
        conditions = ["id = 121"]
        record = dict(news_id=5)
        self.assertTrue(self.data.update_record(record=record, condition=["id = 121"]))
        result = self.data.fetch_record(column=columns, condition=conditions)
        self.assertEqual(result[3], 5)
        # extra column
        record = dict(news_id=6, extra="Extra")
        results = self.data.update_record(record=record, condition=conditions)
        self.assertFalse(results)
        self.assertNotEqual(result[3], 6)


if __name__ == '__main__':
    unittest.main()