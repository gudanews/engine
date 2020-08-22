from holmium.core import Element, Elements, Locators, Section, Sections
from holmium.core import Page
from holmium.core.conditions import VISIBLE
from util import datetime_util
from furl import furl
from database.category import category_mapping
from webpage import WAIT_FOR_ELEMENT_TIMEOUT, WAIT_FOR_SECTION_TIMEOUT, WAIT_FOR_MINIMUM_TIMEOUT, WAIT_FOR_PAGE_LOADING
import time


# JULY 31, 2020 / 4:03 AM / 8 DAYS AGO
DATETIME_PATTERN = r'^(?P<month>%s) (?P<day>\d{1,2})(\,{0,1}) (?P<year>\d{2,4}) / (?P<hour>\d{1,2}):(?P<minute>\d{2}) (?P<period>AM|PM)' % datetime_util.ANY_MONTHS

def get_full_image_url(url):
    # Expected https://s4.reutersmedia.net/resources/r/?m=02&d=20200728&t=2&i=1527461013&w=370&fh=&fw=&ll=&pl=&sq=&r=LYNXNPEG6R1MZ
    # Full image URL https://s4.reutersmedia.net/resources/r/?m=02&d=20200728&t=2&i=1527461013&w=800&r=LYNXNPEG6R1MZ
    if url:
        f = furl(url)
        if "reutersmedia.net" in f.host:
            parameters = dict(f.args)
            parameters["w"] = "800"
            keys = sorted(parameters.keys())
            f.args = None
            for k in keys:
                if parameters[k]:
                    f.args[k] = parameters[k]
            return f.url
    return url

class Stories(Sections):

    title = Element(
        Locators.CSS_SELECTOR,
        "div.story-content h3.story-title",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    datetime_raw = Element(
        Locators.CSS_SELECTOR,
        "div.story-content > time.article-time > span",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    url = Element(
        Locators.CSS_SELECTOR,
        "div.story-content > a[href]",
        value=lambda el: el.get_attribute('href'),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    snippet = Element(
        Locators.CSS_SELECTOR,
        "div.story-content > p",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    image_raw = Element(
        Locators.CSS_SELECTOR,
        "div.story-photo img[src]",
        value=lambda el: el.get_attribute('src'),
        only_if=VISIBLE(),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT,
    )
    @property
    def datetime_created(self):
        return datetime_util.str2datetime(self.datetime_raw)

    @property
    def image(self):
        # Invalid image urls:
        # https://s2.reutersmedia.net/resources_v2/images/core-placeholder-featured.png
        # https://s1.reutersmedia.net/resources_v2/images/1x1.png
        image = self.image_raw
        if image:
            f = furl(image)
            if not f.path.segments[-1] in ("1x1.png", "core-placeholder-featured.png"):
                return image
        return None

    @property
    def image_full(self):
        return get_full_image_url(self.image)


class CrawlPage(Page):
    news = Stories(
        Locators.CSS_SELECTOR,
        "div.column1 div.news-headline-list article.story",
        timeout=WAIT_FOR_SECTION_TIMEOUT
    )
    next = Element(
        Locators.CSS_SELECTOR,
        "div.control-nav a.control-nav-next",
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )


class IndexPage(Page):

    HEADER_CSS_SELECTOR = "div.ArticleHeader_container "
    BODY_CSS_SELECTOR = "div.StandardArticleBody_container "
    LIGHTBOX_CSS_SELECTOR = "div.Lightbox_container "

    category_raw = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "div.ArticleHeader_channel",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    title = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "h1.ArticleHeader_headline",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    datetime_raw = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "div.ArticleHeader_date",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    image_expand_button = Element(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + "div.Image_expand-button[role='button']",
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    image_close_button = Element(
        Locators.CSS_SELECTOR,
        LIGHTBOX_CSS_SELECTOR + "button.SlideshowLightbox_back-button, "
        + LIGHTBOX_CSS_SELECTOR + "button.SlideshowLightbox_close-button",
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    images_raw = Elements(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + "div.Image_container img, "
        + BODY_CSS_SELECTOR + "div.Graphic_container img, "
        + LIGHTBOX_CSS_SELECTOR + "div.Carousel_container img",
        value=lambda el: el.get_attribute('src'),
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    media_raw = Elements(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + "div.Video_container iframe[src]",
        value=lambda el: el.get_attribute('src'),
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    content_raw = Elements(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + "div.StandardArticleBody_body > p",
        value=lambda el:el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    author = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "div.BylineBar_byline, "
        + HEADER_CSS_SELECTOR + "Attribution_attribution > p",
        value=lambda el:el.text,
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    @property
    def datetime_created(self):
        return datetime_util.get_datetime_use_pattern(DATETIME_PATTERN, self.datetime_raw)

    @property
    def category(self):
        return category_mapping(self.category_raw)

    @property
    def content(self):
        return "\n".join([b for b in self.content_raw])

    @property
    def media(self):
        return [m for m in self.media_raw]

    @property
    def images(self):
        _images = []
        if self.image_expand_button:
            self.image_expand_button.click()
            time.sleep(WAIT_FOR_PAGE_LOADING)
        for image in self.images_raw:
            full_image = get_full_image_url(image)
            if not full_image in _images:
                _images.append(full_image)
        if self.image_close_button:
            self.image_close_button.click()
        return _images
