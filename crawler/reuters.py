import unittest
from util.mysql_util import NewsHeadlineTableAction
from util import datetime_util
from util import scroll_down
from holmium.core import Element, Locators, Sections
from holmium.core import Page
from crawler import Crawler as BaseCrawler
from datetime import datetime, timedelta

class Story(Sections):
    heading = Element(
        Locators.CSS_SELECTOR,
        "div.story-content h3.story-title",
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
        "div.story-photo img[src]",
        value=lambda el: el.get_attribute('src'),
        timeout=5
    )

class ReutersPage(Page):
    news = Story(
        Locators.CSS_SELECTOR,
        "article.story",
        timeout=10
    )

class ReutersCrawler(BaseCrawler):

    def __init__(self, driver):
        super(ReutersCrawler, self).__init__(driver)

    def goto_website(self):  # goes to reuters
        self.driver.get('https://www.reuters.com/theWire')
        self.page = ReutersPage(self.driver)
        self.story_contents = []
        scroll_down(self.driver)

    def insert_records(self):
        columns = ["heading", "datetime"]
        conditions = ["datetime BETWEEN '%(yesterday)s' and '%(today)s'" %
                      {'yesterday': datetime.strftime(datetime.now() - timedelta(hours=36), "%Y-%m-%d %H:%M:%S"),
                       'today': datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")}]
        db = NewsHeadlineTableAction()
        existing_data = db.fetch_db_record(column=columns, condition=conditions)
        for n in self.page.news:
            if not (n.heading,datetime_util.str2datetime(n.time)) in existing_data:
                record = dict(heading=n.heading, datetime=datetime_util.str2datetime(n.time), source_id=1, link=n.url,snippet=n.snippet,image=n.image)
                db.insert_db_record(record=record)

