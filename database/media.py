from database import DataBase
import unittest
import logging
from database import MANDATORY, OPTIONAL


logger = logging.getLogger("DataBase.Image")


class MediaDB(DataBase):

    SELECT_COLUMN_CONSTRAINT = ["id", "type_id", "url"]

    INSERT_COLUMN_CONSTRAINT = {
        "type_id": (int, OPTIONAL),
        "url": (str, MANDATORY)}

    UPDATE_COLUMN_CONSTRAINT = {
        "type_id": int,
        "url": str}

    def __init__(self, user=None, password=None, host=None, database=None):
        super(MediaDB, self).__init__("media", user=user, password=password, host=host, database=database)

    def get_category_id_by_url(self, url):
        result = self.fetch_record(column="id", condition=["url = '%s'" % url])
        return result[0] if result else 0

    def add_category(self, url=None, type_id=None):
        record = dict()
        record.update({"type_id": type_id}) if type_id else None
        record.update({"url": url}) if url else None
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
        self.data = MediaDB(user=SANDBOX_USER, password=SANDBOX_PASSWORD, host=SANDBOX_HOST, database=SANDBOX_DATABASE)
        self.data.delete_records()
        self.id = self.data.add_category(url="http://www.reuters.com/video1", type_id=None)
        self.data.add_category(url="http://www.foxnews.com/video2")

    def test_get_media_id_by_url(self):
        id = self.data.get_category_id_by_url('http://www.reuters.com/video1')
        self.assertEqual(id, self.id)

    def test_get_media_id_by_non_exist_url(self):
        id = self.data.get_category_id_by_url('does_not_exist')
        self.assertEqual(id, 0)


if __name__ == "__main__":
    unittest.main()