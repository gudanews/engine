from database.headline import HeadlineDB
from util import checksimilarity
from util.webdriver_util import ChromeDriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import string
from database.headline import HeadlineDB
import logging

import random
from database.news import NewsDB
from datetime import datetime


DEBUGGING_TEST = False

START_TIME = datetime.now()
logger = logging.getLogger("Crawler")


class Processor:
    def __init__(self, driver=None, headline_id=0):
        self.driver = driver
        self.headline_id = headline_id

    def process(self):
        raise NotImplementedError("Please define <process> method")


def main():
    import os
    from util import find_modules, find_public_classes
    from processor import Processor
    logger.info("=" * 40)
    logger.info("Started Crawling ......")
    logger.info("=" * 40 + "\n")
    found = 0
    modules = find_modules(os.path.dirname(__file__))
    for module in modules:
        classes = find_public_classes(module)
        for _,cls in classes.items():
            if issubclass(cls, Processor) and not issubclass(Processor, cls):
                try:
                    driver = ChromeDriver()
                    obj = cls(driver, headline_id)
                    obj.crawl()
                    found += obj.total_found
                    driver.close()
                except:
                    cls.logger.warning("Error happens to current crawler, continuing......")
    logger.info(">" * 40 + "<" * 40)
    logger.info(">>> Completed Crawling. Processing Time [%s]. Total Found [%d]. <<<"
                % (str(datetime.now() - START_TIME), found))
    logger.info(">" * 40 + "<" * 40 + "\n" * 2)

if __name__ == "__main__":

    def get_random_string(length):
        import string
        import random
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str


    def create_test(li):
        db = HeadlineDB()
        for a in li:
            db.insert_db_record(dict(heading=a))


    li = []
    for i in range(40):
        li.append(get_random_string(1))
    create_test(li)
    cd = Proccessor()
    cd.process_duplicates()
