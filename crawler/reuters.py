from util.mysql_util import NewsHeadlineTableAction, ImageTableAction
from util import datetime_util, image_util
from util import scroll_down
from holmium.core import Element, Locators, Sections
from holmium.core import Page
from crawler import Crawler as BaseCrawler

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
        db_news_headline = NewsHeadlineTableAction()
        db_image = ImageTableAction()
        columns = ["heading", "url"]
        existing_data = db_news_headline.get_latest_news_headline(column=columns)
        for n in self.page.news:
            if not (n.heading, n.url) in existing_data:
                image_id = db_image.get_image_id_by_url(n.image)
                if not image_id:
                    image_file_path = image_util.save_image_from_url(n.image)
                    db_image.insert_db_record(record=dict(url=n.image, path=image_file_path))
                    image_id = db_image.get_image_id_by_url(n.image)
                record = dict(heading=n.heading, datetime=datetime_util.str2datetime(n.time), source_id=1,
                              image_id=image_id[0], url=n.url, snippet=n.snippet)
                db_news_headline.insert_db_record(record=record)
