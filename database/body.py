from database import DataBase
import unittest
import logging
from database import MANDATORY, OPTIONAL
from util.text_util import TextHelper


logger = logging.getLogger("DataBase.Image")


class BodyDB(DataBase):

    COLUMN_CONSTRAINT = {
        "id": (str, OPTIONAL),
        "path": (str, MANDATORY)
    }
    INSERT_COLUMN_CONSTRAINT = ["path"]
    UPDATE_COLUMN_CONSTRAINT = ["id", "path"]
    SELECT_COLUMN_CONSTRAINT = ["id", "path"]

    def __init__(self, user=None, password=None, host=None, database=None):
        super(BodyDB, self).__init__("body", user=user, password=password, host=host, database=database)

    def get_body_path_by_id(self, id):
        result = self.fetch_record(column="path", condition=["id = %d" % id])
        return result[0] if result else None

    def get_body_id_by_path(self, path):
        result = self.fetch_record(column="id", condition=["path = '%s'" % path])
        return result[0] if result else 0

    def add_body(self, text=None):
        body_id = 0
        if text:
            img = TextHelper(text)
            logger.debug("Save text into path [%s]" % img.path)
            if img.save():
                return self.add_image_db(path=img.path)
        return body_id

    def add_body_db(self, path=None):
        record = dict(path=path)
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
        self.data = BodyDB(user=SANDBOX_USER, password=SANDBOX_PASSWORD, host=SANDBOX_HOST, database=SANDBOX_DATABASE)
        self.data.delete_records()
        self.id = self.data.add_boy(path="/path/to/body1")

    def test_get_body_path_by_id(self):
        path = self.data.get_body_path_by_id(self.id)
        self.assertEqual(path, "/path/to/body1")

    def test_get_body_id_by_path(self):
        id = self.data.get_body_id_by_path('/path/to/body1')
        self.assertEqual(id, self.id)


if __name__ == "__main__":
    unittest.main()