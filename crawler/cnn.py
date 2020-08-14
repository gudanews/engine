from crawler import Crawler as BaseCrawler
from util.webdriver_util import ChromeDriver
from webpage.cnn import CrawlPage as CNNPage
import logging


logger = logging.getLogger("Crawler.CNN")


class CNNCrawler(BaseCrawler):

    MAX_CRAWLING_PAGES = 1
    WAIT_FOR_ELEMENT_READY = 0.5
    SOURCE_ID = 101
    logger = logging.getLogger("Crawler.CNN")

    def __init__(self, driver):
        web_url = "https://www.cnn.com"
        page = CNNPage(driver)
        super(CNNCrawler, self).__init__(driver, page, web_url)

    def goto_next_page(self):  # CNN news only checks one page
        raise Exception("CNN News Should Only Be Crawled On Home Page")

    # def is_valid_record(self, record):
    #     f = furl(record.get("url", None))
    #     if f.url and f.path.segments[0] == "videos":
    #         return False
    #     return super(CNNCrawler, self).is_valid_record(record)


if __name__ == "__main__":
    driver = ChromeDriver()
    crawler = CNNCrawler(driver)
    crawler.crawl()
    driver.close()
