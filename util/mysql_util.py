import mysql.connector
import logging
import unittest
from util.common import LoggedTestCase
from util.config_util import Configure

logger = logging.getLogger("Util.MySQL")

class MySQLDB:
    def __init__(self, user, password, host, database):
        self._connection = mysql.connector.connect(user=user, password=password, host=host, database=database)
        self._cursor = None

    def _commit(self, sql, val=None, msg=None):
        if not self._connection.is_connected():
            raise mysql.connector.DatabaseError("Cannot connect to DB")
        self._cursor = self._connection.cursor()
        self._cursor.execute(sql, val)
        self._connection.commit()
        if msg:
            logger.debug(msg)
        logger.debug("Commit Result: [%d] record affected." % self._cursor.rowcount)

    def _fetch(self, sql, size=0, msg=None): # size = 0 stands for fetchall
        if not self._connection.is_connected():
            raise mysql.connector.DatabaseError("Cannot connect to DB")
        self._cursor = self._connection.cursor()
        self._cursor.execute(sql)
        result = self._cursor.fetchall() if size == 0 else self._cursor.fetchmany(size) if size > 1 else self._cursor.fetchone()
        if msg:
            logger.debug(msg)
        logger.debug("Fetch Result:\n" + str(result))
        return result

    def get_table_schema(self, table):
        sql = "DESC %s " % table
        return self._fetch(sql, size=1, msg=sql)

    def _build_sql_select_statement(self, table, column=None, condition=None, order_by=None):
        col = "*"
        if column:
            if isinstance(column, str):
                col = column
            elif isinstance(column, list):
                col = ",".join(column)
        sql = "SELECT %s FROM %s" % (col, table)
        if condition:
            sql += " WHERE "
            if isinstance(condition, str):
                sql += condition
            elif isinstance(condition, list):
                sql += " AND ".join(condition)
        if order_by:
            sql += " ORDER BY %s" % order_by
        return sql

    def fetch_table_record(self, table, column=None, condition=None, order_by=None):
        sql = self._build_sql_select_statement(table=table, column=column, condition=condition, order_by=order_by)
        logger.debug("Fetch table record using SQL query:\n%s" % sql)
        return self._fetch(sql, size=1, msg=sql)

    def fetch_table_records(self, table, column=None, condition=None, order_by=None):
        sql = self._build_sql_select_statement(table=table, column=column, condition=condition, order_by=order_by)
        logger.debug("Fetch table records using query:\n%s" % sql)
        return self._fetch(sql, msg=sql)

    def insert_table_record(self, table, record):
        col = []
        val = []
        for (k,v) in record.items():
            col.append(k)
            val.append(v)
        sql = "INSERT INTO %s (%s) VALUES (%s)" % (table, ",".join(col), ",".join(["%s"] * len(record)))
        logger.debug("Insert into table using SQL query:\n%s" % sql)
        self._commit(sql, val=tuple(val), msg=sql)

    def update_table_record(self, table, record, condition=None):
        col = []
        val = []
        for (k,v) in record.items():
            col.append("%s = %s" % (k, "%s"))
            val.append(v)
        sql = "UPDATE %s SET %s" % (table, ",".join(col))
        if condition:
            sql += " WHERE "
            if isinstance(condition, str):
                sql += condition
            elif isinstance(condition, list):
                sql += " AND ".join(condition)
        logger.debug("Update table using SQL query:\n%s" % sql)
        self._commit(sql, val=tuple(val), msg=sql)

    def __exit__(self):
        self._connection.close()

    def __del__(self):
        try:
            self._connection.shutdown()
        except:
            pass


config = Configure()

DEFAULT_USER = config.setting["db_user"]
DEFAULT_PASSWORD = config.setting["db_password"]
DEFAULT_HOST = config.setting["db_host"]
DEFAULT_DATABASE = config.setting["db_schema"]


class TestMySQLDB(LoggedTestCase):

    def setUp(self):
        self.db=MySQLDB(user=DEFAULT_USER,password=DEFAULT_PASSWORD,host=DEFAULT_HOST,database=DEFAULT_DATABASE)

    def test_get_table_records(self):
        results = self.db.fetch_table_records(table='headline', column=["id", "is_processed", "is_duplicated"])
        self.assertIsNotNone(results)
        self.assertEqual(len(results[0]), 3)
        logger.info(results)

    def test_get_table_record(self):
        result = self.db.fetch_table_record(table='headline', column=["id", "is_processed", "is_duplicated"])
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        logger.info(result)

    def test_get_table_non_exists_record(self):
        result = self.db.fetch_table_record(table='headline', column=["id", "is_processed", "is_duplicated"],
                                            condition=["id < 0"])
        self.assertIsNone(result)
        logger.info(result)

    def test_get_table_schema(self):
        result = self.db.get_table_schema(table='headline')
        self.assertIsNotNone(result)
        logger.info(result)

    def test_get_table_schema_not_exist(self):
        self.assertRaises(Exception, self.db.get_table_schema, 'does_not_exist')


if __name__ == '__main__':
    unittest.main()