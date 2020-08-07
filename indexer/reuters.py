from indexer import Indexer as BaseIndexer
from util.webdriver_util import ChromeDriver
from webpage.reuters import IndexPage as ReutersPage
import logging
from furl import furl



class ReutersIndexer(BaseIndexer):

    logger = logging.getLogger("Crawler.REU")

    def __init__(self, driver):
        page = ReutersPage(driver)
        super(ReutersIndexer, self).__init__(driver, page)

    def find_alternative_image_url(self, url):
        # Expected https://s4.reutersmedia.net/resources/r/?m=02&d=20200728&t=2&i=1527461013&w=370&fh=&fw=&ll=&pl=&sq=&r=LYNXNPEG6R1MZ
        # Alternative https://s4.reutersmedia.net/resources/r/?m=02&d=20200728&t=2&i=1527461013&w=800&fh=&fw=&ll=&pl=&sq=&r=LYNXNPEG6R1MZ
        f = furl(url)
        if "w" in f.args.keys():
            f.args["w"] = "800"
        return f.url

if __name__ == "__main__":
    driver = ChromeDriver()
    indexer = ReutersIndexer(driver)
    indexer.index()
    driver.close()
