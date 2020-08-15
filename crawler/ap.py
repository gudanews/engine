from crawler import Crawler as BaseCrawler
from util.webdriver_util import ChromeDriver
from webpage.ap import CrawlPage as APPage
import logging
import time


class APCrawler(BaseCrawler):

    MAX_CRAWLING_PAGES = 2
    MIN_ALLOWED_UNRECORD_NEWS_TO_CONTINUE_CRAWLING = 0
    WAIT_FOR_ELEMENT_READY = 2.0
    WAIT_FOR_PAGE_READY = 5.0
    SOURCE_ID = 2
    logger = logging.getLogger("Crawler.AP")

    def __init__(self, driver):
        web_url = "https://apnews.com"
        page = APPage(driver)
        super(APCrawler, self).__init__(driver, page, web_url)

    def goto_next_page(self):  # AP news only checks home page and top news page
        self.current_page_number += 1
        web_url = "https://apnews.com/apf-topnews"
        self.driver.get(web_url)
        self.logger.info("Checking AP Top News......\n")
        time.sleep(self.WAIT_FOR_PAGE_READY)


if __name__ == "__main__":
    driver = ChromeDriver()
    crawler = APCrawler(driver)
    crawler.crawl()
    driver.close()

