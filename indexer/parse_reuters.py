from holmium.core import Element, Locators, Section, Sections,Elements
from holmium.core import Page
from holmium.core.conditions import VISIBLE


class Stories(Sections):
    heading = Element(
        Locators.CSS_SELECTOR,
        "h1.ArticleHeader_headline",
        value=lambda el: el.text,
        timeout=5
    )
    datetime = Element(
        Locators.CSS_SELECTOR,
        "div.ArticleHeader_date",
        value=lambda el: el.text,
        timeout=5
    )
    image = Element(
        Locators.CSS_SELECTOR,
        "div.Image_container img",
        value=lambda el: el.get_attribute('src'),
        timeout=5,
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
