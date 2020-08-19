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
import difflib

logger = logging.getLogger("Util.Text")

TODAY = date.today()

config = Configure()

WEBSITE_BASE_PATH = config.setting["website_path"]
TEXT_BASE_PATH = config.setting["text_path"]
TEXT_PATH = os.path.join(TEXT_BASE_PATH, str(TODAY.year), "%02d" % TODAY.month, "%02d" % TODAY.day)

MAX_ALLOWED_API_TEXT_LENGTH = 512
MAX_ALLOWED_WEB_TEXT_LENGTH = 4980
DELIMITER = "%%"

def checksimilarity(a, b):
    sim = difflib.get_close_matches
    s = 0
    wa = a.split()
    wb = b.split()
    for i in wb:
        if sim(i, wa):
            s += 1
    n = float(s) / float(len(wb))
    return n

class Translation(metaclass=MetaClassSingleton):

    __metaclass__ = MetaClassSingleton

    def __init__(self, text=None, language="zh-CN"):
        self.driver = None
        self.page = None
        self.last = None
        self.text = text
        self.language = language

    def set_text(self, text):
        self.text = text

    def set_language(self, language):
        self.language = language

    def translate(self, text=None, language=None):
        text = text or self.text
        language = language or self.language
        if text:
            if len(text) < MAX_ALLOWED_API_TEXT_LENGTH:
                return self.translate_use_googletrans(text=text, language=language)
            return self.translate_use_website(text=text, language=language)
        return None

    def translate_use_googletrans(self, text=None, language=None): # Limitation of length and usage frequency
        text = text or self.text
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
            return translator.translate(text=text, dest=language).text
        return text

    def translate_use_website(self, text=None, language=None):
        text = text or self.text
        language = language or self.language
        if language:
            paragraphs = self.split_into_paragraphs(text)
            translation = ""
            logger.info("Find [%d] paragraphs" % len(paragraphs))
            for p in paragraphs:
                if translation and self.last and (datetime.now() - self.last < timedelta(seconds=2)):
                    time.sleep(2.0)
                    logger.info("Sleeping 2 seconds")
                self.last = datetime.now()
                self.driver.switch_to_new_tab()
                self.driver.get(self.page.build_translation_url(language=language))
                self.page.input.send_keys(p)
                translation += self.page.output
                logger.info("Translated text:\t%s" % translation)
            return translation
        return text

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

    def translate_use_website(self, text=None, language=None):
        from webpage.google import GoogleTranslationPage
        if not self.driver:
            self.driver = ChromeDriver()
        self.page = GoogleTranslationPage(self.driver)
        return super(GoogleTranslation, self).translate_use_website(text=text, language=language)


class TextHelper:

    def __init__(self, text, path=None, language="zh-CN"):
        self.text = text
        self._path = path
        self._translation_path = None
        self.language = language
        self.translation = GoogleTranslation(text=text, language=language)

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

    @property
    def translation_path(self):
        if not self._translation_path:
            name, extension = os.path.splitext(os.path.basename(self.path))
            self._translation_path = os.path.join(os.path.dirname(self.path), "%s_%s%s" % (name, self.language, extension))
        return self._translation_path

    @property
    def db_path(self):
        return os.path.relpath(self.path, WEBSITE_BASE_PATH)

    @property
    def db_translation_path(self):
        return os.path.relpath(self.translation_path, WEBSITE_BASE_PATH)

    def save(self):
        try:
            create_parent_folders(self.path)
            with open(self.path, "w") as fh:
                fh.write(self.text)
            return self.db_path
        except:
            return None

    def translate(self, text=None, language=None):
        text = text or self.text
        language = language or self.language
        return self.translation.translate(text=text, language=language)

    def save_translation(self, language="zh-CN"):
        try:
            self.set_language(language=language)
            create_parent_folders(self.translation_path)
            with open(self.translation_path, "w") as fh:
                fh.write(self.translate())
            return self.db_translation_path
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