from holmium.core import Element, Locators, Sections
from holmium.core import Page
from holmium.core.conditions import VISIBLE

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
        timeout=0.5
    )
    datetime = Element(
        Locators.CSS_SELECTOR,
        "div.cnn-search__result-publish-date",
        value=lambda el: el.text,
        timeout=5
    )

class CNNPage(Page):
    news = News(
        Locators.CSS_SELECTOR,
        "section.zn-homepage1-zone-1 div.zn__containers li > article",
        timeout=10
    )