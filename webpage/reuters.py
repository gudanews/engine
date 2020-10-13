from holmium.core import Element, Elements, Locators, Section, Sections
from holmium.core import Page
from holmium.core.conditions import VISIBLE
from util import datetime_util
from furl import furl
from database.category import category_mapping
from webpage import WAIT_FOR_ELEMENT_TIMEOUT, WAIT_FOR_SECTION_TIMEOUT, WAIT_FOR_MINIMUM_TIMEOUT, WAIT_FOR_PAGE_LOADING
import time
import re


# JULY 31, 2020 / 4:03 AM / 8 DAYS AGO
DATETIME_PATTERN = r'^(?P<month>%s) (?P<day>\d{1,2})(\,{0,1}) (?P<year>\d{2,4})(( \/ ){0,1})(?P<hour>\d{1,2}):(?P<minute>\d{2}) (?P<period>AM|PM)' % datetime_util.ANY_MONTHS

def create_image_urls(url):
    # Expected https://s4.reutersmedia.net/resources/r/?m=02&d=20200728&t=2&i=1527461013&w=370&fh=&fw=&ll=&pl=&sq=&r=LYNXNPEG6R1MZ
    # Full image URL https://s4.reutersmedia.net/resources/r/?m=02&d=20200728&t=2&i=1527461013&w=800&r=LYNXNPEG6R1MZ
    # Normalized URL https://s4.reutersmedia.net/resources/r/?m=02&d=20200728&t=2&i=1527461013&w=800&r=LYNXNPEG6R1MZ
    if url:
        f = furl(url)
        if any(s in f.host for s in ("reutersmedia.net", "static.reuters.com")):
            parameters = dict(f.args)
            parameters["w"] = "800"
            keys = sorted(parameters.keys())
            f.args = None
            for k in keys:
                if parameters[k]:
                    f.args[k] = parameters[k]
            return [f.url, url]
        return [url]
    return None

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
                return create_image_urls(image)
        return None


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

    HEADER_CSS_SELECTOR = "div[class*='ArticlePage-article-header'] "
    BODY_CSS_SELECTOR = "article[class*='ArticlePage-article-body'] "
    LIGHTBOX_CSS_SELECTOR = "div[class*='Slideshow-overlay'] "

    category_raw = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "a[class*='ArticleHeader-channel']",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    title = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "h1[class*='Headline-headline']",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    datetime_raw = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "div[class*='ArticleHeader-date']",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    image_expand_button = Element(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + "div[class*='Slideshow-expand-button']",
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    image_close_button = Element(
        Locators.CSS_SELECTOR,
        LIGHTBOX_CSS_SELECTOR + "button[class*='Slideshow-close-button']",
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    image_thumbnail_list = Element(
        Locators.CSS_SELECTOR,
        LIGHTBOX_CSS_SELECTOR + "div[class*='ThumbnailList-thumbnail-list']",
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    images_raw = Elements(
        Locators.CSS_SELECTOR,
        LIGHTBOX_CSS_SELECTOR + "nav div[class*='Thumbnail-image'][role='img']",
        value=lambda el: el.get_attribute('style'),
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    media_raw = Elements(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + "div[class*='VideoPlayer__video'] iframe[src]",
        value=lambda el: el.get_attribute('src'),
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    content_raw = Elements(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + "p[class*='Paragraph-paragraph']",
        value=lambda el:el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    author_raw = Element(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + "[class*='Byline-byline']",
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
    def author(self):
        author = self.author_raw
        if author and author.startswith("By "):
            return author[3:]

    @property
    def content(self):
        return "\n".join([b for b in self.content_raw])

    @property
    def media(self):
        return [m for m in self.media_raw]

    @property
    def images(self):
        all_images = []
        if self.image_expand_button:
            self.image_expand_button.click()
            time.sleep(WAIT_FOR_PAGE_LOADING)
            try:
                self.image_thumbnail_list.hover()
                time.sleep(WAIT_FOR_MINIMUM_TIMEOUT)
            except:
                pass
        images = self.images_raw
        for img in images:
            img = re.sub(r'background-image: url', '', img)
            img = img.strip("()\;\"'")
            urls = create_image_urls(img)
            if urls and not urls in all_images:
                all_images.append(urls)
        if self.image_close_button:
            self.image_close_button.click()
        return all_images
