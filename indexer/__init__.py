from webpage.cnn import IndexPage as CNNPage
from util.webdriver_util import ChromeDriver
from datetime import datetime
import logging


DEBUGGING_TEST = False

START_TIME = datetime.now()
logger = logging.getLogger("Indexer")


class Indexer:

    def __init__(self, driver, page):
        self.driver = driver
        self.page = page
        self._news = []

    def go_to_page(self, url):
        self.driver.get(url)

    def get_candidates(self):
        raise NotImplementedError("Please Implement method <get_candidates> to use Indexer")

    def get_heading(self):
        print(self.page.news.heading)


def main():
    import os
    from util import find_modules, find_public_classes
    from crawler import Crawler
    logger.info("=" * 40)
    logger.info("Started Indexing ......")
    logger.info("=" * 40 + "\n")
    found = 0
    modules = find_modules(os.path.dirname(__file__))
    for module in modules:
        classes = find_public_classes(module)
        for _,cls in classes.items():
            if issubclass(cls, Crawler) and not issubclass(Crawler, cls):
                try:
                    driver = ChromeDriver()
                    obj = cls(driver)
                    obj.crawl()
                    found += obj.total_found
                    driver.close()
                except Exception as e:
                    cls.logger.warning("%s" % e)
                    cls.logger.warning("Error happens to current crawler, continuing......")
    logger.info(">" * 40 + "<" * 40)
    logger.info(">>> Completed Crawling. Processing Time [%s]. Total Found [%d]. <<<"
                % (str(datetime.now() - START_TIME), found))
    logger.info(">" * 40 + "<" * 40 + "\n" * 2)



driver = ChromeDriver()
page = CNNPage(driver)
pp = Indexer(rp, driver)
pp.go_to_page('https://www.cnn.com/2020/08/05/politics/biden-milwaukee-dnc/index.html')
pp.get_heading()
print(pp.get_body())

