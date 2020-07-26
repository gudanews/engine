from crawler import Crawler as BaseCrawler
from util import datetime_util
from util.webdriver_util import ChromeDriver
from webpage.americanpress import APPage
from database.news_headline import NewsHeadlineDB
from database.image import ImageDB
import time
import logging

logger = logging.getLogger("Crawler.AP")

class _APCrawler(BaseCrawler):
    def __init__(self, driver):
        self.homepage = "https://www.americanpress.com/news/"
        super(_APCrawler, self).__init__(driver)

    def goto_homepage(self):
        self.driver.get(self.homepage)
        self.page = APPage(self.driver)
        self.story_contents = []
    def insert_records(self):
        db_news_headline = NewsHeadlineDB()
        columns = ["heading", "url"]
        existing_data = db_news_headline.get_latest_news(column=columns)
        for n in self.page.news:
            if not (n.heading, n.url) in existing_data:
                record = dict(heading=n.heading, source_id=2, url=n.url,datetime=datetime_util.str2datetime(n.time))
                db_news_headline.insert_db_record(record=record)
    def crawl(self):
        self.goto_homepage()
        self.insert_records()


if __name__ == "__main__":
    driver = ChromeDriver()
    crawler = _APCrawler(driver)
    crawler.crawl()
