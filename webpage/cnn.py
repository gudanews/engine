from holmium.core import Element, Elements, Locators, Sections
from holmium.core import Page
from holmium.core.conditions import VISIBLE
from util import datetime_util
import re


class News(Sections):
    heading = Element(
        Locators.CSS_SELECTOR,
        "h3 a span.cd__headline-text",
        value=lambda el: el.text,
        timeout=5
    )
    url = Element(
        Locators.CSS_SELECTOR,
        "h3 a[href]",
        value=lambda el: el.get_attribute('href'),
        timeout=5
    )
    image = Element(
        Locators.CSS_SELECTOR,
        "div.media a img",
        value=lambda el: el.get_attribute('data-src-full16x9'),
        only_if=VISIBLE(),
        timeout=0.5
    )


class CrawlPage(Page):
    news = News(
        Locators.CSS_SELECTOR,
        "section.zn-homepage1-zone-1 div.zn__containers li > article.cd--card",
        timeout=10
    )


# Updated 11:48 AM ET, Sat August 8, 2020
DATETIME_PATTERN = r'.* (?P<hour>\d{1,2}):(?P<minute>\d{2}) (?P<period>AM|PM) (?P<zone>%s)(\,{0,1}) (%s) (?P<month>%s) (?P<day>\d{1,2})(\,{0,1}) (?P<year>\d{2,4})$' % (datetime_util.ANY_TIMEZONE, datetime_util.ANY_WEEK_DAYS_3L, datetime_util.ANY_MONTHS)

class IndexPage(Page):

    BASE_CSS_SELECTOR = "article.pg-rail-tall "
    MAIN_CSS_SELECTOR = BASE_CSS_SELECTOR + "div.pg-side-of-rail "

    heading = Element(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + "h1.pg-headline",
        value=lambda el: el.text,
        timeout=5
    )
    author_raw = Elements(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + "div.metadata p.metadata__byline a",
        value=lambda el: el.text,
        timeout=5
    )
    datetime_raw = Element(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + "div.metadata p.update-time",
        value=lambda el: el.text,
        timeout=5
    )
    image = Element(
        Locators.CSS_SELECTOR,
        MAIN_CSS_SELECTOR + ".pg-rail-tall__head img",
        value=lambda el: el.get_attribute("data-src-full16x9"),
        timeout=0.5
    )
    body_raw = Elements(
        Locators.CSS_SELECTOR,
        MAIN_CSS_SELECTOR + ".pg-rail-tall__body .zn-body__paragraph",
        value=lambda el: el.text,
        timeout=5
    )

    @property
    def author(self):
        return ", ".join(self.author_raw)

    @property
    def datetime(self):
        return datetime_util.get_datetime_use_pattern(DATETIME_PATTERN, self.datetime_raw) if self.datetime_raw else None

    @property
    def body(self):
        return "\n".join(self.body_raw)