from holmium.core import Element, Elements, Locators, Section, Sections, Page
from holmium.core.conditions import VISIBLE
from util import datetime_util
from datetime import datetime
from furl import furl
from util.image_util import IMAGE_HEIGHT, IMAGE_WIDTH
from database.category import category_mapping
from webpage import WAIT_FOR_ELEMENT_TIMEOUT, WAIT_FOR_SECTION_TIMEOUT, WAIT_FOR_MINIMUM_TIMEOUT, WAIT_FOR_PAGE_POPUPS
import re
import time


def create_image_urls(url):
    # Expected https://a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2020/07/640/360/jasmine-Daniels-.jpg?tl=1&ve=1
    # Full Image URL https://a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2020/07/648/365/jasmine-Daniels-.jpg
    # Normalized URL https://a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2020/07/648/365/jasmine-Daniels-.jpg
    if url:
        f = furl(url)
        f.args = None
        width, height = f.path.segments[-3:-1]
        if re.search(r"^\d{3,4}$", width) and re.search(r"^\d{3,4}$", height):
            f.path.segments[-3:-1] = (IMAGE_WIDTH, IMAGE_HEIGHT)
            return [f.url, url]
        return [url]
    return None

class Articles(Sections):

    title = Element(
        Locators.CSS_SELECTOR,
        "div.info h2.title a",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    datetime_raw = Element(
        Locators.CSS_SELECTOR,
        "div.info div.meta span.time",
        value=lambda el: el.get_attribute("data-time-published"),
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    url = Element(
        Locators.CSS_SELECTOR,
        "div.info h2.title a",
        value=lambda el: el.get_attribute("href"),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    image_raw = Element(
        Locators.CSS_SELECTOR,
        "div.m img[src]",
        value=lambda el: el.get_attribute("src"),
        only_if=VISIBLE(),
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    category_raw = Element(
        Locators.CSS_SELECTOR,
        "div.info div.meta a",
        value = lambda el: el.text,
        timeout = 0.5
    )
    @property
    def datetime_created(self):
        return datetime_util.str2datetime(self.datetime_raw)

    @property
    def image(self):
        image = self.image_raw
        return create_image_urls(image)

    @property
    def category(self):
        return category_mapping(self.category_raw)


class CrawlPage(Page):
    news = Articles(
        Locators.CSS_SELECTOR,
        "section.collection-section article.article, div.collection article.article",
        timeout=WAIT_FOR_SECTION_TIMEOUT
    )


class IndexPage(Page):

    BASE_CSS_SELECTOR = "main.main-content article "
    HEADER_CSS_SELECTOR = BASE_CSS_SELECTOR + "header.article-header "
    BODY_CSS_SELECTOR = BASE_CSS_SELECTOR + "div.article-content "

    title = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "h1.headline",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    author_raw = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "div.author-byline > span",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    datetime_raw = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "div.article-date > time",
        value=lambda el: el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    category_link = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "div.eyebrow a",
        value=lambda el:el.get_attribute("href"),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    category_name = Element(
        Locators.CSS_SELECTOR,
        HEADER_CSS_SELECTOR + "div.eyebrow a",
        value=lambda el:el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    images_raw = Elements(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + "div.embed-media img, "
        + BODY_CSS_SELECTOR + "div > picture img",
        value=lambda el: el.get_attribute("src"),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    image_iframe = Element(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + "div.featured iframe",
        timeout=WAIT_FOR_MINIMUM_TIMEOUT
    )
    image_player = Element(
        Locators.CSS_SELECTOR,
        "div#player img",
        value=lambda el: el.get_attribute("src"),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    media_links = Elements(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + "div.embed-media a",
        value=lambda el: el.get_attribute("href"),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    media_iframes = Elements(
        Locators.CSS_SELECTOR,
        BODY_CSS_SELECTOR + "div.embed-media iframe",
        value=lambda el: el.get_attribute("src"),
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )
    content_raw = Elements(
        Locators.XPATH,
        "//div[@class='article-body']/p[not(.//strong)]",
        value=lambda el:el.text,
        timeout=WAIT_FOR_ELEMENT_TIMEOUT
    )

    @property
    def author(self):
        author = self.author_raw
        if author and author.startswith("By "):
            return author[3:]

    @property
    def category(self):
        category = category_mapping(self.category_link)
        return category if category else category_mapping(self.category_name)

    @property
    def datetime_created(self):
        dt = self.datetime_raw
        if dt and dt.startswith("Published "):
            dt = dt[10:]
        return datetime_util.str2datetime(dt)

    @property
    def content(self):
        return "\n".join(self.content_raw)

    @property
    def images(self):
        images = self.images_raw
        all_images = []
        for img in images:
            all_images.append(create_image_urls(img))
        if self.image_iframe:
            self.driver.switch_to.frame(self.image_iframe)
            if self.image_player:
                all_images.append(create_image_urls(self.image_player))
            self.driver.switch_to.default_content()
        return all_images

    @property
    def media(self):
        all_media = []
        for m in self.media_links + self.media_iframes:
            all_media.append(m)
        return all_media

    # If the indexing is running via Chrome, we will see the popup, but no pop up during HEADLESS CHROME run.
    # def dismiss_popup(self, wait=True):
    #     if wait:
    #         time.sleep(WAIT_FOR_PAGE_POPUPS)
    #     if self.popup:
    #         try:
    #             self.driver.switch_to.frame(self.driver.find_element_by_css_selector("div.tp-modal iframe"))
    #             if self.close_popup:
    #                 self.close_popup.click()
    #         except:
    #             pass
    #         finally:
    #             self.driver.switch_to.default_content()
