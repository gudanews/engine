from holmium.core import Element, Locators, Section, Sections
from holmium.core import Page
from holmium.core.conditions import VISIBLE

class Stories(Sections):
    heading = Element(
        Locators.CSS_SELECTOR,
        "div[role='heading']",
        value=lambda el: el.text,
        timeout=5
    )
    datetime = Element(
        Locators.CSS_SELECTOR,
        "span.WG9SHc span",
        value=lambda el: el.text,
        timeout=5
    )
    url = Element(
        Locators.CSS_SELECTOR,
        "a[style='text-decoration:none;display:block']",
        value=lambda el: el.get_attribute('href'),
        timeout=5
    )
    snippet = Element(
        Locators.CSS_SELECTOR,
        "div.Y3v8qd",
        value=lambda el: el.text,
        timeout=5
    )
    image = Element(
        Locators.CSS_SELECTOR,
        "div.KNcnob g-img img",
        value=lambda el: el.get_attribute('src'),
        only_if=VISIBLE(),
        timeout=5,
    )


class GoogleNewsPage(Page):
    news = Stories(
        Locators.CSS_SELECTOR,
        "g-card a",
        timeout=10
    )
    #next = Element(
    #    Locators.CSS_SELECTOR,
    #    "div.control-nav a.control-nav-next",
    #    timeout=10
    #)
