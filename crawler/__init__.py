from util.webdriver_util import ChromeDriver
import logging
import time
from database.headline import HeadlineDB
from database.image import ImageDB
from database.news import NewsDB
from database.source import SourceDB
from util.image_util import ImageHelper
from datetime import datetime

DEBUGGING_TEST = False

START_TIME = datetime.now()
logger = logging.getLogger("Crawler")


class Crawler:

    MAX_CRAWLING_PAGES = 5
    MIN_ALLOWED_UNRECORD_NEWS_TO_CONTINUE_CRAWLING = 2
    WAIT_FOR_PAGE_READY = 2.0
    WAIT_FOR_ELEMENT_READY = 1.0
    SOURCE_ID = None
    logger = logging.getLogger("Crawler")

    def __init__(self, driver, page, web_url):
        self.driver = driver
        self.page = page
        self.web_url = web_url
        self.current_page_number = 1
        self.total_found = 0
        self.start_time = datetime.now()
        if not self.SOURCE_ID:
            raise NotImplementedError("Please Provide A Valid SOURCE_ID Before Proceed......")

    def goto_main_page(self):  # goes to main page
        self.driver.get(self.web_url)
        time.sleep(self.WAIT_FOR_PAGE_READY)

    def goto_next_page(self):  # goes to next page
        self.page.next.click()
        self.current_page_number += 1
        self.logger.info("Go To Page [%s/%s]......\n" % (self.current_page_number, self.MAX_CRAWLING_PAGES))
        time.sleep(self.WAIT_FOR_PAGE_READY)

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
            # Change the image url to download image with better resolution
            url_alternative = self.find_alternative_image_url(url)
            image_id = image_db.get_image_id_by_url(url_alternative) or image_db.get_image_id_by_url(url)
            if not image_id:
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
            if img.download_image(generate_thumbnail=True):
                return image_db.add_image(url=img.url, path=img.db_path, thumbnail=img.db_thumbnail)
        return 0

    def update_record_with_page_element(self, record, element):
        for el in ("heading", "datetime", "snippet", "image"): # No need to insert url again
            if el in dir(element):
                record[el] = eval("element." + el)
                if not record[el]:
                    record.pop(el)
                else:
                    record[el] = record[el][:512] if el in ("snippet", "image") else \
                            record[el][:256] if el == "heading" else record[el]
                    if DEBUGGING_TEST:
                        self.logger.info("[%s]:\t%s" % (el.upper(), record[el]))
                    else:
                        self.logger.debug("[%s]:\t%s" % (el.upper(), record[el]))

    def parse_current_page(self):
        headline_db = HeadlineDB()
        news_db = NewsDB()
        columns = ["url"]
        existing_data = headline_db.get_latest_headlines_by_source(source=self.SOURCE_ID, column=columns)
        unrecorded_news = 0
        for np in self.page.news:
            record = dict(url=np.url[:512])
            if not (record["url"],) in existing_data:  # ("abc",) is different than ("abc")
                np.root.scroll_to()
                time.sleep(self.WAIT_FOR_ELEMENT_READY)
                self.update_record_with_page_element(record, np)
                if self.is_valid_record(record):
                    try:
                        image_id = self.process_image(record["image"]) if "image" in record.keys() else 0
                        record["source_id"]=self.SOURCE_ID
                        record["image_id"]=image_id
                        record.pop("image", None) # Remove image key and replace with image_id
                        headline_id = headline_db.add_headline(record=record) if not DEBUGGING_TEST else 0
                        self.logger.info("Inserted Into <headline> DB [ID=%s] With Values: %s." % (headline_id, record))
                        if headline_id:
                            record["headline_id"] = headline_id
                            news_id = news_db.add_news(record=record) if not DEBUGGING_TEST else 0
                            self.logger.info("Inserted Into <news> DB [ID=%s] With Values: %s." % (news_id, record))
                            if news_id:
                                headline_db.update_headline_by_id(id=record["headline_id"], record=dict(news_id=news_id)) if not DEBUGGING_TEST else None
                                self.logger.info("Update <headline> Record With [news_id].")
                    except Exception as e:
                        self.logger.warning("Unexpected Issues Happened When Crawling as Follows:")
                        self.logger.warning("%s" % e)
                        self.logger.warning("Problematic Record Details: %s" % record)
                    finally:
                        unrecorded_news += 1
                        self.total_found += 1
        self.logger.info("Found [%d] Unrecorded News on Current Page." % unrecorded_news)
        self.complete = False if unrecorded_news >= self.MIN_ALLOWED_UNRECORD_NEWS_TO_CONTINUE_CRAWLING else True

    def crawl(self):
        source_db = SourceDB()
        source_name = source_db.get_source_name_by_id(self.SOURCE_ID)
        self.logger.info("=====================  Crawling [%s] started  =====================" % source_name)
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
        self.logger.info("---------------------  Total [%s] New Records  ---------------------" % self.total_found)
        self.logger.info("===========  Crawling [%s] completed in [%s]  ===========\n" %
                         (source_name, str(datetime.now() - self.start_time)))


def main():
    import os
    from util import find_modules, find_public_classes
    from crawler import Crawler
    logger.info("=" * 40)
    logger.info("Started Crawling ......")
    logger.info("=" * 40 + "\n")
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
                except Exception as e:
                    cls.logger.warning("%s" % e)
                    cls.logger.warning("Error happens to current crawler, continuing......")
    logger.info(">" * 40 + "<" * 40)
    logger.info(">>> Completed Crawling. Processing Time [%s]. Total Found [%d]. <<<"
                % (str(datetime.now() - START_TIME), found))
    logger.info(">" * 40 + "<" * 40 + "\n" * 2)


if __name__ == "__main__":
    main()
