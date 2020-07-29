from crawler import Crawler as BaseCrawler
from util.webdriver_util import ChromeDriver
from webpage.fox_news import FoxNewsPage
import logging
from furl import furl
from util.image_util import IMAGE_HEIGHT, IMAGE_WIDTH
import re


class FoxCrawler(BaseCrawler):

    MAX_CRAWLING_PAGES = 1
    SOURCE_ID = 104
    logger = logging.getLogger("Crawler.Fox")

    def __init__(self, driver):
        web_url = "https://www.foxnews.com"
        page = FoxNewsPage(driver)
        super(FoxCrawler, self).__init__(driver, web_url, page)

    def goto_next_page(self):  # Fox news only checks one page
        raise Exception("Fox News Should Only Be Crawled On Home Page")

    def find_alternative_image_url(self, url):
        # Expected https://a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2020/07/640/360/jasmine-Daniels-.jpg?tl=1&ve=1
        # Alternative https://a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2020/07/780/538/jasmine-Daniels-.jpg?tl=1&ve=1
        f = furl(url)
        width = f.path.segments[-3]
        height = f.path.segments[-2]
        f.path.segments[-3:-1] = (IMAGE_WIDTH, IMAGE_HEIGHT) if re.search(r"^\d{3,4}$", width) \
                and re.search(r"^\d{3,4}$", height) else (width, height)
        return f.url


if __name__ == "__main__":
    driver = ChromeDriver()
    crawler = FoxCrawler(driver)
    crawler.crawl()
    driver.close()
