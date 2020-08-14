from holmium.core import Element, Locators, Section, Sections
from holmium.core import Page
from holmium.core.conditions import VISIBLE
from util import datetime_util

class Stories(Sections):
    title = Element(
        Locators.CSS_SELECTOR,
        "div[role='heading']",
        value=lambda el: el.text,
        timeout=5
    )
    datetime_raw = Element(
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


class GoogleTranslationPage(Page):
    input = Element(
        Locators.CSS_SELECTOR,
        "textarea#source",
        timeout=5
    )
    output = Element(
        Locators.CSS_SELECTOR,
        "span.translation[lang]",
        value=lambda el: el.text,
        timeout=5
    )

    def build_translation_url(self, language="zh-CN"):
        return "https://translate.google.com/#view=home&op=translate&sl=en&tl=%s" % language

