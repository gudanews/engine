from holmium.core import Element, Locators, Section, Sections,Elements
from holmium.core import Page
from holmium.core.conditions import VISIBLE


class Stories(Sections):
    heading = Element(
        Locators.CSS_SELECTOR,
        "h1.headline",
        value=lambda el: el.text,
        timeout=5
    )
    body = Elements(
        Locators.CSS_SELECTOR,
        "div.StandardArticleBody_body > p",
        value=lambda el:el.text,
        timeout=5,
    )


class Reuters_parse(Page):
    news = Stories(
        Locators.CSS_SELECTOR,
        "div.StandardArticle_inner-container",
        timeout=10
    )
