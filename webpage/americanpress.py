from holmium.core import Element, Locators, Section, Sections, Page
from holmium.core.conditions import VISIBLE

class Section(Sections):
    heading = Element(
        Locators.CSS_SELECTOR,
        "div.card-headline h3.tnt-headline a",
        value=lambda el: el.text,
        timeout=5
    )
    datetime = Element(
        Locators.CSS_SELECTOR,
        "div.card-meta li.card-date time[datetime]",
        value=lambda el: el.get_attribute("datetime"),
        timeout=5
    )
    url = Element(
        Locators.CSS_SELECTOR,
        "div.card-headline h3.tnt-headline a[href]",
        value=lambda el: el.get_attribute("href"),
        timeout=5
    )
    snippet = Element(
        Locators.CSS_SELECTOR,
        "div.card-lead p.tnt-summary",
        value=lambda el: el.text,
        timeout=5
    )


class APPage(Page):
    news = Section(
        #Locators.XPATH,
        #"//div[@class='card-container']//div[@class='card-label-flags']/../..",
        Locators.CSS_SELECTOR,
        #"div.col-lg-12 div.card-container",
        "div.card-panel div.card-container",
        timeout=10
    )

#class TestBaseData(unittest.TestCase):
#
#    def setUp(self):
#        self.driver = Driver().connect()
#        self.driver.get('https://www.americanpress.com/news/')
#        self.page = APPage(self.driver)
#
#    def test(self):
#        a = 1
#        for i in self.page.news:
#            print(i.heading)
#
#if __name__ == '__main__':
#    #unittest.main()
#    pass