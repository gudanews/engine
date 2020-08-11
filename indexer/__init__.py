from webpage.reuters import IndexPage as ReutersPage
from util.webdriver_util import ChromeDriver
from database.headline import HeadlineDB
from database.image import ImageDB
from database.news import NewsDB
from database.source import SourceDB
from util.image_util import ImageHelper
from datetime import datetime
import logging
import time


DEBUGGING_TEST = False

START_TIME = datetime.now()
logger = logging.getLogger("Indexer")


class Indexer:

    WAIT_FOR_PAGE_READY = 2.0
    logger = logging.getLogger("Indexer")

    def __init__(self, driver, page):
        self.driver = driver
        self.page = page
        self._indexing_news = []
        self.news_db = NewsDB()
        self.headline_db = HeadlineDB()

    def go_to_page(self, url):
        self.driver.get(url)
        time.sleep(self.WAIT_FOR_PAGE_READY)

    def get_candidates(self):
        return self.news_db.get_non_indexed_news_by_source(source = 1, max_count=50)
        # raise NotImplementedError("Please Implement method <get_candidates> to use Indexer")

    def process_current_page(self):
        element = self.page
        record = dict()
        for el in ("category", "heading", "datetime", "image", "body", "media", "contributor", "length"):  # No need to insert url again
            if el in dir(element):
                record[el] = eval("element." + el)
                if not record[el]:
                    record.pop(el)
                    self.logger.info("Cannot find [%s]" % el.upper())
                else:
                    self.logger.info("[%s]:\t%s" % (el.upper(), record[el]))

    def index(self):
        self._indexing_news = self.get_candidates()
        for (id, url) in self._indexing_news:
            self.go_to_page(url)
            self.logger.info("LOADING PAGE [%s]" % url)
            self.process_current_page()

def main():
    import os
    from util import find_modules, find_public_classes
    from crawler import Crawler
    logger.info("=" * 40)
    logger.info("Started Indexing ......")
    logger.info("=" * 40 + "\n")
    modules = find_modules(os.path.dirname(__file__))
    for module in modules:
        classes = find_public_classes(module)
        for _,cls in classes.items():
            if issubclass(cls, Crawler) and not issubclass(Crawler, cls):
                try:
                    driver = ChromeDriver()
                    obj = cls(driver)
                    obj.index()
                    driver.close()
                except Exception as e:
                    cls.logger.warning("%s" % e)
                    cls.logger.warning("Error happens to current indexer, continuing......")
    logger.info(">" * 40 + "<" * 40)
    logger.info(">>> Completed Indexing. Processing Time [%s]. <<<"
                % str(datetime.now() - START_TIME))
    logger.info(">" * 40 + "<" * 40 + "\n" * 2)


if __name__ == "__main__":
    driver = ChromeDriver()
    page = ReutersPage(driver)
    obj = Indexer(driver=driver, page=page)
    obj.index()
    driver.close()
