from database import DataBase
import unittest
import logging


class ImageDB(DataBase):

    def __init__(self):
        super(ImageDB, self).__init__("image")

    def get_image_id_by_url(self, url):
        result = self.fetch_db_record(column="id", condition=["url = '%s'" % url])
        return result[0] if result else None

    def add_image(self, url=None, path=None):
        self.insert_db_record(record=dict(url=url, path=path))
        return self.db._cursor.lastrowid


class TestImageData(unittest.TestCase):

    def setUp(self):
        self.data = ImageDB()

    def test_get_image_id_by_non_exist_url(self):
        id = self.data.get_image_id_by_url('does_not_exist')
        self.assertIsNone(id)
        logging.info(id)


if __name__ == "__main__":

    unittest.main()