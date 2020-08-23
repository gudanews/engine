from holmium.core import Element, Elements, ElementMap, Locators, Section, Sections
from holmium.core import Page
from holmium.core.conditions import VISIBLE
from util import datetime_util
from furl import furl
from database.category import category_mapping
from webpage import WAIT_FOR_ELEMENT_TIMEOUT, WAIT_FOR_SECTION_TIMEOUT, WAIT_FOR_MINIMUM_TIMEOUT
import time

# Aug. 21, 2020 / 2:59 PM
DATETIME_PATTERN = r'^(?P<month>%s)(\.{0,1})(\s|)(?P<day>\d{1,2})(\,{0,1})(\s|)(?P<year>\d{2,4})(\s|)/(\s|)(?P<hour>\d{1,2}):(?P<minute>\d{2})(\s|)(?P<period>AM|PM)' % datetime_util.ANY_MONTHS_3L

# Expected https://cdnph.upi.com/svc/sv/upi_com/3091597322027/2020/1/faba460183d5f0389d1582436ca9c5b1/British-officials-plan-to-block-migrants-after-10th-day-of-arrivals.jpg
# Full image URL None
# Normalized URL https://cdnph.upi.com/3091597322027/faba460183d5f0389d1582436ca9c5b1/British-officials-plan-to-block-migrants-after-10th-day-of-arrivals.jpg

def create_image_urls(url):
    if url:
        return [url]
    return None

def normalize_image_url(url):
    if url:
        f = furl(url)
        segments = list(f.path.segments)
        for seg in segments:
            if len(seg) < 10 or seg.isdigit():
                f.path.segments.remove(seg)
        return f.url
    return None

class Rows(Sections):

    title = Element(
        Locators.CSS_SELECTOR,
        "div.title",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    category_raw = Element(
        Locators.CSS_SELECTOR,
        "div.category > span",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    datetime_raw = Element(
        Locators.CSS_SELECTOR,
        "div.category > i.time-ago",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    url = Element(
        Locators.XPATH,
        "../a[@href]",
        value=lambda el: el.get_attribute('href'),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    snippet = Element(
        Locators.CSS_SELECTOR,
        "div.content",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    image_raw = Element(
        Locators.CSS_SELECTOR,
        "div > img[src]",
        value=lambda el: el.get_attribute('src'),
        only_if=VISIBLE(),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT,
    )
    @property
    def datetime_created(self):
        dt = self.datetime_raw
        if dt:
            if dt.startswith("// "):
                dt = dt[3:]
            return datetime_util.str2datetime(dt)
        return None

    @property
    def category(self):
        return category_mapping(self.category_raw)

    @property
    def image(self):
        image = self.image_raw
        return create_image_urls(image)


class CrawlPage(Page):
    news = Rows(
        Locators.CSS_SELECTOR,
        "div.sections-container a.row, div.sections-container a[class*=col-md]",
        timeout=WAIT_FOR_SECTION_TIMEOUT
    )
    navigation = ElementMap(
        Locators.CSS_SELECTOR,
        "tbody td.l a",
        key=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )

    @property
    def next(self):
        return self.navigation["Next"]


class IndexPage(Page):

    BASE_CSS_SELECTOR = "div.news-container "
    HEADER_CSS_SELECTOR = BASE_CSS_SELECTOR + "div.news-head "
    SLIDER_CSS_SELECTOR = BASE_CSS_SELECTOR + "div.upi-slider "
    BODY_CSS_SELECTOR = BASE_CSS_SELECTOR + "article[itemprop='articleBody'] "

    category_raw = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "div.breadcrumb a",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    datetime_raw = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "div.article-date",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    title = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "h1.headline",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    author = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "div.author div",
        value=lambda el: el.text,
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    images_raw = Elements(
        Locators.CSS_SELECTOR,
        SLIDER_CSS_SELECTOR + "div.slide",
        value=lambda el: el.get_attribute('data-url'),
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    content_expand = Element(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + "div[onclick] button",
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    content_raw = Elements(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + "p",
        value=lambda el:el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    media_raw = Elements(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + "div iframe[src]",
        value=lambda el: el.get_attribute('src'),
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )

    @property
    def category(self):
        return category_mapping(self.category_raw)

    @property
    def datetime_created(self):
        return datetime_util.get_datetime_use_pattern(DATETIME_PATTERN, self.datetime_raw)

    @property
    def images(self):
        images = self.images_raw
        all_images = []
        for img in images:
            f = furl(img)
            # Invalid image urls: /img/expand_gallery.svg
            if not f.path.segments[-1] in ("expand_gallery.svg"):
                urls = create_image_urls(img)
                if urls and not urls in all_images:
                    all_images.append(urls)
        return all_images

    @property
    def content(self):
        if self.content_expand:
            self.content_expand.scroll_to()
            time.sleep(WAIT_FOR_ELEMENT_TIMEOUT)
            self.content_expand.click()
            time.sleep(WAIT_FOR_MINIMUM_TIMEOUT)
        return "\n".join([b for b in self.content_raw])

    @property
    def media(self):
        return [m for m in self.media_raw]
