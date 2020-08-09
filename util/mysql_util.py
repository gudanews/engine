import mysql.connector
import logging
import unittest
import time
from util.common import MetaClassSingleton


logger = logging.getLogger("Util.MySQLDB")


class MySQLDB(metaclass=MetaClassSingleton):

    __metaclass__ = MetaClassSingleton

    def __init__(self, user, password, host, database):
        self._connection = mysql.connector.connect(user=user, password=password, host=host, database=database)
        self._cursor = None

    def _commit(self, sql, val=None):
        if not self._connection.is_connected():
            raise mysql.connector.DatabaseError("Cannot connect to DB")
        self._cursor = self._connection.cursor()
        if val:
            self._cursor.execute(sql, val)
        else:
            self._cursor.execute(sql)
        self._connection.commit()
        time.sleep(0.1)
        logger.debug("Commit SQL:\t%s" % sql)
        logger.debug("Commit Result: [%d] record affected." % self._cursor.rowcount)

    def _fetch(self, sql, size=0): # size = 0 stands for fetchall
        if not self._connection.is_connected():
            raise mysql.connector.DatabaseError("Cannot connect to DB")
        self._cursor = self._connection.cursor()
        self._cursor.execute(sql)
        result = self._cursor.fetchall() if size == 0 else self._cursor.fetchmany(size) if size > 1 else self._cursor.fetchone()
        # If there is still results left after using fetchone() or fetchmany() method,
        # the connection can be disconnected unless fetchall() the rest
        if self._cursor._nextrow[0] is not None:
            _ = self._cursor.fetchall()
        logger.debug("Fetch SQL:\t%s" % sql)
        logger.debug("Fetch Result [%d]:\n%s" % (self._cursor.rowcount, str(result)))
        return result

    def get_table_schema(self, table):
        sql = "DESC %s " % table
        logger.debug("Fetch table schema using SQL query:\t%s" % sql)
        return self._fetch(sql, size=1)

    def _build_sql_select_statement(self, table, column=None, condition=None, group_by=None, order_by=None, limit=None):
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
        if group_by:
            sql += " GROUP BY %s" % group_by
        if order_by:
            sql += " ORDER BY %s" % order_by
        if limit:
            sql += " limit %s" % limit
        return sql

    def _build_advanced_sql_select_statement(self, table, column=None, advanced=None):
        col = "*"
        if column:
            if isinstance(column, str):
                col = column
            elif isinstance(column, list):
                col = ",".join(column)
        sql = "SELECT %s FROM %s " % (col, table)
        if advanced:
            sql += advanced
        return sql

    def fetch_table_record(self, table, column=None, condition=None, group_by=None, order_by=None):
        sql = self._build_sql_select_statement(table=table, column=column, condition=condition,
                                               group_by=group_by, order_by=order_by)
        logger.debug("Fetch single table record using SQL query:\t%s" % sql)
        return self._fetch(sql, size=1)

    def fetch_table_records(self, table, column=None, condition=None, group_by=None, order_by=None, limit=None):
        sql = self._build_sql_select_statement(table=table, column=column, condition=condition,
                                               group_by=group_by, order_by=order_by, limit=limit)
        logger.debug("Fetch all table records using SQL query:\t%s" % sql)
        return self._fetch(sql)

    def fetch_advanced_table_record(self, table, column=None, advanced=None):
        sql = self._build_advanced_sql_select_statement(table=table, column=column, advanced=advanced)
        logger.debug("Fetch single table record using SQL query:\t%s" % sql)
        return self._fetch(sql, size=1)

    def fetch_advanced_table_records(self, table, column=None, advanced=None):
        sql = self._build_advanced_sql_select_statement(table=table, column=column, advanced=advanced)
        logger.debug("Fetch all table records using SQL query:\t%s" % sql)
        return self._fetch(sql)

    def insert_table_record(self, table, record):
        col = []
        val = []
        for (k,v) in record.items():
            col.append(k)
            val.append(v)
        sql = "INSERT INTO %s (%s) VALUES (%s)" % (table, ",".join(col), ",".join(["%s"] * len(record)))
        logger.debug("Insert into table using SQL query:\t%s" % sql)
        self._commit(sql, val=tuple(val))

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
        logger.debug("Update table using SQL query:\t%s" % sql)
        self._commit(sql, val=tuple(val))

    def delete_table_record(self, table, condition=None):
        col = []
        val = []
        sql = "DELETE FROM %s" % table
        if condition:
            sql += " WHERE "
            if isinstance(condition, str):
                sql += condition
            elif isinstance(condition, list):
                sql += " AND ".join(condition)
        logger.debug("Update table using SQL query:\t%s" % sql)
        self._commit(sql)

    def __exit__(self):
        self._connection.close()

    def __del__(self):
        try:
            self._connection.shutdown()
        except:
            pass


from util.common import LoggedTestCase
from util.config_util import Configure

config = Configure()

SANDBOX_USER = config.sandbox["db_user"]
SANDBOX_PASSWORD = config.sandbox["db_password"]
SANDBOX_HOST = config.sandbox["db_host"]
SANDBOX_DATABASE = config.sandbox["db_schema"]


class TestMySQLDB(LoggedTestCase):

    def setUp(self):
        self.db=MySQLDB(user=SANDBOX_USER,password=SANDBOX_PASSWORD,host=SANDBOX_HOST,database=SANDBOX_DATABASE)

    def test_get_table_records(self):
        results = self.db.fetch_table_records(table='headline', column=["id", "is_processed", "duplicate_id"])
        self.assertIsNotNone(results)
        self.assertEqual(len(results[0]), 3)
        logger.info(results)

    def test_get_table_record(self):
        result = self.db.fetch_table_record(table='headline', column=["id", "is_processed", "duplicate_id"])
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        logger.info(result)

    def test_get_table_non_exists_record(self):
        result = self.db.fetch_table_record(table='headline', column=["id", "is_processed", "duplicate_id"],
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