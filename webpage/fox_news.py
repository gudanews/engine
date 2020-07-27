from holmium.core import Element, Locators, Section, Sections, Page
from holmium.core.conditions import VISIBLE

class Article(Sections):
    heading = Element(
        Locators.CSS_SELECTOR,
        "div.info h2.title a",
        value=lambda el: el.text,
        timeout=5
    )
    datetime = Element(
        Locators.CSS_SELECTOR,
        "div.info div.meta span.time",
        value=lambda el: el.get_attribute("data-time-published"),
        timeout=0.5
    )
    url = Element(
        Locators.CSS_SELECTOR,
        "div.info h2.title a",
        value=lambda el: el.get_attribute("href"),
        timeout=5
    )
    image = Element(
        Locators.CSS_SELECTOR,
        "div.m picture img[src]",
        value=lambda el: el.get_attribute("src"),
        only_if=VISIBLE(),
        timeout=5
    )

class FoxNewsPage(Page):
    news = Article(
        Locators.CSS_SELECTOR,
        "main.main-content div.collection article.article",
        timeout=10
    )