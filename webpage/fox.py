from holmium.core import Element, Elements, Locators, Section, Sections, Page
from holmium.core.conditions import VISIBLE
from util import datetime_util
from datetime import datetime
from furl import furl
from util.image_util import IMAGE_HEIGHT, IMAGE_WIDTH
from database.category import category_mapping
from webpage import WAIT_FOR_ELEMENT_TIMEOUT, WAIT_FOR_SECTION_TIMEOUT, WAIT_FOR_MINIMUM_TIMEOUT
import re


def create_image_urls(url):
    # Expected https://a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2020/07/640/360/jasmine-Daniels-.jpg?tl=1&ve=1
    # Full Image URL https://a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2020/07/648/365/jasmine-Daniels-.jpg
    # Normalized URL https://a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2020/07/648/365/jasmine-Daniels-.jpg
    if url:
        f = furl(url)
        f.args = None
        width, height = f.path.segments[-3:-1]
        if re.search(r"^\d{3,4}$", width) and re.search(r"^\d{3,4}$", height):
            f.path.segments[-3:-1] = (IMAGE_WIDTH, IMAGE_HEIGHT)
            return [f.url, url]
        return [url]
    return None

class Articles(Sections):

    title = Element(
        Locators.CSS_SELECTOR,
        "div.info h2.title a",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    datetime_raw = Element(
        Locators.CSS_SELECTOR,
        "div.info div.meta span.time",
        value=lambda el: el.get_attribute("data-time-published"),
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    url = Element(
        Locators.CSS_SELECTOR,
        "div.info h2.title a",
        value=lambda el: el.get_attribute("href"),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    image_raw = Element(
        Locators.CSS_SELECTOR,
        "div.m img[src]",
        value=lambda el: el.get_attribute("src"),
        only_if=VISIBLE(),
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    category_raw = Element(
        Locators.CSS_SELECTOR,
        "div.info div.meta a",
        value = lambda el: el.text,
        timeout = 0.5
    )
    @property
    def datetime_created(self):
        return datetime_util.str2datetime(self.datetime_raw)

    @property
    def image(self):
        image = self.image_raw
        return create_image_urls(image)

    @property
    def category(self):
        return category_mapping(self.category_raw)


class CrawlPage(Page):
    news = Articles(
        Locators.CSS_SELECTOR,
        "section.collection-section article.article, div.collection article.article",
        timeout=WAIT_FOR_SECTION_TIMEOUT
    )


class IndexPage(Page):

    BASE_CSS_SELECTOR = "main.main-content article "

    title = Element(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + "h1.headline",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    content_raw = Elements(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + "div.article-content > div.article-body > p",
        value=lambda el:el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    author_raw = Element(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + "div.author-byline > span",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    datetime_raw = Element(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + "div.article-date > time",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )

    @property
    def author(self):
        author = self.author_raw
        if author:
            m = re.match(r'By (.*)( \| Fox News)', author)
            if m:
                return m.group(1)
        return None

    @property
    def datetime_created(self):
        return datetime_util.str2datetime(self.datetime_raw)

    @property
    def content(self):
        return "\n".join(self.content_raw)
