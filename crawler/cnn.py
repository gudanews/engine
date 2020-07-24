from util.mysql_util import NewsHeadlineTableAction, ImageTableAction
from util import datetime_util, image_util
from holmium.core import Element, Locators, Sections
from holmium.core import Page
from crawler import Crawler as BaseCrawler
from util.webdriver_util import scroll_down
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class Story(Sections):
    heading = Element(
        Locators.CSS_SELECTOR,
        "div.cd__content h3.cd__headline span.cd__headline-text",
        value=lambda el: el.text,
        timeout=5
    )
    url = Element(
        Locators.CSS_SELECTOR,
        "div.cd__content h3.cd__headline a",
        value=lambda el: el.get_attribute('href'),
        timeout=5
    )

class ReutersPage(Page):
    news = Story(
        Locators.CSS_SELECTOR,
        "div.cd__content",
        timeout=10
    )

class CnnCrawler(BaseCrawler):

    def __init__(self, driver):
        super(CnnCrawler, self).__init__(driver)

    def goto_homepage(self):  # goes to reuters
        self.driver.get('https://www.cnn.com/specials/last-50-stories')
        self.page = ReutersPage(self.driver)
        self.story_contents = []
        scroll_down(self.driver)
    def insert_records(self):
        db_news_headline = NewsHeadlineTableAction()
        columns = ["heading", "url"]
        existing_data = db_news_headline.fetch_db_record(column=columns)
        for n in self.page.news:
            if not (n.heading, n.url) in existing_data:
                record = dict(heading=n.heading, source_id=101, url=n.url)
                db_news_headline.insert_db_record(record=record)
chrome_options = Options()
chrome_options.add_argument("--mute-audio")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)
cc = CnnCrawler(driver)
cc.goto_website()
cc.insert_records()
