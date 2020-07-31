from holmium.core import Element, Locators, Section, Sections, Page
from holmium.core.conditions import VISIBLE

class Cards(Sections):
    heading = Element(
        Locators.CSS_SELECTOR,
        "div.CardHeadline a[href]",
        value=lambda el: el.text,
        timeout=5
    )
    datetime = Element(
        Locators.CSS_SELECTOR,
        "div.CardHeadline span.Timestamp",
        value=lambda el: el.get_attribute("data-source"),
        timeout=5
    )
    url = Element(
        Locators.CSS_SELECTOR,
        "div.CardHeadline a[href], div.FeedCard > a[href]",
        value=lambda el: el.get_attribute("href"),
        timeout=5
    )
    snippet = Element(
        Locators.CSS_SELECTOR,
        "a div.content",
        value=lambda el: el.text,
        timeout=5
    )
    image = Element(
        Locators.CSS_SELECTOR,
        "a img",
        value=lambda el: el.get_attribute("src"),
        only_if=VISIBLE(),
        timeout=5
    )


class APPage(Page):
    news = Cards(
        Locators.CSS_SELECTOR,
        "article div.FeedCard[class*='Component-wireStory']",
        timeout=10
    )