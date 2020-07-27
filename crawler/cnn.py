from crawler import Crawler as BaseCrawler
from util.webdriver_util import ChromeDriver
from webpage.cnn import CNNPage
import logging

logger = logging.getLogger("Crawler.CNN")


class _CNNCrawler(BaseCrawler):

    MAX_CRAWLING_PAGES = 1
    SOURCE_ID = 101
    logger = logging.getLogger("Crawler.CNN")

    def __init__(self, driver):
        web_url = "https://www.cnn.com/search?q=cnn"
        page = CNNPage(driver)
        super(_CNNCrawler, self).__init__(driver, web_url, page)

    def goto_next_page(self):  # CNN news only checks one page
        raise Exception("CNN news should only be crawled on home page")


if __name__ == "__main__":
    driver = ChromeDriver()
    crawler = _CNNCrawler(driver)
    crawler.crawl()