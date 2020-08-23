from indexer import Indexer as BaseIndexer
from util.webdriver_util import ChromeDriver
from webpage.upi import IndexPage as UPIPage
from webpage.upi import normalize_image_url
import logging


class UPIIndexer(BaseIndexer):

    SOURCE_ID = 3
    logger = logging.getLogger("Indexer.UPI")

    def __init__(self, driver):
        page = UPIPage(driver)
        super(UPIIndexer, self).__init__(driver, page)

    def does_image_already_exist(self, images, existing_images):
        for img in images:
            if normalize_image_url(img) in [normalize_image_url(exist) for exist in existing_images]:
                return True
        return False

if __name__ == "__main__":
    driver = ChromeDriver(light_version=False)
    indexer = UPIIndexer(driver)
    indexer.index()
    driver.close()
