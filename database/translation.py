from database import DataBase
import unittest
import logging
from database import MANDATORY, OPTIONAL
from util.text_util import TextHelper
from typing import List, Dict, Tuple, Optional, Any


logger = logging.getLogger("DataBase.Translation")

class TranslationDB(DataBase):

    COLUMN_CONSTRAINT = {
        "id": (MANDATORY, int, 32),
        "language_id": (MANDATORY, int, 8),
        "title": (OPTIONAL, str, 256),
        "snippet": (OPTIONAL, str, 512),
        "content": (OPTIONAL, str, 128)
    }
    INSERT_COLUMN_CONSTRAINT = ["language_id", "title", "snippet", "content"]
    UPDATE_COLUMN_CONSTRAINT = ["id", "language_id", "title", "snippet", "content"]
    SELECT_COLUMN_CONSTRAINT = ["id", "language_id", "title", "snippet", "content"]

    def __init__(self, user=None, password=None, host=None, database=None):
        # type: (Optional[str], Optional[str], Optional[str], Optional[str]) -> None
        super(TranslationDB, self).__init__("translation", user=user, password=password, host=host, database=database)

    def get_translation_by_id(self, id, column=None, record_as_dict=False):
        # type: (int) -> Any
        if not column:
            column = self.SELECT_COLUMN_CONSTRAINT
        return self.fetch_record(column=column, condition=["id = %d" % id], record_as_dict=record_as_dict)

    def add_translation(self, title=None, snippet=None, content=None, language_id=0):
        # type: (Optional[str], Optional[str], Optional[str], Optional[int]) -> int
        translation_id = 0
        if title or snippet or content:
            translation_id = self.add_translation_db(title=title, snippet=snippet, content=content, language_id=language_id)
            logger.info("Added translation [ID=%d]" % translation_id)
        return translation_id


    def add_translation_db(self, title=None, snippet=None, content=None, language_id=0):
        # type: (Optional[str], Optional[str], Optional[str], Optional[int]) -> int
        record = dict()
        record.update({"language_id": language_id}) if language_id else None
        record.update({"title": title}) if title else None
        record.update({"snippet": snippet}) if snippet else None
        record.update({"content": content}) if content else None
        if self.insert_record(record=record):
            return self._db._cursor.lastrowid
        return 0

    def update_translation_by_id(self, id, title=None, snippet=None, content=None, language_id=0):
        # type: (int, Optional[str], Optional[str], Optional[str], Optional[int]) -> None
        record = dict()
        record.update({"language_id": language_id}) if language_id else None
        record.update({"title": title}) if title else None
        record.update({"snippet": snippet}) if snippet else None
        record.update({"content": content}) if content else None
        self.update_record(record=record, condition=["id=%d" % id])


from util.config_util import Configure
from util.common import LoggedTestCase

config = Configure()

SANDBOX_USER = config.sandbox["db_user"]
SANDBOX_PASSWORD = config.sandbox["db_password"]
SANDBOX_HOST = config.sandbox["db_host"]
SANDBOX_DATABASE = config.sandbox["db_schema"]


class TestSourceData(LoggedTestCase):

    def setUp(self):
        self.data = TranslationDB(user=SANDBOX_USER, password=SANDBOX_PASSWORD, host=SANDBOX_HOST, database=SANDBOX_DATABASE)

    def test_get_translation_by_id(self):
        result = self.data.get_translation_by_id(1)
        self.assertEqual(result, 1)

    def test_get_non_exist_translation_id(self):
        result = self.data.get_translation_by_id(999999999)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()