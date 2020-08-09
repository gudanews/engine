from database import DataBase
import unittest
import logging
from database import MANDATORY, OPTIONAL


logger = logging.getLogger("DataBase.Image")


class ImageDB(DataBase):

    SELECT_COLUMN_CONSTRAINT = ["id", "path", "thumbnail", "url"]

    INSERT_COLUMN_CONSTRAINT = {
        "path": (str, OPTIONAL),
        "thumbnail": (str, OPTIONAL),
        "url": (str, OPTIONAL)}

    UPDATE_COLUMN_CONSTRAINT = {
        "path": str,
        "thumbnail": str,
        "url": str}

    def __init__(self, user=None, password=None, host=None, database=None):
        super(ImageDB, self).__init__("image", user=user, password=password, host=host, database=database)

    def get_image_id_by_url(self, url):
        result = self.fetch_record(column="id", condition=["url = '%s'" % url])
        return result[0] if result else 0

    def add_image(self, url=None, path=None, thumbnail=None):
        record = dict()
        record.update({"url": url}) if url else None
        record.update({"path": path}) if path else None
        record.update({"thumbnail": thumbnail}) if thumbnail else None
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
        self.data = ImageDB(user=SANDBOX_USER, password=SANDBOX_PASSWORD, host=SANDBOX_HOST, database=SANDBOX_DATABASE)
        self.data.delete_records()
        self.id = self.data.add_image(url="http://www.reuters.com/image1", path="/path/to/image1", thumbnail=None)
        self.data.add_image(url="http://www.foxnews.com/image2", path="/path/to/image2", thumbnail="/path/to/image2_tn")

    def test_get_image_id_by_url(self):
        id = self.data.get_image_id_by_url('http://www.reuters.com/image1')
        self.assertEqual(id, self.id)

    def test_get_image_id_by_non_exist_url(self):
        id = self.data.get_image_id_by_url('does_not_exist')
        self.assertEqual(id, 0)


if __name__ == "__main__":
    unittest.main()