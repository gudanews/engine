from util import webdriver_util

class Crawler:
    def __init__(self, driver):
        self.driver = driver
        self.page=None

    def goto_homepage(self):
        raise NotImplementedError("Method <goto_homepage> must be defined before initiate.")

    def insert_records(self):
        raise NotImplementedError("Method <insert_records> must be defined before initiate.")

    def crawl(self):
        raise NotImplementedError("Method <crawl> must be defined before initiate.")


def main():
    import os
    from util import find_modules, find_public_classes
    from crawler import Crawler
    modules = find_modules(os.path.dirname(__file__))
    driver = None
    for module in modules:
        classes = find_public_classes(module)
        for _,cls in classes.items():
            if issubclass(cls, Crawler) and not issubclass(Crawler, cls):
                driver = webdriver_util.Driver().connect()
                obj = cls(driver)
                obj.crawl()
    if driver:
        driver.close()

if __name__ == "__main__":
    main()
