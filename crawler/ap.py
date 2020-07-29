from crawler import Crawler as BaseCrawler
from util.webdriver_util import ChromeDriver
from webpage.ap import APPage
import logging
from furl import furl
import re


class APCrawler(BaseCrawler):

    MAX_CRAWLING_PAGES = 1
    SOURCE_ID = 2
    logger = logging.getLogger("Crawler.AP")

    def __init__(self, driver):
        web_url = "https://apnews.com/apf-topnews"
        page = APPage(driver)
        super(APCrawler, self).__init__(driver, web_url, page)

    def goto_next_page(self):  # AP news only checks one page
        raise Exception("American Press News Should Only Be Crawled On Home Page")

    def find_alternative_image_url(self, url):
        # Expected https://storage.googleapis.com/afs-prod/media/8814cee91eef4fce825bfc90e6ddccf8/400.jpeg
        # Alternative https://storage.googleapis.com/afs-prod/media/8814cee91eef4fce825bfc90e6ddccf8/800.jpeg
        f = furl(url)
        pixel = f.path.segments[-1]
        f.path.segments[-1] = "800.jpeg" if re.search(r"^\d{3,4}.jpeg", pixel) else pixel
        return f.url

if __name__ == "__main__":
    driver = ChromeDriver()
    crawler = APCrawler(driver)
    crawler.crawl()
    driver.close()

