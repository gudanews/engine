from holmium.core import Element, Locators, Section, Sections, Page
from holmium.core.conditions import VISIBLE

class Article(Sections):
    heading = Element(
        Locators.CSS_SELECTOR,
        "header.info-header h2.title a",
        value=lambda el: el.text,
        timeout=5
    )
    time = Element(
        Locators.CSS_SELECTOR,
        "div.story-content > time.article-time > span",
        value=lambda el: el.text,
        timeout=5
    )
    url = Element(
        Locators.CSS_SELECTOR,
        "div.story-content > a[href]",
        value=lambda el: el.get_attribute('href'),
        timeout=5
    )
    snippet = Element(
        Locators.CSS_SELECTOR,
        "div.story-content > p",
        value=lambda el: el.text,
        timeout=5
    )
    image = Element(
        Locators.CSS_SELECTOR,
        "div.m[picture[img]]",
        value=lambda el: el.get_attribute('src'),
        timeout=5
    )

class FoxNewsPage(Page):
    news = Article(
        Locators.CSS_SELECTOR,
        "div.main article.article",
        timeout=10
    )