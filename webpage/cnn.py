from holmium.core import Element, Locators, Sections
from holmium.core import Page
from holmium.core.conditions import VISIBLE

class News(Sections):
    heading = Element(
        Locators.CSS_SELECTOR,
        "h3.cnn-search__result-headline a",
        value=lambda el: el.text,
        timeout=5
    )
    url = Element(
        Locators.CSS_SELECTOR,
        "h3.cnn-search__result-headline a",
        value=lambda el: el.get_attribute('href'),
        timeout=5
    )
    image = Element(
        Locators.CSS_SELECTOR,
        "div.cnn-search__result-thumbnail img",
        value=lambda el: el.get_attribute('src'),
        timeout=5
    )
    datetime = Element(
        Locators.CSS_SELECTOR,
        "div.cnn-search__result-publish-date",
        value=lambda el: el.text,
        timeout=5
    )
    snippet = Element(
        Locators.CSS_SELECTOR,
        "div.cnn-search__result-body",
        value=lambda el: el.text,
        timeout=5
    )

class CNNPage(Page):
    news = News(
        Locators.CSS_SELECTOR,
        "div.cnn-search__result",
        timeout=10
    )
    next = Element(
        Locators.CSS_SELECTOR,
        "div.pagination-arrow-right",
        timeout=10
    )
