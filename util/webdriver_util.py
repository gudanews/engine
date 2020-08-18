import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from util.common import LoggedTestCase
from util.common import MetaClassSingleton
import unittest
import logging
from util.config_util import Configure


logger = logging.getLogger("Util.WebDriver")

config = Configure()

USE_HEADLESS_CHROME = os.environ.get("BROWSER", config.setting["browser"]) == "HEADLESS_CHROME"


class ChromeDriver(webdriver.Chrome):
    """
    Driver class decorated by the meta class: MetaClassSingleton.
    Behaviour changed in singleton
    """
    #__metaclass__ = MetaClassSingleton

    def __init__(self):
        chrome_options = Options()
        if USE_HEADLESS_CHROME:
            chrome_options.add_argument("--headless")
        else:
            chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        # chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.popups": 1})
        chrome_options.add_argument("--window-size=1366,768")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--suppress-message-center-popups")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument("--no-first-run")


        super(ChromeDriver, self).__init__(options=chrome_options, desired_capabilities=None)

    def scroll_down(self):
        j = 0
        try:
            while j <= self.execute_script("return document.body.scrollHeight"):
                j += 250
                self.execute_script("window.scrollTo(0, " + str(j) + ")")
                time.sleep(0.05)
        except:
            pass

    def switch_to_new_tab(self):
        self.execute_script("window.open('');")
        self.close()
        self.switch_to.window(self.window_handles[-1])

    def __del__(self):
        try:
            self.quit()
        except:
            pass


class TestWebDriver(LoggedTestCase):

    def setUp(self):
        self.driver=ChromeDriver()

    def test_chrome_driver(self):
        self.driver.get('http://www.google.com')
        self.assertIsNotNone(self.driver.current_url)

if __name__ == '__main__':
    unittest.main()