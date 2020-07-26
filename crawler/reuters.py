from util import datetime_util
from crawler import Crawler as BaseCrawler
from util.webdriver_util import ChromeDriver
from webpage.reuters import ReutersPage
from database.news_headline import NewsHeadlineDB
from database.image import ImageDB
import logging
import time
from util.image_util import ImageHelper
from furl import furl

logger = logging.getLogger("Crawler.Reuters")

MAX_CRAWLING_PAGES = 10
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
        logger.info("Click to Next Page on the Reuters News website......\n\n")
        time.sleep(2.0)

    def insert_records(self):
        page = ReutersPage(self.driver)
        headline_db = NewsHeadlineDB()
        image_db = ImageDB()
        columns = ["url"]
        existing_data = headline_db.get_latest_news(column=columns, source=REUTERS_ID)
        unrecorded_news = 0
        for np in page.news:
            if not (np.url) in existing_data:
                np.root.scroll_to()
                time.sleep(0.5)
                image_id = image_db.get_image_id_by_url(np.image)
                if not image_id:
                    # Change the image url to download image width=1024
                    f = furl(np.image)
                    f.args["w"] = "1024"
                    img = ImageHelper(f.url)
                    if img.download_image():
                        image_id = image_db.add_image(url=img.url, path=img.db_path, thumbnail=img.db_thumbnail)
                record = dict(heading=np.heading, datetime=datetime_util.str2datetime(np.time), source_id=REUTERS_ID,
                              image_id=image_id, url=np.url, snippet=np.snippet)
                logger.info("Insert the following Reuteres record into database:\n" +
                            "[Headline] :\t%s\n" % np.heading +
                            "[URL] :\t<%s>\n" % np.url +
                            "[Date] :\t<%s>\n" % np.time +
                            "[Snippet] :\t%s\n" % np.snippet +
                            "[ImageURL] :\t%s\n\n" % np.image)
                headline_db.insert_db_record(record=record)
                unrecorded_news += 1
        logger.info("Found [%d] unrecorded news on this page......\n" % unrecorded_news)
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
        logger.info("=" * 60)
        logger.info(">>>>>>>>>        Crawling Reuters completed        <<<<<<<<<")
        logger.info("=" * 60)

if __name__ == "__main__":
    driver = ChromeDriver()
    crawler = ReutersCrawler(driver)
    crawler.crawl()
