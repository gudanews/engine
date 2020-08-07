from holmium.core import Element, Elements, Locators, Sections
from holmium.core import Page
from holmium.core.conditions import VISIBLE
from util import datetime_util


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


class IndexPage(Page):

    BASE_CSS_SELECTOR = "article.pg-rail-tall.pg-rail--align-right"
    heading = Element(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + " h1.pg-headline",
        value=lambda el: el.text,
        timeout=5
    )
    datetime = Element(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + " p.update-time",
        value=lambda el: el.text,
        timeout=5
    )
    body = Elements(
        Locators.CSS_SELECTOR,
        BASE_CSS_SELECTOR + " div.zn-body__paragraph",
        value=lambda el: el.text,
        timeout=5,
    )
