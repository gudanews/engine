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
from webpage.google import GoogleTranslationPage
from webpage.deepl import DeepLTranslationPage

logger = logging.getLogger("Util.Text")

TODAY = date.today()

config = Configure()

WEBSITE_BASE_PATH = config.setting["website_path"]
TEXT_BASE_PATH = config.setting["text_path"]
TEXT_PATH = os.path.join(TEXT_BASE_PATH, str(TODAY.year), "%02d" % TODAY.month, "%02d" % TODAY.day)

MAX_ALLOWED_API_TEXT_LENGTH = 512
MAX_ALLOWED_WEB_TEXT_LENGTH = 4800
DELIMITER = "\n%%%\n"

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

class Translator(metaclass=MetaClassSingleton):

    __metaclass__ = MetaClassSingleton

    def __init__(self, text=None, page_class=None, driver=None, language="zh-CN"):
        self.page_class = page_class
        self.driver = driver
        self.page = None
        self.last_use = None
        self.text = text
        self.language = language

    def set_text(self, text):
        self.text = text

    def set_language(self, language):
        self.language = language

    def translate_use_api(self, text=None, language=None): # Limitation of length and usage frequency
        text = text or self.text
        language = language or self.language
        if text and language and len(text) < MAX_ALLOWED_API_TEXT_LENGTH:
            translator = Translator(service_urls=[
                "translate.google.com",
                "translate.google.co.uk",
                "translate.google.ca",
                "translate.google.com.au",
                "translate.google.co.in",
                "translate.google.co.jp"
            ])
            if self.last_use and (datetime.now() - self.last_use < timedelta(seconds=2)):
                time.sleep(2.0)
            self.last_use = datetime.now()
            return translator.translate(text=text, dest=language).text
        return text

    def translate_use_website(self, text=None, language=None):
        text = text or self.text
        language = language or self.language
        if language:
            paragraphs = self.split_into_paragraphs(text)
            translation = ""
            for p in paragraphs:
                if not self.driver:
                    self.driver = ChromeDriver()
                else:
                    self.driver.switch_to_new_tab()
                if not self.page:
                    self.page = self.page_class(self.driver)
                self.driver.get(self.page.build_translation_url(language=language))
                self.page.input_text(p)
                translation += self.page.output_text()
                if p.endswith("\n"):
                    translation += "\n"
            logger.info("Translated text:\t%s" % translation)
            return translation
        return text

    def split_into_paragraphs(self, text=None):
        text = text or self.text
        # text = sent_tokenize(text)
        current_paragraph = ""
        paragraphs = []
        for s in text:
            if len(current_paragraph + s) <= MAX_ALLOWED_WEB_TEXT_LENGTH:
                current_paragraph += s
            else:
                paragraphs.append(current_paragraph)
                current_paragraph = s
        if current_paragraph:
            paragraphs.append(current_paragraph)
        return paragraphs


class GoogleTranslator(Translator):

    def __init__(self, text=None, page_class=GoogleTranslationPage, language="zh-CN"):
        super(GoogleTranslator, self).__init__(page_class=page_class, language=language)

class DeepLTranslator(Translator):

    def __init__(self, text=None, page_class=DeepLTranslationPage, language="ZH"):
        super(DeepLTranslator, self).__init__(page_class=page_class, language=language)


class TextHelper:

    def __init__(self, text="", path=None, language="ZH"):
        self.text = text
        self.translation_text = None
        self._texts = []
        self._translation_texts = []
        self._path = path
        self._translation_path = None
        self.language = language
        self.translator = DeepLTranslator(language=language)

    def set_text(self, text=None):
        self.text = text

    def add_additional_text(self, text):
        self._texts.append(text)

    def set_language(self, language):
        self.language = language

    def set_path(self, path):
        self._path = path
        self._translation_path = None

    def set_translation_path(self, path):
        self._translation_path = path

    def get_translation(self):
        return self.translation_text

    def get_additional_translation(self):
        return self._translation_texts

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
        elif not os.path.isabs(self._translation_path):
            self._translation_path = os.path.normpath(os.path.join(WEBSITE_BASE_PATH, self._translation_path))
        return self._translation_path

    @property
    def db_path(self):
        return os.path.relpath(self.path, WEBSITE_BASE_PATH)

    @property
    def db_translation_path(self):
        return os.path.relpath(self.translation_path, WEBSITE_BASE_PATH)

    def translate(self, language=None):
        language = language or self.language
        text = DELIMITER.join(self._texts)
        if self.text:
            text += DELIMITER + self.text
        translation_text = self.translator.translate_use_website(text, language)
        self._translation_texts = translation_text.split(DELIMITER)
        self.translation_text = self._translation_texts.pop(-1)

    def save_to_file(self):
        try:
            create_parent_folders(self.path)
            with open(self.path, "w") as fh:
                fh.write(self.text)
            return self.db_path
        except:
            return None

    def save_translation_to_file(self, language="ZH"):
        try:
            self.set_language(language=language)
            create_parent_folders(self.translation_path)
            with open(self.translation_path, "w") as fh:
                fh.write(self.translation_text)
            return self.db_translation_path
        except:
            return None


class TestCase(LoggedTestCase):

    def setUp(self):
        self.text = TextHelper(text="Hurtado was born Luisa Amelia Garcia Rodriguez Hurtado on Nov. 28, 1920, in Maiquetía, Venezuela. When she was 8, the family immigrated to New York City. She had a short-lived marriage to Chilean journalist Daniel del Solar and later, through her various art world connections, she met Paalen, an Austrian theorist and painter. By the 1940s, she was living in Mexico with Paalen and her two children during a time she later described as 'very bohemian,' socializing with artists including Frida Kahlo, Leonora Carrington and Oklahoma-born painter Mullican.")

    def _test_save_text(self):
        self.text.save()
        self.assertTrue(os.path.exists(self.text.path))

    def test_translate_text(self):
        abc = self.text.translate()
        self.assertFalse(os.path.exists(self.text.path))


if __name__ == '__main__':
    # unittest.main()
    th = TextHelper(text="""WASHINGTON (Reuters) - Chinese government-linked hackers targeted biotech company Moderna Inc, a U.S.-based coronavirus vaccine research developer, this year in a bid to steal data, according to a U.S. security official tracking Chinese hacking.
China on Friday rejected the accusation that hackers linked to it had targeted Moderna.
Last week, the U.S. Justice Department made public an indictment of two Chinese nationals accused of spying on the United States, including three unnamed U.S.-based targets involved in medical research to fight the novel coronavirus.
The indictment said the Chinese hackers “conducted reconnaissance” against the computer network of a Massachusetts biotech firm known to be working on a coronavirus vaccine in January.
Moderna, which is based in Massachusetts and announced its COVID-19 vaccine candidate in January, confirmed to Reuters that the company had been in contact with the FBI and was made aware of the suspected “information reconnaissance activities” by the hacking group mentioned in last week’s indictment.
Reconnaissance activities can include a range of actions, including probing public websites for vulnerabilities to scouting out important accounts after entering a network, cybersecurity experts say.
“Moderna remains highly vigilant to potential cybersecurity threats, maintaining an internal team, external support services and good working relationships with outside authorities to continuously assess threats and protect our valuable information,” said company spokesman Ray Jordan, declining to provide further detail.
The U.S. security official, who spoke on condition of anonymity, did not provide further details. The FBI and the U.S. Department of Health and Human Services declined to disclose the identities of companies targeted by Chinese hackers.
Moderna’s vaccine candidate is one of the earliest and biggest bets by the Trump administration to fight the pandemic.
The federal government is supporting development of the company’s vaccine with nearly half a billion dollars and helping Moderna launch a clinical trial of up to 30,000 people beginning this month.
China is also racing to develop a vaccine, bringing together its state, military and private sectors to combat a disease that has killed more than 660,000 people worldwide.
The July 7 indictment alleges that the two Chinese hackers, identified as Li Xiaoyu and Dong Jiazhi, conducted a decade-long hacking spree that most recently included the targeting of COVID-19 medical research groups.
Prosecutors said Li and Dong acted as contractors for China’s Ministry of State Security, a state intelligence agency. Messages left with several accounts registered under Li’s digital alias, oro0lxy, were not returned. Contact details for Dong were not available.
China has consistently denied any role in hacking and its foreign ministry spokesman in Beijing, Wang Wenbin, rejected as “baseless” the accusation that hackers linked to the government had targeted Moderna.
China leads the world in the development of a coronavirus vaccine and it is more worried that other countries using hackers to steal its technology, he said.
“We absolutely do not nor need to engage in theft to achieve this leading position,” Wang said.
The two other unidentified medical research companies mentioned in the Justice Department indictment are described as biotech companies based in California and Maryland. Prosecutors said the hackers “searched for vulnerabilities” and “conducted reconnaissance” against them.
The court filing describes the California firm as working on antiviral drug research and suggested the Maryland company had publicly announced efforts to develop a vaccine in January. Two companies that could match those descriptions: Gilead Sciences Inc and Novavax Inc.
Gilead spokesperson Chris Ridley said the firm does not comment on cybersecurity matters. Novavax would not comment on specific cyber security activities but said: “Our cyber security team has been alerted to the alleged foreign threats identified in the news.”
A security consultant familiar with multiple hacking investigations involving premier biotech firms over the last year said Chinese groups believed to be broadly associated with China’s Ministry of State security are one of the primary forces targeting COVID-19 research, globally. This matches the description of the indicted hackers, as ministry contractors.""")
    th.add_additional_text("Chile's Pinera vows crackdown after nine-year-old injured by gunfire in Araucania")
    th.add_additional_text("""BUKAVU, Congo (Reuters) - A soldier shot dead 12 people and injured nine others during a drunken rampage in eastern Democratic Republic of Congo on Thursday evening, regional authorities said. Security services are conducting a search for the gunman in the city of Sange, 15 miles (24 km) from the Burundian border, where the shooting took place, the governor of South Kivu province, Theo Kasi, said in a statement. President Felix Tshisekedi called the attack a heinous crime and offered his condolences to the victims’ families. Congo’s vast army is widely seen as poorly trained and unprofessional, and its personnel are frequently accused of committing crimes against civilians. Senior generals are under U.S. and EU sanctions for alleged abuses, and are accused by the United Nations of having supplied weapons to rebels and criminal gangs.""")
    th.translate()
    pass