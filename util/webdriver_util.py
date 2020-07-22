import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

USE_HEADLESS_CHROME = os.environ.get("BROWSER", "CHROME") == "HEADLESS_CHROME"
class MetaClassSingleton(type):
    """
    Meta class implementation
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Override __call__ special method based on singleton pattern
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaClassSingleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]


class Driver(metaclass=MetaClassSingleton):
    """
    Driver class decorated by the meta class: MetaClassSingleton.
    Behaviour changed in singleton
    """
    connection = None

    def connect(self):
        """
        Set the connection with the web driver
        :return: web driver
        """
        if self.connection is None:
            chrome_options = Options()
            if USE_HEADLESS_CHROME:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--mute-audio")
            chrome_options.add_argument("--start-maximized")
            self.connection = webdriver.Chrome(options=chrome_options)

        return self.connection

def scroll_down(driver):
    j = 0
    try:
        #print("Start scrolling down......")
        while j <= driver.execute_script("return document.body.scrollHeight"):
            j += 250
            driver.execute_script("window.scrollTo(0, " + str(j) + ")")
            time.sleep(0.05)
            #print("Finish scrolling down......")
    except:
        pass