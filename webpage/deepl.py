from holmium.core import Element, Elements, ElementMap, Locators, Section, Sections
from holmium.core import Page
from holmium.core.conditions import VISIBLE
from webpage import WAIT_FOR_ELEMENT_TIMEOUT, WAIT_FOR_SECTION_TIMEOUT, WAIT_FOR_MINIMUM_TIMEOUT, WAIT_FOR_PAGE_LOADING
import time


class DeepLTranslationPage(Page):
    input = Element(
        Locators.CSS_SELECTOR,
        "div[dl-test='translator-source'] textarea",
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    output = Element(
        Locators.CSS_SELECTOR,
        "div[dl-test='translator-target'] textarea",
        value=lambda el: el.get_attribute("value"),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    target_language_button = Element(
        Locators.CSS_SELECTOR,
        "button[dl-test='translator-target-lang-btn']",
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    target_language_list = ElementMap(
        Locators.CSS_SELECTOR,
        "div[dl-test='translator-target-lang-list'] button",
        key=lambda el:el.get_attribute("dl-lang"),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    accept_cookies = Element(
        Locators.CSS_SELECTOR,
        "button.dl_cookieBanner--buttonSelected",
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    translate_progress_popup = Element(
        Locators.CSS_SELECTOR,
        "div[dl-test='translator-progress-popup']",
        only_if=VISIBLE(),
        timeout=WAIT_FOR_PAGE_LOADING
    )

    def build_translation_url(self, language="ZH"):
        self.language = language
        return "https://www.deepl.com/translator"

    def input_text(self, text):
        script = "arguments[0].value=arguments[1];"
        self.driver.execute_script(script, self.input, text)

    def select_target_language(self, language):
        language = language or self.language
        # if self.accept_cookies:
        #     self.accept_cookies.click()
        self.target_language_button.click()
        self.target_language_list[language].scroll_to()
        time.sleep(WAIT_FOR_MINIMUM_TIMEOUT)
        self.target_language_list[language].click()
        time.sleep(WAIT_FOR_ELEMENT_TIMEOUT)
        self.input.scroll_to()
        time.sleep(WAIT_FOR_MINIMUM_TIMEOUT)
        wait_cycle_remains = 10
        while self.translate_progress_popup and wait_cycle_remains > 0:
            wait_cycle_remains -= 1
            time.sleep(WAIT_FOR_ELEMENT_TIMEOUT)
        time.sleep(WAIT_FOR_ELEMENT_TIMEOUT)

    def output_text(self):
        self.select_target_language(language=self.language)
        return self.output