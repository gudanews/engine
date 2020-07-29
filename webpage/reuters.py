from holmium.core import Element, Locators, Section, Sections
from holmium.core import Page
from holmium.core.conditions import VISIBLE


class Stories(Sections):
    heading = Element(
        Locators.CSS_SELECTOR,
        "div.story-content h3.story-title",
        value=lambda el: el.text,
        timeout=5
    )
    datetime = Element(
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
        "div.story-photo img[src]",
        value=lambda el: el.get_attribute('src'),
        only_if=VISIBLE(),
        timeout=5,
    )


class ReutersPage(Page):
    news = Stories(
        Locators.CSS_SELECTOR,
        "article.story:not(.no-border-bottom)",
        timeout=10
    )
    next = Element(
        Locators.CSS_SELECTOR,
        "div.control-nav a.control-nav-next",
        timeout=10
    )
