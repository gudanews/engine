from indexer import Indexer as BaseIndexer
from util.webdriver_util import ChromeDriver
from webpage.ap import IndexPage as APPage
import logging


class APIndexer(BaseIndexer):

    SOURCE_ID = 2
    logger = logging.getLogger("Indexer.AP")
    MAX_RECORD_COUNT = 3

    def __init__(self, driver):
        page = APPage(driver)
        super(APIndexer, self).__init__(driver, page)


if __name__ == "__main__":
    driver = ChromeDriver(light_version=False)
    indexer = APIndexer(driver)
    indexer.index()
    driver.close()
