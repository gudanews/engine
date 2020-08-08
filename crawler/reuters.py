from crawler import Crawler as BaseCrawler
from util.webdriver_util import ChromeDriver
from webpage.reuters import CrawlPage as ReutersPage
import logging
from furl import furl
import time


class ReutersCrawler(BaseCrawler):

    MAX_CRAWLING_PAGES = 5
    MIN_ALLOWED_UNRECORD_NEWS_TO_CONTINUE_CRAWLING = 0
    WAIT_FOR_ELEMENT_READY = 2.0
    SOURCE_ID = 1
    logger = logging.getLogger("Crawler.REU")

    def __init__(self, driver):
        web_url = "https://www.reuters.com/theWire"
        page = ReutersPage(driver)
        super(ReutersCrawler, self).__init__(driver, page, web_url)

    def find_alternative_image_url(self, url):
        # Expected https://s4.reutersmedia.net/resources/r/?m=02&d=20200728&t=2&i=1527461013&w=370&fh=&fw=&ll=&pl=&sq=&r=LYNXNPEG6R1MZ
        # Alternative https://s4.reutersmedia.net/resources/r/?m=02&d=20200728&t=2&i=1527461013&w=800&fh=&fw=&ll=&pl=&sq=&r=LYNXNPEG6R1MZ
        f = furl(url)
        if "w" in f.args.keys():
            f.args["w"] = "800"
        return f.url

    def goto_next_page(self):  # goes to next page
        self.current_page_number += 1
        web_url = "https://www.reuters.com/news/archive/us-the-wire?view=page&page=%d&pageSize=20" % self.current_page_number
        self.driver.get(web_url)
        self.logger.info("Go To Page [%s/%s]......\n" % (self.current_page_number, self.MAX_CRAWLING_PAGES))
        time.sleep(self.WAIT_FOR_PAGE_READY)

if __name__ == "__main__":
    driver = ChromeDriver()
    crawler = ReutersCrawler(driver)
    crawler.crawl()
    driver.close()

