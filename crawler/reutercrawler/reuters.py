from util.mysql_util import NewsHeadlineTableAction, ImageTableAction
from util import datetime_util
from util import scroll_down
from holmium.core import Element, Locators, Sections
from holmium.core import Page
from crawler import Crawler as BaseCrawler
from datetime import datetime, timedelta
from util.images import download_image_from_url,find_image_path
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
        db_new_headline = NewsHeadlineTableAction()
        db_image = ImageTableAction()
        columns = ["heading", "url"]
        existing_data = db_new_headline.get_latest_news_headline(column=columns)
        for n in self.page.news:
            if not (n.heading, n.url) in existing_data:
                #image_id = db_image.get_image_id_by_url('url')
                #download_image_from_url(n.image,str(n.heading)+'.png')
                db_image.insert_db_record(record=dict(url=n.image,path=find_image_path(n.heading+'.png')))
                #if not image_id:
                #    db_image.insert_db_record(record=dict(url=n.image,path=???))
                record = dict(heading=n.heading, datetime=datetime_util.str2datetime(n.time), source_id=1, url=n.url,snippet=n.snippet)#,image_id=db_image.get_image_id_by_url(n.url)
                db_new_headline.insert_db_record(record=record)
