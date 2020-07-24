from util import datetime_util, image_util
from crawler import Crawler as BaseCrawler
from util.webdriver_util import Driver, scroll_down
from database.news_headline import NewsHeadlineDB
from database.image import ImageDB
from webpage.fox_news import FoxNewsPage

class _FoxCrawler(BaseCrawler):
    def __init__(self, driver):
        self.homepage = "https://www.reuters.com/news/archive/us-the-wire?view=page"
        super(_FoxCrawler, self).__init__(driver)

    def goto_homepage(self):
        self.driver.get(self.homepage)
        self.page = FoxNewsPage(self.driver)
        #scroll_down(self.driver)
        print(self.page.news.heading)
        for i in self.page.news:
            print(i.heading)

if __name__ == "__main__":
    driver = Driver().connect()
    crawler = _FoxCrawler(driver)
    crawler.crawl()