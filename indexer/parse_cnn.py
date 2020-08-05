from holmium.core import Element, Locators, Section, Sections, Elements
from holmium.core import Page
from holmium.core.conditions import VISIBLE


class Stories(Sections):
    heading = Element(
        Locators.CSS_SELECTOR,
        "h1.pg-headline",
        value=lambda el: el.text,
        timeout=5
    )
    datetime = Element(
        Locators.CSS_SELECTOR,
        "p.update-time",
        value=lambda el: el.text,
        timeout=5
    )
    body = Elements(
        Locators.CSS_SELECTOR,
        "div.zn-body__paragraph",
        value=lambda el: el.text,
        timeout=5,
    )


class Cnn_parse(Page):
    news = Stories(
        Locators.CSS_SELECTOR,
        "article.pg-rail-tall.pg-rail--align-right",
        timeout=10
    )
