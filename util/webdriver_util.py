import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from util import MetaClassSingleton

USE_HEADLESS_CHROME = os.environ.get("BROWSER", "CHROME") == "HEADLESS_CHROME"

class ChromeDriver(webdriver.Chrome):
    """
    Driver class decorated by the meta class: MetaClassSingleton.
    Behaviour changed in singleton
    """
    __metaclass__ = MetaClassSingleton

    def __init__(self):
        chrome_options = Options()
        if USE_HEADLESS_CHROME:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--start-maximized")
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

    def __del__(self):
        try:
            self.quit()
        except:
            pass