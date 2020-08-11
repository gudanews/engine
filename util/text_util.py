import sys
import os
from datetime import date
from util.common import LoggedTestCase
import unittest
from util.config_util import Configure
from util import generate_random_alphanumeric_string, create_parent_folders, human_format
import logging

logger = logging.getLogger("Util.Text")

TODAY = date.today()

config = Configure()

WEBSITE_BASE_PATH = config.setting["website_path"]
TEXT_BASE_PATH = config.setting["text_path"]
TEXT_PATH = os.path.join(TEXT_BASE_PATH, str(TODAY.year), "%02d" % TODAY.month, "%02d" % TODAY.day)

IMAGE_WIDTH = 648
IMAGE_HEIGHT = 365
THUMBNAIL_WIDTH = 144
THUMBNAIL_HEIGHT = 108
DEFAULT_FILLING = (255, 255, 255)
IMAGE_PIXEL_MIN = 20


class TextHelper:

    def __init__(self, text, path=None):
        self._text = text
        if not path:
            _name = generate_random_alphanumeric_string(24) + ".txt"
            path = os.path.join(TEXT_PATH, _name)
        elif not os.path.isabs(path):
            path = os.path.normpath(os.path.join(WEBSITE_BASE_PATH, path))
        self.path = path

    def save(self):
        try:
            create_parent_folders(self.path)
            with open(self.path, "w") as fh:
                fh.write(self._text)
            return True
        except:
            return False

    def translate(self):
        pass


class TestCase(LoggedTestCase):

    def setUp(self):
        self.text = TextHelper(text=None)

    def test_save_text(self):
        self.text.save()
        self.assertTrue(os.path.exists(self.text.path))

    def test_translate_text(self):
        self.text.translate()
        self.assertTrue(os.path.exists(self.text.path))


if __name__ == "__main__":
    unittest.main()
