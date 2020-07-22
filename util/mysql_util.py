import mysql.connector
import logging
import unittest

from datetime import datetime, timedelta

DEFAULT_USER = "gudaman"
DEFAULT_PASSWORD = "GudaN3w2"
DEFAULT_HOST = "192.168.1.49"
DEFAULT_DATABASE = "gudanews"

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

    def fetch_table_records(self, table, column=None, condition=None, order_by=None):
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
    def __init__(self, table):
        self.db = MySQLDB(user="gudaman", password= "GudaN3w2", host="192.168.1.49", database= "gudanews")
        self.table = table
        self._table_schema = None

    @property
    def table_schema(self):
        if not self._table_schema:
            self._table_schema= self.db.get_table_schema(self.table)
        return self._table_schema

    def insert_db_record(self, record):
        self.db.insert_table_record(self.table, record)

    def fetch_db_record(self, column=None, condition=None, order_by=None):
        return self.db.fetch_table_records(self.table, column, condition, order_by)


class NewsHeadlineTableAction(MySQLDBTableAction):

    def __init__(self):
        super(NewsHeadlineTableAction, self).__init__("news_headline")

    def get_latest_news_headline(self, column=None):
        conditions = ["datetime BETWEEN '%(start_time)s' and '%(end_time)s'" %
                      {'start_time': datetime.strftime(datetime.now() - timedelta(hours=36), "%Y-%m-%d %H:%M:%S"),
                       'end_time': datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")}]
        return self.fetch_db_record(column=column, condition=conditions)


class NewsDataTableAction(MySQLDBTableAction):

    def __init__(self):
        super(NewsDataTableAction, self).__init__("news_data")

class ImageTableAction(MySQLDBTableAction):

    def __init__(self):
        super(ImageTableAction, self).__init__("image")

    def get_image_id_by_url(self, url):
        results = self.fetch_db_record(column="id", condition=["url = '%s'" % url])
        return [r[0] for r in results]

class TestMySQLDB(unittest.TestCase):

    def setUp(self):
        self.db=MySQLDB()

    def test_get_table_records(self):
        result = self.db.fetch_table_records(table='news_headline', column=["id", "is_processed", "is_duplicated"])
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

    def _test_news_headline_insertion(self):
        self.db_action = NewsHeadlineTableAction()
        self.assertListEqual(self.db_action.table_schema,
                             "id is_duplicated is_processed is_displayed headline datetime " \
                             "source_id url snippet image_id".split())
        record = dict(headline="News headline added", source_id=1, datetime=datetime.now())
        self.db_action.insert_db_record(record)
        logging.info(record)


    def test_news_headline_retrieve_all_records(self):
        self.db_action = NewsHeadlineTableAction()
        columns = ["id", "headline", "datetime", "source_id"]
        results = self.db_action.fetch_db_record(column=columns)
        self.assertGreater(len(results), 1)
        logging.info(results)

    def test_news_headline_retrieve_conditional_records(self):
        self.db_action = NewsHeadlineTableAction()
        columns = ["id", "headline", "datetime", "source_id"]
        conditions = ["id > 10", "source_id = 1"]
        results_1 = self.db_action.fetch_db_record(column=columns)
        results_2 = self.db_action.fetch_db_record(column=columns, condition=conditions)
        self.assertGreater(len(results_1), len(results_2))
        for r in results_2:
            self.assertGreater(r[0], 10)
        logging.info(results_1)
        logging.info(results_2)


if __name__ == '__main__':
    unittest.main()