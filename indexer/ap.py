from indexer import Indexer as BaseIndexer
from util.webdriver_util import ChromeDriver
from webpage.ap import IndexPage as APPage
import logging
from furl import furl
import re


class _APIndexer(BaseIndexer):

    MAX_CRAWLING_PAGES = 1
    SOURCE_ID = 2
    logger = logging.getLogger("Crawler.AP")

    def __init__(self, driver):
        page = APPage(driver)
        super(_APIndexer, self).__init__(driver, page)


if __name__ == "__main__":
    driver = ChromeDriver()
    indexer = _APIndexer(driver)
    indexer.index()
    driver.close()
