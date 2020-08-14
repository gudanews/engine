from indexer import Indexer as BaseIndexer
from util.webdriver_util import ChromeDriver
from webpage.reuters import IndexPage as ReutersPage
import logging
from furl import furl


class ReutersIndexer(BaseIndexer):

    SOURCE_ID = 1
    logger = logging.getLogger("Crawler.REU")

    def __init__(self, driver):
        page = ReutersPage(driver)
        super(ReutersIndexer, self).__init__(driver, page)


if __name__ == "__main__":
    driver = ChromeDriver()
    indexer = ReutersIndexer(driver)
    indexer.index()
    driver.close()
