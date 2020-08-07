from holmium.core import Element, Elements, Locators, Section, Sections
from holmium.core import Page
from holmium.core.conditions import VISIBLE
from util import datetime_util


class Stories(Sections):
    heading = Element(
        Locators.CSS_SELECTOR,
        "div.story-content h3.story-title",
        value=lambda el: el.text,
        timeout=5
    )
    datetime_raw = Element(
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
        only_if=VISIBLE(),
        timeout=5,
    )
    @property
    def datetime(self):
        return datetime_util.str2datetime(self.datetime_raw)


class CrawlPage(Page):
    news = Stories(
        Locators.CSS_SELECTOR,
        "article.story:not(.no-border-bottom)",
        timeout=10
    )
    next = Element(
        Locators.CSS_SELECTOR,
        "div.control-nav a.control-nav-next",
        timeout=10
    )


class IndexPage(Page):

    BASE_CSS_SELECTOR = "div.StandardArticle_inner-container"
    HEADER_CSS_SELECTOR = BASE_CSS_SELECTOR + " div.ArticleHeader_content-container"
    BODY_CSS_SELECTOR = BASE_CSS_SELECTOR + " div.StandardArticleBody_container"

    category_raw = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + " div.ArticleHeader_channel",
        value=lambda el: el.text,
        timeout=5
    )
    heading = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + " h1.ArticleHeader_headline",
        value=lambda el: el.text,
        timeout=5
    )
    datetime_raw = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + " div.ArticleHeader_date",
        value=lambda el: el.text,
        timeout=5
    )
    image = Element(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + " div.Image_container img",
        value=lambda el: el.get_attribute('src'),
        timeout=5
    )
    body_raw = Elements(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + " div.StandardArticleBody_body > p",
        value=lambda el:el.text,
        timeout=5
    )
    contributor = Element(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + " Attribution_attribution > p",
        value=lambda el:el.text,
        timeout=5
    )
    length = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + " p.BylineBar_reading-time",
        value=lambda el:el.text,
        timeout=5
    )
    @property
    def datetime(self):
        return self.datetime_raw

    @property
    def category(self):
        return self.category_raw

    @property
    def body(self):
        return "\n".join([b for b in self.body_raw])
