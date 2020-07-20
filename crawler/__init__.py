class Crawler:
    def __init__(self, driver):
        self.driver = driver
        self.page=None

    def goto_website(self):
        raise NotImplementedError("Missing goto_website")

    def parse_content(self):
        raise NotImplementedError("Missing parse_content")

    def insert_into_news_headline_db(self):
        pass

    def crawl(self):
        self.goto_website()
        self.parse_content()
        self.insert_into_news_headline_db()

if __name__ == "main":
    for cl in __dict__:
        if issubclass(cl, Crawler):
            obj = cl(driver)
            obj.crawl()