import sys
import os
from datetime import date, datetime, timedelta
from util.common import LoggedTestCase
import unittest
from util.config_util import Configure
from util import generate_random_alphanumeric_string, create_parent_folders, human_format
import logging
from googletrans import Translator
from util.webdriver_util import ChromeDriver
import time
from nltk.tokenize import sent_tokenize
from util.common import MetaClassSingleton


logger = logging.getLogger("Util.Text")

TODAY = date.today()

config = Configure()

WEBSITE_BASE_PATH = config.setting["website_path"]
TEXT_BASE_PATH = config.setting["text_path"]
TEXT_PATH = os.path.join(TEXT_BASE_PATH, str(TODAY.year), "%02d" % TODAY.month, "%02d" % TODAY.day)

MAX_ALLOWED_API_TEXT_LENGTH = 512
MAX_ALLOWED_WEB_TEXT_LENGTH = 4980
DELIMITER = "%%"

class Translation(metaclass=MetaClassSingleton):

    __metaclass__ = MetaClassSingleton

    def __init__(self, text=None, language=None):
        self.driver = None
        self.page = None
        self.last = None
        self.text = text
        self.language = language

    def set_text(self, text):
        self.text = text

    def set_language(self, language):
        self.language = language

    def translate(self, language=None):
        if len(self.text) < MAX_ALLOWED_API_TEXT_LENGTH:
            return self.translate_use_googletrans(language=language)
        return self.translate_use_website(language=language)

    def translate_use_googletrans(self, language=None): # Limitation of length and usage frequency
        language = language or self.language
        if language:
            translator = Translator(service_urls=[
                "translate.google.com",
                "translate.google.co.uk",
                "translate.google.ca",
                "translate.google.com.au",
                "translate.google.co.in",
                "translate.google.co.jp"
            ])
            if self.last and (datetime.now() - self.last < timedelta(seconds=2)):
                time.sleep(2.0)
            self.last = datetime.now()
            return translator.translate(self.text, dest=language).text
        return self.text

    def translate_use_website(self, language=None):
        language = language or self.language
        if language:
            self.driver.get(self.page.build_translation_url(language=language))
            paragraphs = self.split_into_paragraphs(self.text)
            translation = ""
            for p in paragraphs:
                time.sleep(2.0) if translation else None
                self.page.input.send_keys(p)
                translation += self.page.output
            return translation
        return self.text

    def split_into_paragraphs(self, text=None):
        text = text or self.text
        sentences = sent_tokenize(text)
        current_paragraph = ""
        paragraphs = []
        for s in sentences:
            if len(current_paragraph + s) <= MAX_ALLOWED_WEB_TEXT_LENGTH:
                current_paragraph += s
            else:
                paragraphs.append(current_paragraph)
                current_paragraph = s
        if current_paragraph:
            paragraphs.append(current_paragraph)
        return paragraphs


class GoogleTranslation(Translation):

    def __init__(self, text=None, language="zh-CN"):
        super(GoogleTranslation, self).__init__(text=text, language=language)

    def translate_use_website(self, language=None):
        from webpage.google import GoogleTranslationPage
        self.driver = ChromeDriver()
        self.page = GoogleTranslationPage(self.driver)
        return super(GoogleTranslation, self).translate_use_website(language=language)


class TextHelper:

    def __init__(self, text, path=None, language="zh-CN"):
        self.text = text
        self._path = path
        self.language = language

    def set_text(self, text):
        self.text = text

    def set_language(self, language):
        self.language = language

    @property
    def path(self):
        if not self._path:
            self._path = os.path.join(TEXT_PATH, generate_random_alphanumeric_string(24) + ".txt")
        elif not os.path.isabs(self._path):
            self._path = os.path.normpath(os.path.join(WEBSITE_BASE_PATH, self._path))
        return self._path

    def get_translation_path(self, language=None):
        language = language or self.language
        name, extension = os.path.splitext(os.path.basename(self.path))
        return os.path.join(os.path.dirname(self.path), "%s_%s%s" % (name, language, extension))

    def save(self):
        try:
            create_parent_folders(self.path)
            with open(self.path, "w") as fh:
                fh.write(self._text)
            return self.path
        except:
            return None

    def translate(self, language="zh-CN"):
        tl = GoogleTranslation(self._text)
        return tl.translate(language=language)

    def save_translation(self, language="zh-CN"):
        try:
            path = self.get_translation_path(language=language)
            create_parent_folders(path)
            with open(path, "w") as fh:
                fh.write(self.translate(language=language))
            return path
        except:
            return None


class TestCase(LoggedTestCase):

    def setUp(self):
        self.text = TextHelper(text=None)

    def test_save_text(self):
        self.text.save()
        self.assertTrue(os.path.exists(self.text.path))

    def test_translate_text(self):
        self.text.translate()
        self.assertTrue(os.path.exists(self.text.path))


if __name__ == '__main__':
    unittest.main()