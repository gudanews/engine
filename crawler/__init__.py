from util.webdriver_util import ChromeDriver
import logging
import time
from database.image import ImageDB, NewsImageDB
from database.news import NewsDB
from database.source import SourceDB
from database.category import CategoryDB, NewsCategoryDB
from datetime import datetime, timedelta

DEBUGGING_TEST = False

START_TIME = datetime.now()
logger = logging.getLogger("Crawler")


class Crawler:

    MAX_CRAWLING_PAGES = 5
    MIN_ALLOWED_UNRECORD_NEWS_TO_CONTINUE_CRAWLING = 2
    WAIT_FOR_PAGE_READY = 3.5
    WAIT_FOR_ELEMENT_READY = 1.0
    SOURCE_ID = None
    logger = logging.getLogger("Crawler")

    def __init__(self, driver, page, web_url):
        self.driver = driver
        self.page = page
        self.homepage_url = web_url
        self.current_page_number = 1
        self.total_checked = 0
        self.total_found = 0
        self.start_time = datetime.now()
        if not self.SOURCE_ID:
            raise NotImplementedError("Please Provide A Valid SOURCE_ID Before Proceed......")
        self.news_db = NewsDB()
        self.news_image_db = NewsImageDB()
        self.news_category_db = NewsCategoryDB()
        self.image_db = ImageDB()
        self.category_db = CategoryDB()
        self.source_db = SourceDB()
        self.existing_urls = [r[0] for r in self.news_db.get_latest_news_by_source_id(source_id=self.SOURCE_ID, column=["url"])]

    def goto_main_page(self):  # goes to main page
        self.driver.get(self.homepage_url)
        time.sleep(self.WAIT_FOR_PAGE_READY)

    def goto_next_page(self):  # goes to next page
        self.page.next.click()
        self.current_page_number += 1
        self.logger.info("Go To Page [%s/%s]......\n" % (self.current_page_number, self.MAX_CRAWLING_PAGES))
        time.sleep(self.WAIT_FOR_PAGE_READY)

    def is_valid_record(self, record):
        if not record.get("url", None) or (datetime.now() - record.get("datetime_created", datetime.now()) >= timedelta(days=14)):
            # element must contain url and within 14 days
            self.logger.warning("Record is not valid.\n%s" % record)
            return False
        return True

    def process_image(self, record):
        image_urls = record.get("image", None)
        if image_urls:
            for url in image_urls:
                self.logger.info("Add Image into ImageDB [%s]" % url)
                image_id = self.image_db.add_image(url, generate_thumbnail=True)
                if image_id > 0:
                    return image_id
        return 0

    def update_record_with_page_element(self, record, element):
        for el in ("title", "datetime_created", "snippet", "image", "category", "author"): # No need to insert url again
            if el in dir(element):
                record[el] = eval("element." + el)
                if not record[el]:
                    record.pop(el)
                else:
                    self.logger.info("[%s]:\t%s" % (el.upper(), record[el]))

    def create_database_record(self, record):
        record["image_id"] = self.process_image(record) if not DEBUGGING_TEST else 0
        record["category_id"] = self.category_db.get_category_id_by_name(record.get("category", None))
        record["source_id"] = self.SOURCE_ID
        news_id = self.news_db.add_news_use_record(record=record) if not DEBUGGING_TEST else 0
        self.logger.info("Inserted Into <news> DB [ID=%s] With Values: %s." % (news_id, record))
        if not DEBUGGING_TEST and news_id:
            if record["image_id"]:
                self.news_image_db.add_news_image(news_id=news_id, image_id=record["image_id"])
            if record["category_id"]:
                self.news_category_db.add_news_category(news_id=news_id, category_id=record["category_id"])

    def process_current_page(self):
        new_found = 0
        for np in self.page.news:
            self.total_checked += 1
            record = dict(url=np.url)
            if not record["url"] in self.existing_urls:  # ("abc",) is different than ("abc")
                np.root.scroll_to()
                time.sleep(self.WAIT_FOR_ELEMENT_READY)
                self.update_record_with_page_element(record, np)
                if self.is_valid_record(record):
                    try:
                        self.create_database_record(record)
                    except Exception as e:
                        self.logger.warning("Unexpected Issues Happened When Crawling as Follows:")
                        self.logger.warning("%s" % e)
                        self.logger.warning("Problematic Record Details: %s" % record)
                    finally:
                        self.existing_urls.append(record["url"])
                        new_found += 1
                        self.total_found += 1
        self.logger.info("Found [%d] Unrecorded News on Page [%d/%d]." % (new_found, self.current_page_number, self.MAX_CRAWLING_PAGES))
        self.complete = False if new_found >= self.MIN_ALLOWED_UNRECORD_NEWS_TO_CONTINUE_CRAWLING else True

    def crawl(self):
        source_name = self.source_db.get_source_name_by_id(self.SOURCE_ID)
        self.logger.info("==========================  Crawler [%s] started  ==========================" % source_name)
        self.goto_main_page()
        self.complete = False
        for i in range(self.MAX_CRAWLING_PAGES):
            try:
                self.process_current_page()
            except Exception as e:
                self.logger.warning("%s" % e)
                self.logger.warning("Error when crawling page [%d/%d], skipping the page......" %
                                    (self.current_page_number, self.MAX_CRAWLING_PAGES))
            if self.complete or i == self.MAX_CRAWLING_PAGES - 1:
                break
            self.goto_next_page()
        self.logger.info("===========  Crawler [%s] completed in [%s] found [%s/%s] new records  ===========\n" %
                         (source_name, str(datetime.now() - self.start_time), self.total_found, self.total_checked))


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
