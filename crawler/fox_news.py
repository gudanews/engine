from util.mysql_util import NewsHeadlineTableAction, ImageTableAction
from util import datetime_util, image_util
from holmium.core import Element, Locators, Section, Sections, Page
from holmium.core.conditions import VISIBLE
from crawler import Crawler as BaseCrawler
from util.webdriver_util import scroll_down
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

class Article(Sections):
    heading = Element(
        Locators.CSS_SELECTOR,
        "header.info-header h2.title a",
        value=lambda el: el.text,
        timeout=5
    )
    time = Element(
        Locators.CSS_SELECTOR,
        "div.story-content > time.article-time > span",
        value=lambda el: el.text,
        timeout=5
    )
    url = Element(
        Locators.CSS_SELECTOR,
        "div.story-content > a[href]",
        value=lambda el: el.get_attribute('href'),
        timeout=5
    )
    snippet = Element(
        Locators.CSS_SELECTOR,
        "div.story-content > p",
        value=lambda el: el.text,
        timeout=5
    )
    image = Element(
        Locators.CSS_SELECTOR,
        "div.m[picture[img]]",
        value=lambda el: el.get_attribute('src'),
        timeout=5
    )

class FoxPage(Page):
    news = Article(
        Locators.CSS_SELECTOR,
        "div.main article.article",
        timeout=10
    )
class FoxCrawler(BaseCrawler):
    def __init__(self, driver):
        super(FoxCrawler, self).__init__(driver)

    def goto_homepage(self):
        self.driver.get('https://www.foxnews.com/')
        self.page = FoxPage(self.driver)
        #scroll_down(self.driver)
        print(self.page.news.heading)
        for i in self.page.news:
            print(i.heading)

if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    fc = FoxCrawler(driver)
    fc.goto_website()