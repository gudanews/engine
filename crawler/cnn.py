from crawler import Crawler as BaseCrawler
from util.webdriver_util import ChromeDriver
from webpage.cnn import CrawlPage as CNNPage
import logging

logger = logging.getLogger("Crawler.CNN")


class CNNCrawler(BaseCrawler):

    MAX_CRAWLING_PAGES = 1
    WAIT_FOR_ELEMENT_READY = 0.2
    SOURCE_ID = 101
    logger = logging.getLogger("Crawler.CNN")

    def __init__(self, driver):
        web_url = "https://www.cnn.com"
        page = CNNPage(driver)
        super(CNNCrawler, self).__init__(driver, web_url, page)

    def goto_next_page(self):  # CNN news only checks one page
        raise Exception("CNN News Should Only Be Crawled On Home Page")


if __name__ == "__main__":
    driver = ChromeDriver()
    crawler = CNNCrawler(driver)
    crawler.crawl()
    driver.close()
