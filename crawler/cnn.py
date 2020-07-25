from util import datetime_util, image_util
from crawler import Crawler as BaseCrawler
from util.webdriver_util import Driver, scroll_down
from webpage.cnn import CNNPage
from database.news_headline import NewsHeadlineDB
from database.image import ImageDB

class _CnnCrawler(BaseCrawler):

    def __init__(self, driver):
        self.homepage = "https://www.cnn.com/specials/last-50-stories"
        super(_CnnCrawler, self).__init__(driver)

    def goto_homepage(self):  # goes to cnn
        self.driver.get(self.homepage)
        self.page = CNNPage(self.driver)
        self.story_contents = []
        scroll_down(self.driver)

    def insert_records(self):
        db_news_headline = NewsHeadlineDB()
        columns = ["heading", "url"]
        existing_data = db_news_headline.get_latest_news(column=columns,source=101)
        for n in self.page.news:
            if not (n.heading, n.url) in existing_data:
                record = dict(heading=n.heading, source_id=101, url=n.url)
                db_news_headline.insert_db_record(record=record)
    def crawl(self):
        self.goto_homepage()
        self.insert_records()
if __name__ == "__main__":
    driver = Driver().connect()
    crawler = _CnnCrawler(driver)
    crawler.crawl()