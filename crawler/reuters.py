import threading
from datetime import datetime
import unittest
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from util.mysql import NewsHeadlineTableAction
from util import convert_to_datetime as datetimeUtil
from util import scroll_down
from holmium.core import Element, Elements, Locators, Sections
from holmium.core import Page
from crawler import Crawler as BaseCrawler

class Story(Sections):
    heading = Element(
        Locators.CSS_SELECTOR,
        "div.story-content h3.story-title",
        value=lambda el: el.text,
        timeout=5
    )
    time = Element(
        Locators.CSS_SELECTOR,
        "div.story-content > time.article-time > span",
        value=lambda el: el.text,
        timeout=5
    )
    url = Element(
        Locators.CSS_SELECTOR,
        "div.story-content > a[href]",
        value=lambda el: el.get_attribute('href'),
        timeout=5
    )
    snippet = Element(
        Locators.CSS_SELECTOR,
        "div.story-content > p",
        value=lambda el: el.text,
        timeout=5
    )
    image = Element(
        Locators.CSS_SELECTOR,
        "div.story-photo img[src]",
        value=lambda el: el.get_attribute('src'),
        timeout=5
    )

class ReutersPage(Page):
    news = Story(
        Locators.CSS_SELECTOR,
        "article.story",
        timeout=10
    )

class ReutersCrawler(BaseCrawler):

    def __init__(self, driver):
        super(ReutersCrawler, self).__init__(driver)

    def go_to_reuters(self):  # goes to reuters

        self.driver.get('https://www.reuters.com/theWire')
        self.page = ReutersPage(self.driver)
        self.story_contents = []
        scroll_down(self.driver)

    def insert_into_news_headlline_db(self):
        columns = ["heading","datetime"]
        conditions = None
        #conditions = ["datetime BETWEEN yesterdy and today"]
        db = NewsHeadlineTableAction()
        existing_data = db.fetch_db_record(column=columns, condition=conditions)
        for n in self.page.news:
            #print(n.image)
            #sys.exit()
            if not (n.heading,datetimeUtil.convert_to_datetime(n.time)) in existing_data:
                record = dict(heading=n.heading, datetime=datetimeUtil.convert_to_datetime(n.time), source_id=1, link=n.url,snippet=n.snippet,image=n.image)
                db.insert_db_record(record=record)


chrome_options = Options()
#chrome_options.add_argument("--headless")
chrome_options.add_argument("--mute-audio")
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=chrome_options)

f = ReutersCrawler(driver)
f.go_to_reuters()
f.insert_into_news_headlline_db()


def get_image(driver):
    driver.get('https://www.reuters.com/theWire')
    image = driver.find_element_by_css_selector('div.story-photo img')
    print(image.get_attribute('src'))
#get_image(driver)

