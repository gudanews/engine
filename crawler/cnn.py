from util import datetime_util, image_util
from crawler import Crawler as BaseCrawler
from util.webdriver_util import ChromeDriver
from webpage.cnn import CNNPage
from database.news_headline import NewsHeadlineDB
from database.image import ImageDB
import time
import logging
from util.image_util import ImageHelper

logger = logging.getLogger("Crawler.CNN")

MAX_CRAWLING_PAGES = 20
MIN_ALLOWED_UNRECORD_NEWS_TO_CONTINUE_CRAWLING = 3
CNN_ID = 101

class CNNCrawler(BaseCrawler):

    def __init__(self, driver):
        self.homepage = "https://www.cnn.com/search?q=cnn"
        super(CNNCrawler, self).__init__(driver)

    def goto_homepage(self):  # goes to cnn
        self.driver.get(self.homepage)

    def goto_nextpage(self):  # goes to next page
        page = CNNPage(self.driver)
        page.next.click()
        logger.info("Click to Next Page on the CNN News website......\n\n")
        time.sleep(2.0)

    def insert_records(self):
        page = CNNPage(self.driver)
        headline_db = NewsHeadlineDB()
        image_db = ImageDB()
        columns = ["url"]
        existing_data = headline_db.get_latest_news(column=columns,source=CNN_ID)
        unrecorded_news = 0
        for np in page.news:
            if not (np.url) in existing_data:
                np.root.scroll_to()
                time.sleep(0.5)
                image_id = image_db.get_image_id_by_url(np.image)
                if not image_id:
                    # Change the image url to download larger image
                    img_url = np.image
                    if img_url and img_url.endswith("-story-body.jpg"):
                        img_url = "-exlarge-169".join(img_url.rsplit("-story-body", 1))
                    img = ImageHelper(img_url)
                    if img.download_image():
                        image_id = image_db.add_image(url=img.url, path=img.db_path, thumbnail=img.db_thumbnail)
                record = dict(heading=np.heading, datetime=datetime_util.str2datetime(np.date), source_id=CNN_ID,
                              image_id=image_id, url=np.url, snippet=np.snippet[:256])
                headline_db.insert_db_record(record=record)
                logger.info("Insert the following CNN record into database:\n" +
                            "[Headline] :\t%s\n" % np.heading +
                            "[URL] :\t<%s>\n" % np.url +
                            "[Date] :\t<%s>\n" % np.date +
                            "[Snippet] :\t%s\n" % np.snippet[:256] +
                            "[ImageURL] :\t%s\n\n" % np.image)
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
        logger.info(">>>>>>>>>          Crawling CNN completed          <<<<<<<<<")
        logger.info("=" * 60)


if __name__ == "__main__":
    driver = ChromeDriver()
    crawler = CNNCrawler(driver)
    crawler.crawl()