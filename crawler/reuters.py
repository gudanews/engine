from util import datetime_util, image_util
from crawler import Crawler as BaseCrawler
from util.webdriver_util import Driver, scroll_down
from webpage.reuters import ReutersPage
from database.news_headline import NewsHeadlineDB
from database.image import ImageDB


MAX_CRAWLING_PAGES = 5
MIN_ALLOWED_UNRECORD_NEWS_TO_CONTINUE_CRAWLING = 3
REUTERS_ID = 1

class ReutersCrawler(BaseCrawler):

    def __init__(self, driver):
        self.homepage = "https://www.reuters.com/news/archive/us-the-wire?view=page"
        super(ReutersCrawler, self).__init__(driver)

    def goto_homepage(self):  # goes to reuters
        self.driver.get(self.homepage)

    def goto_nextpage(self):  # goes to next page
        page = ReutersPage(self.driver)
        page.next.click()

    def insert_records(self):
        page = ReutersPage(self.driver)
        scroll_down(self.driver)
        headline_db = NewsHeadlineDB()
        image_db = ImageDB()
        columns = ["heading", "url"]
        existing_data = headline_db.get_latest_news(column=columns, source=REUTERS_ID)
        unrecorded_news = 0
        for np in page.news:
            if not (np.heading, np.url) in existing_data:
                image_id = image_db.get_image_id_by_url(np.image)
                if not image_id:
                    image_file_path = image_util.save_image_from_url(np.image)
                    image_id = image_db.add_image(url=np.image, path=image_file_path)
                record = dict(heading=np.heading, datetime=datetime_util.str2datetime(np.time), source_id=REUTERS_ID,
                              image_id=image_id, url=np.url, snippet=np.snippet)
                print("Insert the following record into database......")
                print("Headline : <%s>\nURL : <%s>\nSnippet : %s<>\n\n\n" % (np.heading, np.url, np.snippet))
                headline_db.insert_db_record(record=record)
                unrecorded_news += 1
        self.complete = True if unrecorded_news < MIN_ALLOWED_UNRECORD_NEWS_TO_CONTINUE_CRAWLING else False

    def crawl(self):
        self.goto_homepage()
        self.complete = False
        for i in range(MAX_CRAWLING_PAGES):
            if not self.complete:
                self.insert_records()
                self.goto_nextpage()


if __name__ == "__main__":
    driver = Driver().connect()
    crawler = ReutersCrawler(driver)
    crawler.crawl()
    driver.close()
