from util import webdriver_util
class Crawler:
    def __init__(self, driver):
        self.driver = driver
        self.page=None

    def goto_website(self):
        raise NotImplementedError("Missing goto_website")

    def insert_records(self):
        raise NotImplementedError("Missing goto_website")

    def crawl(self):
        self.goto_website()
        self.insert_records()

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
