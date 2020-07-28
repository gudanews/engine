from crawler import Crawler as BaseCrawler
from util.webdriver_util import ChromeDriver
from webpage.americanpress import APPage
import logging


class _APCrawler(BaseCrawler):

    MAX_CRAWLING_PAGES = 1
    SOURCE_ID = 2
    logger = logging.getLogger("Crawler.AP")

    def __init__(self, driver):
        web_url = "https://www.americanpress.com/news/"
        page = APPage(driver)
        super(_APCrawler, self).__init__(driver, web_url, page)

    def goto_next_page(self):  # AP news only checks one page
        raise Exception("American Press News Should Only Be Crawled On Home Page")


if __name__ == "__main__":
    driver = ChromeDriver()
    crawler = _APCrawler(driver)
    crawler.crawl()
