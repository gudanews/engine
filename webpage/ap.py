from holmium.core import Element, Elements, Locators, Section, Sections, Page
from holmium.core.conditions import VISIBLE
from util import datetime_util
from furl import furl
from database.category import category_mapping
from webpage import WAIT_FOR_ELEMENT_TIMEOUT, WAIT_FOR_SECTION_TIMEOUT, WAIT_FOR_MINIMUM_TIMEOUT
import re


def get_full_image_url(url):
    # Expected https://storage.googleapis.com/afs-prod/media/8814cee91eef4fce825bfc90e6ddccf8/400.jpeg
    # Image Full https://storage.googleapis.com/afs-prod/media/8814cee91eef4fce825bfc90e6ddccf8/800.jpeg
    if url:
        f = furl(url)
        pixel = f.path.segments[-1]
        f.path.segments[-1] = "800.jpeg" if re.search(r"^\d{3,4}.jpeg", pixel) else pixel
        return f.url
    return url

class Cards(Sections):

    title = Element(
        Locators.CSS_SELECTOR,
        "div.CardHeadline [data-key='card-headline']",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    datetime_raw = Element(
        Locators.CSS_SELECTOR,
        "div.CardHeadline span.Timestamp",
        value=lambda el: el.get_attribute("data-source"),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    url = Element(
        Locators.CSS_SELECTOR,
        "a[class*='Component']",
        value=lambda el: el.get_attribute("href"),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    snippet = Element(
        Locators.CSS_SELECTOR,
        "a div.content",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    image = Element(
        Locators.CSS_SELECTOR,
        "a img",
        value=lambda el: el.get_attribute("src"),
        only_if=VISIBLE(),
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    author_raw = Element(
        Locators.CSS_SELECTOR,
        "div.CardHeadline span[class*='Component-bylines']",
        value=lambda el: el.text,
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    category_raw = Element(
        Locators.CSS_SELECTOR,
        "div.CardHeadline a.HubTag",
        value=lambda el: el.text,
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    @property
    def datetime_created(self):
        return datetime_util.str2datetime(self.datetime_raw)

    @property
    def image_full(self):
        return get_full_image_url(self.image)

    @property
    def author(self):
        author = self.author_raw
        return author[3:] if author and author.startswith("By ") else author

    @property
    def category(self):
        return category_mapping(self.category_raw)


class CrawlPage(Page):
    news = Cards(
        Locators.CSS_SELECTOR,
        "article div.FeedCard[class*='Component-wireStory']",
        timeout=WAIT_FOR_SECTION_TIMEOUT
    )

# JULY 31, 2020 / 4:03 AM / 8 DAYS AGO
DATETIME_PATTERN = r'^(?P<month>%s) (?P<day>\d{1,2})(\,{0,1}) (?P<year>\d{2,4}) / (?P<hour>\d{1,2}):(?P<minute>\d{2}) (?P<period>AM|PM)' % datetime_util.ANY_MONTHS

class IndexPage(Page):

    BASE_CSS_SELECTOR = "div.Body div.Content "
    HEADER_CSS_SELECTOR = BASE_CSS_SELECTOR + "div.CardHeadline "

    title = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "div[data-key='card-headline'] h1",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    author = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "span[class*='Component-bylines']",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    datetime_raw = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "span[data-key='timestamp']",
        value=lambda el: el.get_attribute('data-source'),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    image_open = Element(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + "a.LeadFeature",
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    image_raw = Elements(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + "div[data-key='media-placeholder'] img",
        value=lambda el: el.get_attribute('src'),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    image_close = Element(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + "div[class*='imageModal'] svg[class*='close']",
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    content_raw = Elements(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + "div.Article p[class*='Component-root']",
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )

    @property
    def datetime(self):
        return datetime_util.str2datetime(self.datetime_raw)

    @property
    def image(self):
        if self.image_open:
            self.image_open.click()
            images = self.image_raw
            self.image_close.click()
        return images

    @property
    def content(self):
        return "\n".join(self.content_raw)
