from holmium.core import Element, Elements, Locators, Section, Sections, Page
from holmium.core.conditions import VISIBLE
from util import datetime_util
from datetime import datetime


class Articles(Sections):
    heading = Element(
        Locators.CSS_SELECTOR,
        "div.info h2.title a",
        value=lambda el: el.text,
        timeout=5
    )
    datetime_raw = Element(
        Locators.CSS_SELECTOR,
        "div.info div.meta span.time",
        value=lambda el: el.get_attribute("data-time-published"),
        timeout=0.5
    )
    url = Element(
        Locators.CSS_SELECTOR,
        "div.info h2.title a",
        value=lambda el: el.get_attribute("href"),
        timeout=5
    )
    image = Element(
        Locators.CSS_SELECTOR,
        "div.m picture img[src]",
        value=lambda el: el.get_attribute("src"),
        only_if=VISIBLE(),
        timeout=5
    )
    @property
    def datetime(self):
        if not self.datetime_raw:
            return datetime.now()
        return datetime_util.str2datetime(self.datetime_raw)


class CrawlPage(Page):
    news = Articles(
        Locators.CSS_SELECTOR,
        "main.main-content div.collection article.article",
        timeout=10
    )


class IndexPage(Page):

    BASE_CSS_SELECTOR = "div.StandardArticle_inner-container"

    heading = Element(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + " h1.headline",
        value=lambda el: el.text,
        timeout=5
    )
    body = Elements(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + " div.StandardArticleBody_body > p",
        value=lambda el:el.text,
        timeout=5,
    )
