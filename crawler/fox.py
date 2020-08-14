from crawler import Crawler as BaseCrawler
from util.webdriver_util import ChromeDriver
from webpage.fox import CrawlPage as FoxPage
import logging


class FoxCrawler(BaseCrawler):

    MAX_CRAWLING_PAGES = 1
    SOURCE_ID = 104
    logger = logging.getLogger("Crawler.Fox")

    def __init__(self, driver):
        web_url = "https://www.foxnews.com"
        page = FoxPage(driver)
        super(FoxCrawler, self).__init__(driver, page, web_url)

    def goto_next_page(self):  # Fox news only checks one page
        raise Exception("Fox News Should Only Be Crawled On Home Page")

    def is_valid_record(self, record):
        if record.get("category", None) == "ads":
            return False
        return super(FoxCrawler, self).is_valid_record(record)



if __name__ == "__main__":
    driver = ChromeDriver()
    crawler = FoxCrawler(driver)
    crawler.crawl()
    driver.close()
