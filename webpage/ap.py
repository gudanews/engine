from holmium.core import Element, Elements, Locators, Section, Sections, Page
from holmium.core.conditions import VISIBLE
from util import datetime_util
from furl import furl
from database.category import category_mapping
from webpage import WAIT_FOR_ELEMENT_TIMEOUT, WAIT_FOR_SECTION_TIMEOUT, WAIT_FOR_MINIMUM_TIMEOUT, WAIT_FOR_PAGE_LOADING, WAIT_FOR_PAGE_POPUPS
import re
import time


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

    HEADER_CSS_SELECTOR = "div.Content > div.CardHeadline "
    GALLERY_CSS_SELECTOR = "div[class*='imageModal'] "
    BODY_CSS_SELECTOR = "div.Content > div.Article "

    popup = Element(
        Locators.CSS_SELECTOR,
        "div.tp-iframe-wrapper.tp-active",
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    close_popup = Element(
        Locators.CSS_SELECTOR,
        "button[class*='close']",
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    title = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "div[data-key='card-headline'] h1",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    author_raw = Element(
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
    category_raw = Elements(
        Locators.CSS_SELECTOR,
        "div.RelatedTopics li.tag",
        value=lambda el: el.text,
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    image_gallery_open = Element(
        Locators.CSS_SELECTOR,
        "svg.gallery-arrow",
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    image_gallery_next = Element(
        Locators.CSS_SELECTOR,
        GALLERY_CSS_SELECTOR + "svg[class*='right']",
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    images_raw = Elements(
        Locators.CSS_SELECTOR,
        GALLERY_CSS_SELECTOR + "div[class*='imagePlaceholder'] img, "
        + "div[data-key='media-placeholder'] img",
        value=lambda el: el.get_attribute('src'),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    image_gallery_close = Element(
        Locators.CSS_SELECTOR,
        GALLERY_CSS_SELECTOR + "svg[class*='close']",
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    content_raw = Elements(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + "p[class*='Component-root']",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )

    @property
    def datetime_created(self):
        return datetime_util.str2datetime(self.datetime_raw)

    @property
    def author(self):
        author = self.author_raw
        if author and author.startswith("By "):
            return author[3:]

    @property
    def categories(self):
        self.dismiss_popup(wait=False)
        _categories = []
        cat = self.category_raw
        if cat:
            for c in cat:
                category = category_mapping(c)
                if category and not category in _categories:
                    _categories.append(category)
        return _categories


    @property
    def images(self):
        self.dismiss_popup(wait=False)
        _images = []
        images = self.images_raw
        for img in images:
            image = get_full_image_url(img)
            if not image in _images:
                _images.append(image)
        if self.image_gallery_open:
            try:
                self.image_gallery_open.click()
                time.sleep(WAIT_FOR_PAGE_LOADING)
                clicks_remains = 20
                while clicks_remains > 0:
                    time.sleep(WAIT_FOR_MINIMUM_TIMEOUT)
                    images = self.images_raw
                    for img in images:
                        image = get_full_image_url(img)
                        if not image in _images:
                            _images.append(image)
                    if self.image_gallery_next:
                        clicks_remains -= 1
                        self.image_gallery_next.click()
                    else:
                        clicks_remains = 0
                self.image_gallery_close.click()
            except:
                pass
        return _images

    @property
    def content(self):
        return "\n".join(self.content_raw)

    def dismiss_popup(self, wait=True):
        if wait:
            time.sleep(WAIT_FOR_PAGE_POPUPS)
        if self.popup:
            try:
                self.driver.switch_to.frame(self.driver.find_element_by_css_selector("div.tp-modal iframe"))
                if self.close_popup:
                    self.close_popup.click()
            except:
                pass
            finally:
                self.driver.switch_to.default_content()