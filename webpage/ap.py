from holmium.core import Element, Locators, Section, Sections, Page
from holmium.core.conditions import VISIBLE

class Cards(Sections):
    heading = Element(
        Locators.CSS_SELECTOR,
        "div.CardHeadline [data-key='card-headline']",
        value=lambda el: el.text,
        timeout=5
    )
    datetime = Element(
        Locators.CSS_SELECTOR,
        "div.CardHeadline span[data-key='timestamp']",
        value=lambda el: el.get_attribute("data-source"),
        timeout=5
    )
    url = Element(
        Locators.CSS_SELECTOR,
        "div.CardHeadline [data-key='card-headline']",
        value=lambda el: el.get_attribute("href"),
        timeout=5
    )
    snippet = Element(
        Locators.CSS_SELECTOR,
        "a[data-key='story-link'] div.content",
        value=lambda el: el.text,
        timeout=5
    )
    image = Element(
        Locators.CSS_SELECTOR,
        "div[data-key='media-placeholder'] img",
        value=lambda el: el.get_attribute("src"),
        timeout=5
    )


class APPage(Page):
    news = Cards(
        Locators.CSS_SELECTOR,
        "article div.FeedCard",
        timeout=10
    )