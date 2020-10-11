from util.webdriver_util import ChromeDriver
import time
from webpage.google import GoogleNewsPage
from database import headline
from database import news
from datetime import datetime


class searchGoogle():
    def __init__(self, driver):
        self.driver = driver

    def go_to_google_and_search_past_week(self, keyword):
        self.driver.get("https://www.google.com/search?q=" + str(keyword) + "&tbm=nws&biw=1707&bih=924&tbs=qdr%3Aw")
        self.page = GoogleNewsPage(self.driver)

    def get_headlines(self):
        output = []
        for entry in self.page.news:
            output.append(entry.heading)
            return output

    def get_urls(self):
        output = []
        for entry in self.page.news:
            output.append(entry.url)
            return output

    def get_datetime(self):
        output = []
        for entry in self.page.news:
            output.append(entry.datetime)
        return output

    def get_snippet(self):
        output = []
        for entry in self.page.news:
            output.append(entry.snippet)
            return output

    def get_image(self):
        output = []
        for entry in self.page.news:
            output.append(entry.image)
        return output

    def insert_into_database(self, list_of_urls, heading_id):
        datadb = news()
        column = ['link']
        existing_data = datadb.get_latest_news(column=column)
        i = 0
        for url in list_of_urls:
            if (url,) not in existing_data:
                i += 1
                record = dict(link=url, headline_id=heading_id, source_id=0, heading='None',
                              datetime=datetime.now(), snippet=None, image=None)
                datadb.insert_db_record(record=record)

    def grab_headlines_from_db(self):
        headline_db = headline()
        columns = ["heading"]
        output = []
        for data in headline_db.fetch_db_records(column=columns):
            print(data)
            output.append(data[0])
        return output

    def grab_id_from_db(self):
        headline_db = headline()
        columns = ["id"]
        output = []
        for data in headline_db.fetch_db_records(column=columns):
            existing_data = ''
            for i in range(1, len((str(data))) - 2):
                existing_data += str(data)[i]
            output.append(existing_data)
        return output

    def index(self):
        headlines = self.grab_headlines_from_db()
        ids = self.grab_id_from_db()
        for data in range(len(headlines)):
            self.go_to_google_and_search_past_week(headlines[data])
            urls = self.get_urls()


driver = ChromeDriver()
sg = searchGoogle(driver)
sg.go_to_google_and_search_past_week('google')
sg.get_image()
sg.get_datetime()
sg.get_snippet()
print(sg.grab_headlines_from_db())
time.sleep(10000)

# class TestSearchGoogle(LoggedTestCase):
#    def test_go_to_google_and_search(self):
#        for i in range(20):
#            length = 10
#            letters = string.ascii_lowercase
#            result_str = ''.join(random.choice(letters) for i in range(length))
#            sg.go_to_google_and_search_past_week(result_str)
#    # def test_change_settings(self):
#    #    sg.change_settings()
