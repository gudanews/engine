from database import DataBase
import unittest
import logging
from database import MANDATORY, OPTIONAL
from util.image_util import ImageHelper
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any


logger = logging.getLogger("DataBase.Image")


class ImageDB(DataBase):

    COLUMN_CONSTRAINT = {
        "id": (MANDATORY, int, 32),
        "path": (OPTIONAL, str, 128),
        "thumbnail": (OPTIONAL, str, 128),
        "url": (OPTIONAL, str, 512),
        "datetime_created": (OPTIONAL, datetime)
    }
    INSERT_COLUMN_CONSTRAINT = ["path", "thumbnail", "url", "datetime_created"]
    UPDATE_COLUMN_CONSTRAINT = ["id", "path", "thumbnail", "url", "datetime_created"]
    SELECT_COLUMN_CONSTRAINT = ["id", "path", "thumbnail", "url", "datetime_created"]

    def __init__(self, user=None, password=None, host=None, database=None):
        # type: (Optional[str], Optional[str], Optional[str], Optional[str]) -> None
        super(ImageDB, self).__init__("image", user=user, password=password, host=host, database=database)

    def get_recent_image_id_by_url(self, url):
        # type: (Optional[str]) -> int
        result = self.fetch_record(column=["id"], condition=["url = '%s'" % url,
            "datetime_created > '%s'" % (datetime.strftime(datetime.now() - timedelta(days=60), "%Y-%m-%d %H:%M:%S"))])
        return result[0] if result else 0

    def get_image_id_by_url(self, url):
        # type: (Optional[str]) -> int
        result = self.fetch_record(column=["id"], condition=["url = '%s'" % url])
        return result[0] if result else 0

    def get_image_by_id(self, id, column:list=None):
        # type: (int, Optional[List]) -> Any
        if not column:
            column = self.SELECT_COLUMN_CONSTRAINT
        result = self.fetch_record(column=column, condition=["id = %d" % id])
        return result if result else None

    def get_image_url_by_news_id(self, news_id):
        # type: (int) -> str
        adv_query = "INNER JOIN news ON news.image_id = image.id WHERE news.id=%d" % news_id
        result = self.fetch_advanced_record(column=["image.url"], advanced=adv_query)
        return result[0] if result[0] else None

    def get_additional_image_url_by_news_id(self, news_id):
        # type: (int) -> List
        adv_query = "INNER JOIN news_image ON news_image.image_id = image.id WHERE news_image.news_id=%d" % news_id
        return [r[0] for r in self.fetch_advanced_records(column=["image.url"], advanced=adv_query)]

    def add_image(self, url=None, generate_thumbnail=False):
        # type: (Optional[str], Optional[bool]) -> int
        image_id = 0
        if url:
            image_id = self.get_recent_image_id_by_url(url)
            if not image_id:
                img = ImageHelper(url)
                logger.debug("Download image with URL [%s]" % url)
                if img.download_image(generate_thumbnail=generate_thumbnail):
                    if generate_thumbnail:
                        return self.add_image_db(url=img.url, path=img.db_path, thumbnail=img.db_thumbnail)
                    return self.add_image_db(url=img.url, path=img.db_path)
        return image_id

    def add_image_db(self, url=None, path=None, thumbnail=None):
        # type: (Optional[str], Optional[str], Optional[str]) -> int
        record = dict()
        record.update({"url": url}) if url else None
        record.update({"path": path}) if path else None
        record.update({"thumbnail": thumbnail}) if thumbnail else None
        if self.insert_record(record=record):
            return self._db._cursor.lastrowid
        return 0


class NewsImageDB(DataBase):

    COLUMN_CONSTRAINT = {
        "news_id": (MANDATORY, int, 32),
        "image_id": (MANDATORY, int, 32)
    }
    INSERT_COLUMN_CONSTRAINT = ["news_id", "image_id"]
    UPDATE_COLUMN_CONSTRAINT = ["news_id", "image_id"]
    SELECT_COLUMN_CONSTRAINT = ["news_id", "image_id"]


    def __init__(self, user=None, password=None, host=None, database=None):
        # type: (Optional[str], Optional[str], Optional[str], Optional[str]) -> None
        super(NewsImageDB, self).__init__("news_image", user=user, password=password, host=host, database=database)

    def get_all_image_id_by_news_id(self, news_id):
        # type: (int) -> List
        return [r[0] for r in self.fetch_records(column=["image_id"], condition=["news_id = %d" % news_id])]

    def add_news_image(self, news_id, image_id):
        # type: (int, int) -> None
        if news_id and image_id:
            record = dict(news_id=news_id, image_id=image_id)
            self.insert_record(record=record)
        else:
            logger.warning("Trying to insert invalid <news_image> record [news_id=%s, image_id=%s]" % (news_id, image_id))


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
        self.id = self.data.add_image_db(url="http://www.reuters.com/image1", path="/path/to/image1", thumbnail=None)
        self.data.add_image_db(url="http://www.foxnews.com/image2", path="/path/to/image2", thumbnail="/path/to/image2_tn")

    def test_get_image_id_by_url(self):
        id = self.data.get_image_id_by_url('http://www.reuters.com/image1')
        self.assertEqual(id, self.id)

    def test_get_image_by_id(self):
        result = self.data.get_image_by_id(self.id)
        self.assertEqual(result[3], "http://www.reuters.com/image1")
        self.assertEqual(result[1], "/path/to/image1")
        self.assertIsNone(result[2])

    def test_get_image_columns_by_id(self):
        result = self.data.get_image_by_id(self.id, column=["url"])
        self.assertEqual(len(result), 1)

    def test_get_image_id_by_non_exist_url(self):
        id = self.data.get_image_id_by_url('does_not_exist')
        self.assertEqual(id, 0)


if __name__ == "__main__":
    unittest.main()