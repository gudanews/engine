from crawler import Crawler as BaseCrawler
from util.webdriver_util import ChromeDriver
from webpage.reuters import ReutersPage
import logging
from furl import furl


class ReutersCrawler(BaseCrawler):

    SOURCE_ID = 1
    logger = logging.getLogger("Crawler.REU")

    def __init__(self, driver):
        web_url = "https://www.reuters.com/news/archive/us-the-wire?view=page"
        page = ReutersPage(driver)
        super(ReutersCrawler, self).__init__(driver, web_url, page)

    def find_alternative_image_url(self, url):
        f = furl(url)
        f.args["w"] = "1024"
        return f.url

if __name__ == "__main__":
    driver = ChromeDriver()
    crawler = ReutersCrawler(driver)
    crawler.crawl()
