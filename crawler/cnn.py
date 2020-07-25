from util import datetime_util, image_util
from crawler import Crawler as BaseCrawler
from util.webdriver_util import ChromeDriver
from webpage.cnn import CNNPage
from database.news_headline import NewsHeadlineDB
from database.image import ImageDB
import time
import logging
from datetime import  datetime
logger = logging.getLogger("Crawler.CNN")

class _CnnCrawler(BaseCrawler):

    def __init__(self, driver):
        self.homepage = "https://www.cnn.com/specials/last-50-stories"
        super(_CnnCrawler, self).__init__(driver)

    def goto_homepage(self):  # goes to cnn
        self.driver.get(self.homepage)
        self.page = CNNPage(self.driver)
        self.story_contents = []

    def insert_records(self):
        db_news_headline = NewsHeadlineDB()
        columns = ["heading", "url"]
        existing_data = db_news_headline.get_latest_news(column=columns,source=101)
        for np in self.page.news:
            # np.wrapper.scroll_to()
            time.sleep(0.2)
            if not (np.heading, np.url) in existing_data:
                record = dict(heading=np.heading, source_id=101, url=np.url,datetime=datetime.now())
                db_news_headline.insert_db_record(record=record)
                #logger.info("Insert the following record into database:\n" +
                #            "[Headline] :\t%s\n" % np.heading +
                #            "[URL] :\t<%s>\n" % np.url)

    def crawl(self):
        self.goto_homepage()
        self.insert_records()

if __name__ == "__main__":
    driver = ChromeDriver()
    crawler = _CnnCrawler(driver)
    crawler.crawl()