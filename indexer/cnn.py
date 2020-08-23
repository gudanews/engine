from indexer import Indexer as BaseIndexer
from util.webdriver_util import ChromeDriver
from webpage.cnn import IndexPage as CNNPage
import logging


class CNNIndexer(BaseIndexer):

    SOURCE_ID = 101
    logger = logging.getLogger("Indexer.CNN")

    def __init__(self, driver):
        page = CNNPage(driver)
        super(CNNIndexer, self).__init__(driver, page)


if __name__ == "__main__":
    driver = ChromeDriver()
    indexer = CNNIndexer(driver)
    indexer.index()
    driver.close()
