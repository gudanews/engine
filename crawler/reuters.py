from util import datetime_util, image_util
from crawler import Crawler as BaseCrawler
from util.webdriver_util import ChromeDriver
from webpage.reuters import ReutersPage
from database.news_headline import NewsHeadlineDB
from database.image import ImageDB
import logging
import time


logger = logging.getLogger("CRAWLERS.Reuters")

MAX_CRAWLING_PAGES = 1
MIN_ALLOWED_UNRECORD_NEWS_TO_CONTINUE_CRAWLING = 3
REUTERS_ID = 1


class ReutersCrawler(BaseCrawler):

    def __init__(self, browser):
        self.homepage = "https://www.reuters.com/news/archive/us-the-wire?view=page"
        super(ReutersCrawler, self).__init__(browser)

    def goto_homepage(self):  # goes to reuters
        self.driver.get(self.homepage)

    def goto_nextpage(self):  # goes to next page
        page = ReutersPage(self.driver)
        page.next.click()
        logger.info("Click to Next Page on the source News website......")

    def insert_records(self):
        page = ReutersPage(self.driver)
        headline_db = NewsHeadlineDB()
        image_db = ImageDB()
        columns = ["heading", "url"]
        existing_data = headline_db.get_latest_news(column=columns, source=REUTERS_ID)
        unrecorded_news = 0
        for np in page.news:
            if not (np.heading, np.url) in existing_data:
                np.wrapper.scroll_to()
                time.sleep(0.5)
                image_id = image_db.get_image_id_by_url(np.image)
                if not image_id:
                    image_file_path = image_util.save_image_from_url(np.image)
                    image_id = image_db.add_image(url=np.image, path=image_file_path)
                record = dict(heading=np.heading, datetime=datetime_util.str2datetime(np.time), source_id=REUTERS_ID,
                              image_id=image_id, url=np.url, snippet=np.snippet)
                logger.info("Insert the following record into database:\n" +
                            "[Headline] :\t%s\n" % np.heading +
                            "[URL] :\t<%s>\n" % np.url +
                            "[Snippet] :\t%s\n" % np.snippet +
                            "[IMAGE] :\t%s\n\n" % np.image)
                headline_db.insert_db_record(record=record)
                unrecorded_news += 1
        self.complete = True if unrecorded_news < MIN_ALLOWED_UNRECORD_NEWS_TO_CONTINUE_CRAWLING else False

    def crawl(self):
        self.goto_homepage()
        self.complete = False
        for i in range(MAX_CRAWLING_PAGES):
            self.insert_records()
            if not self.complete and i < MAX_CRAWLING_PAGES - 1:
                self.goto_nextpage()
            else:
                break


if __name__ == "__main__":
    driver = ChromeDriver()
    crawler = ReutersCrawler(driver)
    crawler.crawl()
