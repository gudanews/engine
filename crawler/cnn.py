from crawler import Crawler as BaseCrawler
from util.webdriver_util import ChromeDriver
from webpage.cnn import CNNPage
import logging

logger = logging.getLogger("Crawler.CNN")


class _CNNCrawler(BaseCrawler):

    MIN_ALLOWED_UNRECORD_NEWS_TO_CONTINUE_CRAWLING = 0
    SOURCE_ID = 101
    logger = logging.getLogger("Crawler.CNN")

    def __init__(self, driver):
        web_url = "https://www.cnn.com/search?q=cnn"
        page = CNNPage(driver)
        super(_CNNCrawler, self).__init__(driver, web_url, page)

    def find_alternative_image_url(self, url):
        if url and url.endswith("-story-body.jpg"):
            url = "-exlarge-169".join(url.rsplit("-story-body", 1))
        return url


if __name__ == "__main__":
    driver = ChromeDriver()
    crawler = _CNNCrawler(driver)
    crawler.crawl()