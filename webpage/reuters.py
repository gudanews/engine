from holmium.core import Element, Elements, Locators, Section, Sections
from holmium.core import Page
from holmium.core.conditions import VISIBLE
from util import datetime_util
from furl import furl
import re


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

CATEGORY_MAPPING = {
    "top": [],
    "local": [],
    "national": [],
    "world": ["WORLD NEWS"],
    "opinion": [],
    "politics": ["POLITICS"],
    "business": ["DEALS", "BUSINESS NEWS", "U.S. LEGAL NEWS"],
    "technology & science": ["TECHNOLOGY NEWS", "ENVIRONMENT", "CYBER RISK"],
    "entertainment & art": [],
    "health": [],
    "sport": [],
    "weather": [],
    "lifestyle & culture": [],
    "multimedia": [],
}
# JULY 31, 2020 / 4:03 AM / 8 DAYS AGO
DATETIME_PATTERN = r'^(?P<month>%s) (?P<day>\d{1,2})(\,{0,1}) (?P<year>\d{2,4}) / (?P<hour>\d{1,2}):(?P<minute>\d{2}) (?P<period>AM|PM)' % datetime_util.ANY_MONTHS

class IndexPage(Page):

    BASE_CSS_SELECTOR = "div.StandardArticle_inner-container "
    HEADER_CSS_SELECTOR = BASE_CSS_SELECTOR + "div.ArticleHeader_content-container "
    BODY_CSS_SELECTOR = BASE_CSS_SELECTOR + "div.StandardArticleBody_container "

    category_raw = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "div.ArticleHeader_channel",
        value=lambda el: el.text,
        timeout=5
    )
    heading = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "h1.ArticleHeader_headline",
        value=lambda el: el.text,
        timeout=5
    )
    datetime_raw = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "div.ArticleHeader_date",
        value=lambda el: el.text,
        timeout=5
    )
    image_raw = Elements(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + "div.Image_container img, "
        + BODY_CSS_SELECTOR + "div.Slideshow_container img",
        value=lambda el: el.get_attribute('src'),
        timeout=0.5
    )
    media_raw = Elements(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + "div.Video_container iframe[src]",
        value=lambda el: el.get_attribute('src'),
        timeout=0.5
    )
    body_raw = Elements(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + "div.StandardArticleBody_body > p",
        value=lambda el:el.text,
        timeout=5
    )
    author = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "div.BylineBar_byline, "
        + HEADER_CSS_SELECTOR + "Attribution_attribution > p",
        value=lambda el:el.text,
        timeout=0.5
    )
    length = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "p.BylineBar_reading-time",
        value=lambda el:el.text,
        timeout=5
    )
    @property
    def datetime(self):
        return datetime_util.get_datetime_use_pattern(DATETIME_PATTERN, self.datetime_raw)

    @property
    def category(self):
        for (k,v) in CATEGORY_MAPPING.items():
            if self.category_raw in v:
                return k
        return None

    @property
    def body(self):
        return "\n".join([b for b in self.body_raw])

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
