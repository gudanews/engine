from holmium.core import Element, Elements, Locators, Sections
from holmium.core import Page
from holmium.core.conditions import VISIBLE
from util import datetime_util
from furl import furl
from database.category import category_mapping
from webpage import WAIT_FOR_ELEMENT_TIMEOUT, WAIT_FOR_SECTION_TIMEOUT, WAIT_FOR_MINIMUM_TIMEOUT
import re


# Updated 11:48 AM ET, Sat August 8, 2020
DATETIME_PATTERN = r'.* (?P<hour>\d{1,2}):(?P<minute>\d{2}) (?P<period>AM|PM) (?P<zone>%s)(\,{0,1}) (%s) (?P<month>%s) (?P<day>\d{1,2})(\,{0,1}) (?P<year>\d{2,4})$' % (datetime_util.ANY_TIMEZONE, datetime_util.ANY_WEEK_DAYS_3L, datetime_util.ANY_MONTHS)

def create_image_urls(url):
    # Expected cdn.cnn.com/cnnnext/dam/assets/200806183042-02-trump-0806-full-169.jpg
    # Full Image URL cdn.cnn.com/cnnnext/dam/assets/200806183042-02-trump-0806.jpg
    # Normalized Image URL cdn.cnn.com/cnnnext/dam/assets/200806183042-02-trump-0806.jpg
    if url:
        m = re.match(r'(.*)\-full\-\d{2,4}.jpg$', url, re.IGNORECASE)
        if m:
            return [m.group(1) + ".jpg", url]
        return [url]
    return None

class News(Sections):

    title = Element(
        Locators.CSS_SELECTOR,
        "h3 a span.cd__headline-text",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    url = Element(
        Locators.CSS_SELECTOR,
        "h3 a[href]",
        value=lambda el: el.get_attribute('href'),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    image_raw = Element(
        Locators.CSS_SELECTOR,
        "div.media a img",
        value=lambda el: el.get_attribute('data-src-full16x9'),
        only_if=VISIBLE(),
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    category_raw = Element(
        Locators.XPATH,
        "../article",
        value=lambda el: el.get_attribute('data-section-name'),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    @property
    def image(self):
        image = self.image_raw
        if image and image.startswith("//"):
            image = "https:" + image
        return create_image_urls(image)

    @property
    def category(self):
        return category_mapping(self.category_raw)


class CrawlPage(Page):
    news = News(
        Locators.CSS_SELECTOR,
        "section.zn-has-multiple-containers article.cd--article",
        timeout=WAIT_FOR_SECTION_TIMEOUT
    )


class IndexPage(Page):

    BASE_CSS_SELECTOR = "article.pg-rail-tall "
    MAIN_CSS_SELECTOR = BASE_CSS_SELECTOR + "div.pg-side-of-rail "

    category_raw = Element(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + "meta[itemprop='articleSection']",
        value=lambda el: el.get_attribute("content"),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    title = Element(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + "h1.pg-headline",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    author_raw = Elements(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + "p.metadata__byline span",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    datetime_raw = Element(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + "div.metadata p.update-time",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    image_raw = Element(
        Locators.CSS_SELECTOR,
        MAIN_CSS_SELECTOR + ".pg-rail-tall__head div.l-container img[data-src-full16x9]",
        value=lambda el: el.get_attribute("data-src-full16x9"),
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    content_raw = Elements(
        Locators.CSS_SELECTOR,
        MAIN_CSS_SELECTOR + ".pg-rail-tall__body .zn-body__paragraph",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )

    @property
    def category(self):
        return category_mapping(self.category_raw)

    @property
    def image(self):
        image = self.image_raw
        if image and image.startswith("//"):
            image = "https:" + image
        return create_image_urls(image)

    @property
    def author(self):
        author = self.author_raw
        if author:
            if author.lower().startswith("by "):
                return author[3:]
            elif author.lower().contains(" by "):
                return author.split(" by ")[-1]
        return None

    @property
    def datetime_created(self):
        return datetime_util.get_datetime_use_pattern(DATETIME_PATTERN, self.datetime_raw) if self.datetime_raw else None

    @property
    def content(self):
        return "\n".join(self.content_raw)