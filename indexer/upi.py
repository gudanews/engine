from indexer import Indexer as BaseIndexer
from util.webdriver_util import ChromeDriver
from webpage.upi import IndexPage as UPIPage
import logging


class UPIIndexer(BaseIndexer):

    SOURCE_ID = 3
    logger = logging.getLogger("Indexer.UPI")

    def __init__(self, driver):
        page = UPIPage(driver)
        super(UPIIndexer, self).__init__(driver, page)


if __name__ == "__main__":
    driver = ChromeDriver(light_version=False)
    indexer = UPIIndexer(driver)
    indexer.index()
    driver.close()
