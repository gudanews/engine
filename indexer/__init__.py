from util.webdriver_util import ChromeDriver
from database.topic import TopicDB
from database.image import ImageDB
from database.news import NewsDB, NewsImageDB
from database.source import SourceDB
from datetime import datetime
import logging
import time


DEBUGGING_TEST = False

START_TIME = datetime.now()
logger = logging.getLogger("Indexer")


class Indexer:

    WAIT_FOR_PAGE_READY = 2.0
    SOURCE_ID = None
    logger = logging.getLogger("Indexer")

    def __init__(self, driver, page):
        self.driver = driver
        self.page = page
        self.indexing_news = []
        if not self.SOURCE_ID:
            raise NotImplementedError("Please Provide A Valid SOURCE_ID Before Proceed......")
        self.news_db = NewsDB()
        self.news_image_db = NewsImageDB()
        self.topic_db = TopicDB()
        self.source_db = SourceDB()
        self.image_db = ImageDB()
        self.start_time = datetime.now()

    def is_valid_news_url(self, url):
        return True
    
    def go_to_page(self, url):
        self.driver.switch_to_new_tab()
        self.driver.get(url)
        time.sleep(self.WAIT_FOR_PAGE_READY)

    def get_candidates(self):
        return self.news_db.get_non_indexed_news_by_source_id(source_id = self.SOURCE_ID, max_count=10)

    def process_images(self, index_record):
        news_id = index_record["id"]
        index_images = index_record.pop("images", [])
        index_images.append(index_record.pop("image", None))
        existing_image = self.image_db.get_image_url_by_news_id(news_id)
        all_images = []
        if existing_image:
            all_images.append(existing_image)
            all_images.extend(self.image_db.get_additional_image_url_by_news_id(news_id))
        for img in index_images:
            if img and img not in all_images:
                img_id = self.image_db.add_image(img, generate_thumbnail=existing_image is None)
                if not existing_image:
                    self.news_db.update_news_by_id(id=news_id, record=dict(image_id=img_id))
                    existing_image = img
                else:
                    self.news_image_db.add_news_image(news_id=news_id, image_id=img_id)
                all_images.append(img)

    def process_translation(self, index_record):
        news_id = index_record["id"]
        title, snippet = self.news_db.get_news_by_id(id=news_id, column=["title", "snippet"])

    def process_content(self, index_record):
        pass

    def update_record_with_page_element(self, record):
        for el in ("category", "images", "image", "media", "title", "datetime_created", "content", "author"):
            if el in dir(self.page):
                record[el] = eval("page." + el)
                if not record[el]:
                    record.pop(el)
                else:
                    self.logger.info("[%s]:\t%s" % (el.upper(), record[el]))
        return record

    def process_database_index_record(self, index_record):
        column = ["category_id", "image_id", 'title', 'datetime_created', "snippet", "content", "author"]
        existing_record = self.news_db.get_news_by_id(id=index_record["id"], column=column)

        if not DEBUGGING_TEST:
            self.process_image(index_record)
            self.process_translation(index_record)
            self.process_content(index_record)
        record["category_id"] = self.category_db.get_category_id_by_name(record.get("category", None))
        record["source_id"] = self.SOURCE_ID
        news_id = self.news_db.add_news_use_record(record=record) if not DEBUGGING_TEST else 0
        self.logger.info("Inserted Into <news> DB [ID=%s] With Values: %s." % (news_id, record))

    def process_current_page(self, news_id):
        index_record = dict(id=news_id)
        self.update_record_with_page_element(index_record)
        self.process_database_index_record(index_record)

    def index(self):
        source_name = self.source_db.get_source_name_by_id(self.SOURCE_ID)
        self.logger.info("=====================  Indexing [%s] started  =====================" % source_name)

        self.indexing_news = self.get_candidates()
        for (id, url) in self.indexing_news:
            if self.is_valid_news_url(url):
                self.go_to_page(url)
                self.logger.info("LOADING PAGE [%s]" % url)
                self.process_current_page(id)

        self.logger.info("---------------------  Total New Records  ---------------------")
        self.logger.info("===========  Indexing [%s] completed in [%s]  ===========\n" %
                         (source_name, str(datetime.now() - self.start_time)))


def main():
    import os
    from util import find_modules, find_public_classes
    from indexer import Indexer
    logger.info("=" * 40)
    logger.info("Started Indexing ......")
    logger.info("=" * 40 + "\n")
    modules = find_modules(os.path.dirname(__file__))
    for module in modules:
        classes = find_public_classes(module)
        for _,cls in classes.items():
            if issubclass(cls, Indexer) and not issubclass(Indexer, cls):
                try:
                    driver = ChromeDriver()
                    obj = cls(driver)
                    obj.index()
                    driver.close()
                except Exception as e:
                    cls.logger.warning("%s" % e)
                    cls.logger.warning("Error happens to current indexer, continuing......")
    logger.info(">" * 40 + "<" * 40)
    logger.info(">>> Completed Indexing. Processing Time [%s]. <<<"
                % str(datetime.now() - START_TIME))
    logger.info(">" * 40 + "<" * 40 + "\n" * 2)


if __name__ == "__main__":
    main()
