from util.webdriver_util import ChromeDriver
from holmium.core import Page
import logging
import time
from util import datetime_util
from database.news_headline import NewsHeadlineDB
from database.image import ImageDB
from database.source import SourceDB
from util.image_util import ImageHelper


class Crawler:

    MAX_CRAWLING_PAGES = 20
    MIN_ALLOWED_UNRECORD_NEWS_TO_CONTINUE_CRAWLING = 3
    SOURCE_ID = None
    logger = logging.getLogger("Crawler")

    def __init__(self, driver, web_url, page):
        self.driver = driver
        self.web_url = web_url
        self.page = page
        if not self.SOURCE_ID:
            raise NotImplementedError("Please specify the SOURCE_ID")

    def goto_main_page(self):  # goes to reuters
        self.driver.get(self.web_url)

    def goto_nextpage(self):  # goes to next page
        self.page.next.click()
        self.logger.info("Click to continue on Next Page......\n")
        time.sleep(2.0)

    def find_alternative_image_url(self, url):
        return url

    def process_image(self, url):
        image_db = ImageDB()
        image_id = image_db.get_image_id_by_url(url)
        if not image_id:
            # Change the image url to download image right size image
            url_alternative = self.find_alternative_image_url(url)
            try:
                image_id = self.save_image(url_alternative)
            except:
                pass
            finally:
                if image_id == 0:
                    image_id = self.save_image(url)
        return image_id

    def save_image(self, url):
        img = ImageHelper(url)
        image_db = ImageDB()
        if img.download_image():
            return image_db.add_image(url=img.url, path=img.db_path, thumbnail=img.db_thumbnail)
        return 0

    def build_record_from_page_element(self, element):
        record = dict()
        for el in ("heading", "datetime", "url", "snippet"):
            if el in dir(element):
                exec("record[el] = element." + el)
                if el == "datetime":
                    record["datetime"] = datetime_util.str2datetime(element.datetime) # convert to proper datetime
                if el == "snippet":
                    record["snippet"] = record[el][:256] # limit the snippet 256
                self.logger.debug("[%s] :\t%s\n" % (el.upper(), record[el]))
        return record

    def parse_current_page(self):
        headline_db = NewsHeadlineDB()
        columns = ["url"]
        existing_data = headline_db.get_latest_news(column=columns, source=self.SOURCE_ID)
        unrecorded_news = 0
        for np in self.page.news:
            if not (np.url) in existing_data:
                np.root.scroll_to()
                time.sleep(0.5)
                image_id = self.process_image(np.image)
                self.logger.info("Inserting a new record into database.")
                record = self.build_record_from_page_element(np)
                record["source_id"]=self.SOURCE_ID
                record["image_id"]=image_id
                headline_db.insert_db_record(record=record)
                unrecorded_news += 1
        self.logger.info("Found [%d] unrecorded news on current page." % unrecorded_news)
        self.complete = True if unrecorded_news < self.MIN_ALLOWED_UNRECORD_NEWS_TO_CONTINUE_CRAWLING else False

    def crawl(self):
        self.goto_main_page()
        self.complete = False
        for i in range(self.MAX_CRAWLING_PAGES):
            try:
                self.parse_current_page()
            except:
                pass
            if self.complete or i >= self.MAX_CRAWLING_PAGES:
                break
            self.goto_nextpage()
        source_db = SourceDB()
        self.logger.info("=" * 50)
        self.logger.info("=" * 50)
        self.logger.info(">>>>>>>>>  Crawling [%s] completed  <<<<<<<<<" % source_db.get_source_name_by_id(self.SOURCE_ID))
        self.logger.info("=" * 50)
        self.logger.info("=" * 50)


def main():
    import os
    from util import find_modules, find_public_classes
    from crawler import Crawler
    modules = find_modules(os.path.dirname(__file__))
    for module in modules:
        classes = find_public_classes(module)
        for _,cls in classes.items():
            if issubclass(cls, Crawler) and not issubclass(Crawler, cls):
                try:
                    driver = ChromeDriver()
                    obj = cls(driver)
                    obj.crawl()
                except:
                    pass



if __name__ == "__main__":
    main()
