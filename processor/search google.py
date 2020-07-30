from util.webdriver_util import ChromeDriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import string
from database.news_headline import NewsHeadlineDB

import random
from database.news_data import *


class searchGoogle():
    def __init__(self, driver):
        self.driver = driver

    def go_to_google_and_search_past_week(self, keyword):
        self.driver.get("https://www.google.com/search?q=" + str(keyword) + "&biw=1707&bih=924&tbs=qdr%3Aw")

    def get_urls(self):
        list_of_urls = []
        for result in self.driver.find_elements_by_css_selector('div.r'):
            for url in result.find_elements_by_css_selector('a'):
                list_of_urls.append(url.get_attribute('href'))
                break
        return list_of_urls

    def insert_into_database(self, list_of_urls, heading_id):
        datadb = NewsDataDB()
        column = ['link']
        existing_data = datadb.get_latest_news(column=column)
        i = 0
        for url in list_of_urls:
            if (url,) not in existing_data:
                i += 1
                record = dict(link=url, headline_id=heading_id, source_id=0, heading='None',
                              datetime=datetime.now(), snippet=None, image=None)
                datadb.insert_db_record(record=record)

    def grab_headlines_from_db(self):
        headline_db = NewsHeadlineDB()
        columns = ["heading"]
        output = []
        for data in headline_db.fetch_db_records(column=columns):
            existing_data = ''
            for i in range(2, len((str(data))) - 3):
                existing_data += str(data)[i]
            output.append(existing_data)
        return output

    def grab_id_from_db(self):
        headline_db = NewsHeadlineDB()
        columns = ["id"]
        output = []
        for data in headline_db.fetch_db_records(column=columns):
            existing_data = ''
            for i in range(1, len((str(data))) - 2):
                existing_data += str(data)[i]
            output.append(existing_data)
        return output
    def index(self):
        headlines = self.grab_headlines_from_db()
        ids = self.grab_id_from_db()
        for data in range(len(headlines)):
            self.go_to_google_and_search_past_week(headlines[data])
            urls = self.get_urls()

# seach.go_to_google_and_search_past_week('apple')
# urls = seach.get_urls()
# seach.insert_into_database(list_of_urls=urls)

import unittest

sg = searchGoogle(driver)
from util.common import LoggedTestCase


class TestSearchGoogle(LoggedTestCase):
    def test_go_to_google_and_search(self):
        for i in range(20):
            length = 10
            letters = string.ascii_lowercase
            result_str = ''.join(random.choice(letters) for i in range(length))
            sg.go_to_google_and_search_past_week(result_str)
    # def test_change_settings(self):
    #    sg.change_settings()


if __name__ == '__main__':
    # unittest.main()
    pass
