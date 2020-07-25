from holmium.core import Element, Locators, Sections
from holmium.core import Page
from holmium.core.conditions import VISIBLE

class Story(Sections):
    heading = Element(
        Locators.CSS_SELECTOR,
        "div.cd__content h3.cd__headline span.cd__headline-text",
        value=lambda el: el.text,
        timeout=5
    )
    url = Element(
        Locators.CSS_SELECTOR,
        "div.cd__content h3.cd__headline a",
        value=lambda el: el.get_attribute('href'),
        timeout=5
    )
    wrapper = Element(
        Locators.CSS_SELECTOR,
        "div.cd__content",
        timeout=5
    )

class CNNPage(Page):
    news = Story(
        Locators.CSS_SELECTOR,
        "div.cd__content",
        timeout=10
    )
