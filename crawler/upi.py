from crawler import Crawler as BaseCrawler
from util.webdriver_util import ChromeDriver
from webpage.upi import CrawlPage as UPIPage
import logging
import time


class UPICrawler(BaseCrawler):

    MAX_CRAWLING_PAGES = 5
    MIN_ALLOWED_UNRECORD_NEWS_TO_CONTINUE_CRAWLING = 0
    WAIT_FOR_ELEMENT_READY = 2.0
    WAIT_FOR_PAGE_READY = 5.0
    SOURCE_ID = 3
    logger = logging.getLogger("Crawler.UPI")

    def __init__(self, driver):
        web_url = "https://www.upi.com/Top_News"
        page = UPIPage(driver)
        super(UPICrawler, self).__init__(driver, page, web_url)

    def goto_next_page(self):  # goes to next page
        self.current_page_number += 1
        web_url = "https://www.upi.com/Top_News/p%s/" % self.current_page_number
        self.driver.get(web_url)
        self.logger.info("Go To Page [%s/%s]......\n" % (self.current_page_number, self.MAX_CRAWLING_PAGES))
        time.sleep(self.WAIT_FOR_PAGE_READY)


if __name__ == "__main__":
    driver = ChromeDriver()
    crawler = UPICrawler(driver)
    crawler.crawl()
    driver.close()

