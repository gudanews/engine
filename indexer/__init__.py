from util.webdriver_util import ChromeDriver
from database.topic import TopicDB
from database.image import ImageDB
from database.news import NewsDB
from database.source import SourceDB
from datetime import datetime
import logging
import time


DEBUGGING_TEST = False

START_TIME = datetime.now()
logger = logging.getLogger("Indexer")


class Indexer:

    WAIT_FOR_PAGE_READY = 2.0
    SOURCE_ID = None
    logger = logging.getLogger("Indexer")

    def __init__(self, driver, page):
        self.driver = driver
        self.page = page
        self.indexing_news = []
        if not self.SOURCE_ID:
            raise NotImplementedError("Please Provide A Valid SOURCE_ID Before Proceed......")
        self.news_db = NewsDB()
        self.topic_db = TopicDB()
        self.source_db = SourceDB()
        self.image_db = ImageDB()
        self.start_time = datetime.now()

    def is_valid_news_url(self, url):
        return True
    
    def go_to_page(self, url):
        self.driver.get(url)
        time.sleep(self.WAIT_FOR_PAGE_READY)

    def get_candidates(self):
        return self.news_db.get_non_indexed_news_by_source_id(source_id = self.SOURCE_ID, max_count=1)
        # raise NotImplementedError("Please Implement method <get_candidates> to use Indexer")

    def process_current_page(self):
        element = self.page
        record = dict()
        for el in ("category", "title", "datetime_created", "image", "content", "media", "author"):  # No need to insert url again
            if el in dir(element):
                record[el] = eval("element." + el)
                if not record[el]:
                    record.pop(el)
                    self.logger.info("Cannot find [%s]" % el.upper())
                else:
                    self.logger.info("[%s]:\t%s" % (el.upper(), record[el]))

    def index(self):
        source_name = self.source_db.get_source_name_by_id(self.SOURCE_ID)
        self.logger.info("=====================  Indexing [%s] started  =====================" % source_name)

        self.indexing_news = self.get_candidates()
        for (id, url) in self.indexing_news:
            if self.is_valid_news_url(url):
                self.go_to_page(url)
                self.logger.info("LOADING PAGE [%s]" % url)
                self.process_current_page()

        self.logger.info("---------------------  Total New Records  ---------------------")
        self.logger.info("===========  Indexing [%s] completed in [%s]  ===========\n" %
                         (source_name, str(datetime.now() - self.start_time)))


def main():
    import os
    from util import find_modules, find_public_classes
    from indexer import Indexer
    logger.info("=" * 40)
    logger.info("Started Indexing ......")
    logger.info("=" * 40 + "\n")
    modules = find_modules(os.path.dirname(__file__))
    for module in modules:
        classes = find_public_classes(module)
        for _,cls in classes.items():
            if issubclass(cls, Indexer) and not issubclass(Indexer, cls):
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
    main()
