from holmium.core import Element, Elements, ElementMap, Locators, Section, Sections
from holmium.core import Page
from holmium.core.conditions import VISIBLE
from util import datetime_util
from furl import furl
from database.category import category_mapping
from webpage import WAIT_FOR_ELEMENT_TIMEOUT, WAIT_FOR_SECTION_TIMEOUT, WAIT_FOR_MINIMUM_TIMEOUT


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
    image = Element(
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

    BASE_CSS_SELECTOR = "div.StandardArticle_inner-container "
    HEADER_CSS_SELECTOR = BASE_CSS_SELECTOR + "div.ArticleHeader_content-container "
    BODY_CSS_SELECTOR = BASE_CSS_SELECTOR + "div.StandardArticleBody_container "

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
    image_raw = Elements(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + "div.Image_container img, "
        + BODY_CSS_SELECTOR + "div.Slideshow_container img",
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
    length = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "p.BylineBar_reading-time",
        value=lambda el:el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    @property
    def datetime_created(self):
        return datetime_util.str2datetime(self.datetime_raw)

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
    def image(self):
        normalized_results = []
        results = []
        for img in self.image_raw:
            f = furl(img)
            f.args.pop("w", None)
            if not f.url in normalized_results: # Remove duplicate images.
                normalized_results.append(f.url)
                results.append(img)
        return results
