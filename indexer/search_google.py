from util.webdriver_util import ChromeDriver
driver = ChromeDriver()
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

class Indexer:
    def __init__(self, driver):
        self.driver = driver
    def go_and_search_google(self,keyword):
        self.driver.get('https://www.google.com')
        search = driver.find_element_by_css_selector("input[name='q']")
        search.send_keys(keyword)
        search.send_keys(Keys.RETURN)

    def get_source(self):
        pass
    def change_settings(self):
        settings = self.driver.find_element_by_css_selector('a.hdtb-tl')
        settings.click()
        done = False

        time.sleep(1)
        WebDriverWait(driver, 0.001).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.mn-hd-txt")))
        for element in self.driver.find_elements_by_css_selector('div.mn-hd-txt'):
            element.click()
            for i in self.driver.find_elements_by_css_selector('a.q.qs'):
                if i.text == 'Past week':
                    i.click()
                    done = True
                    break
            if done == True:
                break
index = Indexer(driver)
index.go_and_search_google('google.com')
index.change_settings()