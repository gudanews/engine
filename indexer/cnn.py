from indexer import Indexer as BaseIndexer
from util.webdriver_util import ChromeDriver
from webpage.cnn import IndexPage as CNNPage
import logging


class _CNNIndexer(BaseIndexer):

    MAX_CRAWLING_PAGES = 1
    SOURCE_ID = 101
    logger = logging.getLogger("Crawler.CNN")

    def __init__(self, driver):
        page = CNNPage(driver)
        super(_CNNIndexer, self).__init__(driver, page)


if __name__ == "__main__":
    driver = ChromeDriver()
    indexer = _CNNIndexer(driver)
    indexer.index()
    driver.close()
