import mysql.connector
import logging
import unittest

from datetime import datetime

DEFAULT_USER = "9999cn"
DEFAULT_PASSWORD = "password"
DEFAULT_HOST = "192.168.1.49"
DEFAULT_DATABASE = "news"

class MySQLDB:
    def __init__(self, user=DEFAULT_USER, password=DEFAULT_PASSWORD, host=DEFAULT_HOST, database=DEFAULT_DATABASE):
        self.db_connection = mysql.connector.connect(user=user, password=password, host=host, database=database)

    def _commit(self, sql, val=None, msg=None):
        if not self.db_connection.is_connected():
            raise mysql.connector.DatabaseError("Cannot connect to DB")
        _cursor = self.db_connection.cursor()
        _cursor.execute(sql, val)
        self.db_connection.commit()
        if msg:
            logging.info(msg)
        logging.debug(_cursor.rowcount, "record affected.")

    def _fetchall(self, sql, msg=None):
        if not self.db_connection.is_connected():
            raise mysql.connector.DatabaseError("Cannot connect to DB")
        _cursor = self.db_connection.cursor()
        _cursor.execute(sql)
        _result = _cursor.fetchall()
        if msg:
            logging.info(msg)
        for r in _result:
            logging.debug(r)
        return _result

    def get_table_schema(self, table):
        sql = "DESC %s " % table
        results = self._fetchall(sql, msg=sql)
        if results:
            return [r[0] for r in results]
        return None

    def fetch_table_records(self, table, columns=None, condition=None, order_by=None):
        col = "*"
        if columns:
            if isinstance(columns, str):
                col = columns
            elif isinstance(columns, list):
                col = ",".join(columns)
        sql = "SELECT %s FROM %s" % (col, table)
        if condition:
            sql += " WHERE "
            if isinstance(condition, str):
                sql += condition
            elif isinstance(condition, list):
                sql += " AND ".join(condition)
        if order_by:
            sql += " ORDER BY %s" % order_by
        return self._fetchall(sql, msg=sql)

    def insert_table_record(self, table, record):
        col = []
        val = []
        for (k,v) in record.items():
            col.append(k)
            val.append(v)
        sql = "INSERT INTO %s (%s) VALUES (%s)" % (table, ",".join(col), ",".join(["%s"] * len(record)))
        self._commit(sql, val=tuple(val), msg=sql)

    def update_table_record(self, table, record, condition=None):
        val = []
        for (k,v) in record.items():
            val.append("%s=%s" % (k,v))
        sql = "UPDATE %s SET %s" % (table, ",".join(val))
        if condition:
            sql += " WHERE "
            if isinstance(condition, str):
                sql += condition
            elif isinstance(condition, list):
                sql += " AND ".join(condition)
        self._commit(sql, val=tuple(val), msg=sql)


class MySQLDBTableAction:
    def __init__(self, table=None):
        self.db = MySQLDB(user="9999cn", password= "password", host="192.168.1.49", database= "news")
        self.table = table
        self.record = None
        self._table_schema = None

    @property
    def table_schema(self):
        if not self._table_schema:
            self._table_schema= self.db.get_table_schema(self.table)
        return self._table_schema

    def create_record(self, **kwargs):
        self.record = dict()
        for k in kwargs:
            self.record[k] = kwargs[k]

    def insert_db_record(self):
        self.db.insert_table_record(self.table, self.record)

class NewsHeadlineTableAction(MySQLDBTableAction):

    def __init__(self):
        super(NewsHeadlineTableAction, self).__init__("news_headline")

class NewsDataTableAction(MySQLDBTableAction):

    def __init__(self):
        super(NewsDataTableAction, self).__init__("news_data")


class TestMySQLDB(unittest.TestCase):

    def setUp(self):
        self.db=MySQLDB()

    def test_get_table_records(self):
        result = self.db.fetch_table_records(table='news_headline', columns=["id", "is_processed", "is_duplicated"])
        self.assertIsNotNone(result)
        self.assertEqual(len(result[0]), 3)
        logging.info(result)

    def test_get_table_schema(self):
        result = self.db.get_table_schema(table='news_headline')
        self.assertIsNotNone(result)
        logging.info(result)

    def _test_update_table_record(self):
        self.db.update_table_record(table='news_headline', record={"id": 2}, condition="id=1")

    def _test_insert_table_record(self):
        self.db.insert_table_record(table='news_headline', record={"id": 2})

    def test_news_headline_db_action(self):
        self.db_action = NewsHeadlineTableAction()
        self.assertListEqual(self.db_action.table_schema,
                             "id is_duplicated is_processed is_displayed headline datetime " \
                             "source_id link snippet image".split())
        self.db_action.create_record(headline="aaaa", source_id=1, datetime=datetime(2020, 7, 20, 12, 45, 00))
        self.db_action.insert_db_record()
        logging.info(self.db_action.record)


if __name__ == '__main__':
    unittest.main()