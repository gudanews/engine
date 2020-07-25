import unittest
from holmium.core import Element, Locators, Section, Sections, Page
from util.webdriver_util import Driver, scroll_down
from util import datetime_util, image_util
from crawler import Crawler as BaseCrawler
from util.webdriver_util import Driver, scroll_down
from webpage.cnn import CNNPage
from database.news_headline import NewsHeadlineDB
class Section(Sections):
    heading = Element(
        Locators.CSS_SELECTOR,
        "div.card-headline h3.tnt-headline a",
        value=lambda el: el.text,
        timeout=5
    )
    time = Element(
        Locators.CSS_SELECTOR,
        "div.card-meta ul.list-inline li.card-date time",
        value=lambda el: el.text,
        timeout=5
    )
    url = Element(
        Locators.CSS_SELECTOR,
        "h3.tnt-headline a",
        value=lambda el: el.get_attribute('href'),
        timeout=5
    )
    snippet = Element(
        Locators.CSS_SELECTOR,
        "p.tnt-summary",
        value=lambda el: el.text,
        timeout=5
    )
class APPage(Page):
    news = Section(
        Locators.XPATH,
        "//div[@class='card-container']//div[@class='card-label-flags']/../..",
        timeout=10
    )

class APCrawler(BaseCrawler):
    def __init__(self, driver):
        self.homepage = "https://www.americanpress.com/news/"
        super(APCrawler, self).__init__(driver)

    def goto_homepage(self):
        self.driver.get(self.homepage)
        self.page = APPage(self.driver)
        self.story_contents = []
        scroll_down(self.driver)

    def insert_records(self):
        db_news_headline = NewsHeadlineDB()
        columns = ["heading", "url"]
        existing_data = db_news_headline.get_latest_news(column=columns)
        for n in self.page.news:
            if not (n.heading, n.url) in existing_data:
                record = dict(heading=n.heading, source_id=2, url=n.url)
                db_news_headline.insert_db_record(record=record)
    def crawl(self):
        self.goto_homepage()
        self.insert_records()
driver = Driver().connect()
ac = APCrawler(driver)
ac.crawl()
#class TestBaseData(unittest.TestCase):
#
#    def setUp(self):
#        self.driver = Driver().connect()
#        self.driver.get('https://www.americanpress.com/news/')
#        self.page = APPage(self.driver)
#
#    def test(self):
#        a = 1
#        for i in self.page.news:
#            print(i.heading)
#
#if __name__ == '__main__':
#    #unittest.main()
#    pass