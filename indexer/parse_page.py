#from webpage.reuters import
from indexer.parse_cnn import Cnn_parse
from util.webdriver_util import ChromeDriver

class parsePage():
    def __init__(self, page, driver):
        self.driver = driver
        self.page = page

    def go_to_page(self, url):
        self.driver.get(url)

    def get_body(self):
        output = ''
        for i in self.page.news.body:
            print(i)
            output+=i
        return output
    def get_heading(self):
        print(self.page.news.heading)
driver = ChromeDriver()
rp = Cnn_parse(driver)
pp = parsePage(rp, driver)
pp.go_to_page('https://www.cnn.com/2020/08/05/politics/biden-milwaukee-dnc/index.html')
pp.get_heading()
print(pp.get_body())

