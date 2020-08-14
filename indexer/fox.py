from indexer import Indexer as BaseIndexer
from util.webdriver_util import ChromeDriver
from webpage.fox import IndexPage as FoxPage
import logging
from furl import furl
import re


class FoxIndexer(BaseIndexer):

    MAX_CRAWLING_PAGES = 1
    SOURCE_ID = 104
    logger = logging.getLogger("Crawler.Fox")

    def __init__(self, driver):
        page = FoxPage(driver)
        super(FoxIndexer, self).__init__(driver, page)


if __name__ == "__main__":
    driver = ChromeDriver()
    indexer = FoxIndexer(driver)
    indexer.index()
    driver.close()
