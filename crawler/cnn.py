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

    def find_alternative_image_url(self, url):
        # Expected //cdn.cnn.com/cnnnext/dam/assets/200806183042-02-trump-0806-full-169.jpg
        # Alternative cdn.cnn.com/cnnnext/dam/assets/200806183042-02-trump-0806-full-169.jpg
        return "http:" + url if url.startswith("//") else url


if __name__ == "__main__":
    driver = ChromeDriver()
    crawler = CNNCrawler(driver)
    crawler.crawl()
    driver.close()
