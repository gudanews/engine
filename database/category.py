from database import DataBase
import unittest
import logging
from database import MANDATORY, OPTIONAL


logger = logging.getLogger("DataBase.Image")


class CategoryDB(DataBase):

    COLUMN_CONSTRAINT = {
        "id": (int, OPTIONAL),
        "name": (str, OPTIONAL),
        "alias": (str, OPTIONAL)
    }
    INSERT_COLUMN_CONSTRAINT = ["name", "alias"]
    UPDATE_COLUMN_CONSTRAINT = ["id", "name", "alias"]
    SELECT_COLUMN_CONSTRAINT = ["id", "name", "alias"]

    def __init__(self, user=None, password=None, host=None, database=None):
        super(CategoryDB, self).__init__("category", user=user, password=password, host=host, database=database)

    def get_category_id_by_name(self, name):
        result = self.fetch_record(column="id", condition=["name = '%s'" % name])
        return result[0] if result else 0

    def get_category_name_by_id(self, id):
        result = self.fetch_record(column="name", condition=["id = %d" % id])
        return result[0] if result else None

    def add_category(self, name=None, alias=None):
        record = dict()
        record.update({"name": name}) if name else None
        record.update({"alias": alias}) if alias else None
        if self.insert_record(record=record):
            return self._db._cursor.lastrowid
        return 0


from util.config_util import Configure
from util.common import LoggedTestCase

config = Configure()

SANDBOX_USER = config.sandbox["db_user"]
SANDBOX_PASSWORD = config.sandbox["db_password"]
SANDBOX_HOST = config.sandbox["db_host"]
SANDBOX_DATABASE = config.sandbox["db_schema"]


class TestImageData(LoggedTestCase):

    def setUp(self):
        self.data = CategoryDB(user=SANDBOX_USER, password=SANDBOX_PASSWORD, host=SANDBOX_HOST, database=SANDBOX_DATABASE)
        self.data.delete_records()
        self.id = self.data.add_category(name="category1")
        self.data.add_category(name="category2", alias="alias2")

    def test_get_category_id_by_name(self):
        id = self.data.get_category_id_by_name('category1')
        self.assertEqual(id, self.id)

    def test_get_category_name_by_id(self):
        name = self.data.get_category_name_by_id(self.id)
        self.assertEqual(name, "category1")

    def test_get_category_id_by_non_exist_name(self):
        id = self.data.get_category_id_by_name('does_not_exist')
        self.assertEqual(id, 0)


if __name__ == "__main__":
    unittest.main()