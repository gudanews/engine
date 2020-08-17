from database import DataBase
import unittest
import logging
from database import MANDATORY, OPTIONAL
from typing import List, Dict, Tuple, Optional, Any


logger = logging.getLogger("DataBase.Image")


CATEGORY_MAPPING = {
    "top": ["top", "hot", "trend"],
    "local": ["local", "city", "town"],
    "national": ["us", "u.s.", "nation"],
    "world": ["world", "international", "asia", "europe", "africa", "australia", "america"],
    "opinion": ["opinion"],
    "politics": ["politic", "law", "religion", "court", "defense"],
    "business": ["business", "trade", "legal", "deal", "car", "money", "financ"],
    "technology & science": ["tech", "environ", "cyber", "science"],
    "entertainment & art": ["entertain", "art", "movie", "music", "tv"],
    "health": ["health"],
    "sport": ["sport", "mlb", "nfl", "nba", "race", "ball"],
    "weather": ["climate", "weather"],
    "lifestyle & culture": ["animal","relationship", "fashion", "culture", "life", "style", "architecture",
                            "beauty", "design", "food", "drink", "travel"],
    "multimedia": ["video", "audio"],
    "ads": ["sponsor"],
}

def category_mapping(phrase):
    if phrase:
        for (k, v) in CATEGORY_MAPPING.items():
            if phrase and any(c in phrase.lower() for c in v):
                return k
    return None

class CategoryDB(DataBase):

    COLUMN_CONSTRAINT = {
        "id": (MANDATORY, int, 32),
        "name": (MANDATORY, str, 32),
        "display": (OPTIONAL, str, 64),
        "color": (OPTIONAL, str, 8)
    }
    INSERT_COLUMN_CONSTRAINT = ["name", "display", "color"]
    UPDATE_COLUMN_CONSTRAINT = ["id", "name", "display", "color"]
    SELECT_COLUMN_CONSTRAINT = ["id", "name", "display", "color"]

    def __init__(self, user=None, password=None, host=None, database=None):
        # type: (Optional[str], Optional[str], Optional[str], Optional[str]) -> None
        super(CategoryDB, self).__init__("category", user=user, password=password, host=host, database=database)

    def get_category_id_by_name(self, name):
        # type: (str) -> int
        result = self.fetch_record(column=["id"], condition=["name = '%s'" % name])
        return result[0] if result else 0

    def get_category_name_by_id(self, id):
        # type: (int) -> str
        result = self.fetch_record(column=["name"], condition=["id = %d" % id])
        return result[0] if result else None

    def add_category(self, name=None, display_name=None):
        # type: (Optional[str], Optional[str]) -> int
        record = dict()
        record.update({"name": name}) if name else None
        record.update({"display_name": display_name}) if display_name else None
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
        self.data.add_category(name="category2", display_name="display_name2")

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