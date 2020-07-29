from util.webdriver_util import ChromeDriver
import logging
import time
from util import datetime_util
from database.news_headline import NewsHeadlineDB
from database.image import ImageDB
from database.source import SourceDB
from util.image_util import ImageHelper
from datetime import datetime

DEBUGGING_TEST = False

NOW = datetime.now()
logger = logging.getLogger("Crawler")


class Crawler:

    MAX_CRAWLING_PAGES = 5
    MIN_ALLOWED_UNRECORD_NEWS_TO_CONTINUE_CRAWLING = 2
    WAIT_FOR_ELEMENT_READY = 1.0
    SOURCE_ID = None
    logger = logging.getLogger("Crawler")

    def __init__(self, driver, web_url, page):
        self.driver = driver
        self.web_url = web_url
        self.page = page
        self.current_page_number = 1
        self.total_found = 0
        if not self.SOURCE_ID:
            raise NotImplementedError("Please Provide A Valid SOURCE_ID Before Proceed......")

    def goto_main_page(self):  # goes to main page
        self.driver.get(self.web_url)

    def goto_next_page(self):  # goes to next page
        self.page.next.click()
        self.current_page_number += 1
        self.logger.info("Landing At [%s/%s] Page......\n" % (self.current_page_number, self.MAX_CRAWLING_PAGES))
        time.sleep(2.0)

    def is_valid_record(self, record):
        if not "url" in record.keys(): # element must contain url
            self.logger.warning("Record Does NOT Contain <URL> Field.\n%s" % record)
            return False
        return True

    def find_alternative_image_url(self, url):
        return url

    def process_image(self, url):
        if url:
            image_db = ImageDB()
            image_id = image_db.get_image_id_by_url(url)
            if not image_id:
                # Change the image url to download image with better resolution
                url_alternative = self.find_alternative_image_url(url)
                image_id = self.save_image(url_alternative)
                if not image_id:
                    if url_alternative != url:
                        self.logger.info("Alternative Image Link Failed: [%s]" % url_alternative)
                        image_id = self.save_image(url)
            return image_id
        return 0

    def save_image(self, url):
        if not DEBUGGING_TEST:
            img = ImageHelper(url)
            image_db = ImageDB()
            if img.download_image():
                return image_db.add_image(url=img.url, path=img.db_path, thumbnail=img.db_thumbnail)
        return 0

    def build_record_from_page_element(self, element):
        record = dict()
        for el in ("heading", "datetime", "url", "snippet", "image"):
            if el in dir(element):
                record[el] = eval("element." + el)
                if not record[el]:
                    record.pop(el)
                else:
                    record[el] = datetime_util.str2datetime(element.datetime) if el == "datetime" else \
                            record[el][:320] if el == "snippet" else \
                            record[el][:256] if el == "heading" else \
                            record[el][:512] if el in ("url", "image") else \
                            record[el]
                    if DEBUGGING_TEST:
                        self.logger.info("[%s]:\t%s" % (el.upper(), record[el]))
                    else:
                        self.logger.debug("[%s]:\t%s" % (el.upper(), record[el]))
        if not "datetime" in record.keys(): # Always provide a datetime for record
            record["datetime"] = datetime.now()
            if DEBUGGING_TEST:
                self.logger.info("[DATETIME]:\t%s" % record["datetime"])
            else:
                self.logger.debug("[DATETIME]:\t%s" % record["datetime"])
        return record

    def parse_current_page(self):
        headline_db = NewsHeadlineDB()
        columns = ["url"]
        existing_data = headline_db.get_latest_news(column=columns, source=self.SOURCE_ID)
        unrecorded_news = 0
        for np in self.page.news:
            if not (np.url,) in existing_data:  # ("abc",) is different than ("abc")
                np.root.scroll_to()
                time.sleep(self.WAIT_FOR_ELEMENT_READY)
                record = self.build_record_from_page_element(np)
                if self.is_valid_record(record):
                    try:
                        image_id = self.process_image(record["image"]) if "image" in record.keys() else 0
                        record["source_id"]=self.SOURCE_ID
                        record["image_id"]=image_id
                        record.pop("image", None) # Remove image key if exists
                        self.logger.info("Record To Be Inserted: %s" % record)
                        headline_id = headline_db.add_headline(record=record) if not DEBUGGING_TEST else 0
                        self.logger.info("Inserted New Record [ID=%s] into Database." % headline_id)
                    except Exception as e:
                        self.logger.warning("Unexpected Issues Happened When Crawling as Follows:")
                        self.logger.warning("%s" % e)
                        self.logger.warning("Problematic Record Details: %s" % record)
                    finally:
                        unrecorded_news += 1
                        self.total_found += 1
        self.logger.info("Found [%d] Unrecorded News on Current Page." % unrecorded_news)
        self.complete = True if unrecorded_news < self.MIN_ALLOWED_UNRECORD_NEWS_TO_CONTINUE_CRAWLING else False

    def crawl(self):
        source_db = SourceDB()
        source_name = source_db.get_source_name_by_id(self.SOURCE_ID)
        self.logger.info("===========  Crawling [%s] started  ===========" % source_name)
        self.goto_main_page()
        self.complete = False
        for i in range(self.MAX_CRAWLING_PAGES):
            try:
                self.parse_current_page()
            except:
                pass
            if self.complete or i == self.MAX_CRAWLING_PAGES - 1:
                break
            self.goto_next_page()
        self.logger.info("-----------  Total [%s] New Records  -----------" % self.total_found)
        self.logger.info("===========  Crawling [%s] completed  ===========\n" % source_name)


def main():
    import os
    from util import find_modules, find_public_classes
    from crawler import Crawler
    logger.info("=" * 40)
    logger.info("Started Crawling ......")
    logger.info("=" * 40)
    found = 0
    modules = find_modules(os.path.dirname(__file__))
    for module in modules:
        classes = find_public_classes(module)
        for _,cls in classes.items():
            if issubclass(cls, Crawler) and not issubclass(Crawler, cls):
                try:
                    driver = ChromeDriver()
                    obj = cls(driver)
                    obj.crawl()
                    found += obj.total_found
                    driver.close()
                except:
                    cls.logger.warning("Error happens to current crawler, continuing......")
    logger.info(">" * 40 + "<" * 40)
    logger.info(">>> Completed Crawling. Processing Time [%s]. Total Found [%d]. <<<" % (str(datetime.now() - NOW), found))
    logger.info(">" * 40 + "<" * 40 + "\n" * 2)



if __name__ == "__main__":
    main()
