from util.webdriver_util import ChromeDriver
from database.topic import TopicDB
from database.image import ImageDB, NewsImageDB
from database.news import NewsDB
from database.source import SourceDB
from database.translation import TranslationDB
from database.category import CategoryDB, NewsCategoryDB
from datetime import datetime, timedelta
import logging
import time
from util.text_util import checksimilarity, TextHelper
import re


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
        self.news_category_db = NewsCategoryDB()
        self.topic_db = TopicDB()
        self.source_db = SourceDB()
        self.image_db = ImageDB()
        self.translation_db = TranslationDB()
        self.category_db = CategoryDB()
        self.start_time = datetime.now()
        self.total_indexed = 0
        self.total_invalid = 0
        self.total_record = 0

    def is_valid_news_url(self, url):
        return True
    
    def go_to_page(self, url):
        self.driver.switch_to_new_tab()
        self.driver.get(url)
        time.sleep(self.WAIT_FOR_PAGE_READY)

    def get_candidates(self):
        return self.news_db.get_non_indexed_news_by_source_id(source_id = self.SOURCE_ID, max_count=5)

    def process_category(self, record_indexing, news_id):
        categories_indexing = record_indexing.pop("categories", [])
        if record_indexing.get("category", None):
            categories_indexing.append(record_indexing.pop("category"))
        category_existing = self.category_db.get_category_name_by_news_id(news_id)
        all_categories = self.category_db.get_additional_category_name_by_news_id(news_id)
        for cat in categories_indexing:
            if cat and cat not in all_categories:
                cat_id = self.category_db.get_category_id_by_name(cat)
                if not category_existing:
                    self.news_db.update_news_by_id(id=news_id, record=dict(category_id=cat_id))
                self.news_category_db.add_news_category(news_id=news_id, category_id=cat_id)
                all_categories.append(cat)

    def process_image(self, record_indexing, news_id):
        images_indexing = record_indexing.pop("images", [])
        if record_indexing.get("image", None):
            images_indexing.append(record_indexing.pop("image"))
        image_existing = self.image_db.get_image_url_by_news_id(news_id)
        all_images = self.image_db.get_additional_image_url_by_news_id(news_id)
        for img in images_indexing:
            if img and img not in all_images:
                img_id = self.image_db.add_image(img, generate_thumbnail=not image_existing)
                if not image_existing:
                    self.news_db.update_news_by_id(id=news_id, record=dict(image_id=img_id))
                self.news_image_db.add_news_image(news_id=news_id, image_id=img_id)
                all_images.append(img)

    def process_text(self, record_indexing, record_existing):
        news_id = record_existing.get("id")
        title_indexing = record_indexing.pop("title")
        content_indexing = record_indexing.pop("content", "")
        snippet_existing = record_existing.get("snippet", None)
        snippet_indexing = snippet_existing if snippet_existing else \
            content_indexing.split("\n")[0][:512] if content_indexing else None
        text_helper = TextHelper(text=content_indexing)
        self.logger.info("TIME STAMP BEFORE TRANSLATION")
        translation_id = self.translation_db.add_translation(text_helper=text_helper, title=title_indexing,
            snippet=snippet_indexing, content=content_indexing) if not record_existing.get("translation_id", None) else 0
        self.logger.info("TIME STAMP AFTER TRANSLATION")
        content_indexing = text_helper.save() if not record_existing.get("content", None) else None
        record = dict()
        if title_indexing != record_existing.get("title"):
            record["title"] = title_indexing
        if snippet_indexing != snippet_existing:
            record["snippet"] = snippet_indexing
        if content_indexing:
            record["content"] = content_indexing
        if translation_id:
            record["translation_id"]= translation_id
        if record:
            self.news_db.update_news_by_id(id=news_id, record=record)

    def create_record_with_page_element(self):
        record = dict()
        if "popup" in dir(self.page):
            self.page.dismiss_popup()
        for el in ("category", "categories", "author", "title", "datetime_created", "content", "media", "image", "images"):
            if el in dir(self.page):
                record[el] = eval("self.page." + el)
                if not record[el]:
                    record.pop(el)
                else:
                    self.logger.info("[%s]:\t%s" % (el.upper(), record[el]))
        return record

    def is_valid_indexing_record(self, record_indexing, record_existing):
        news_id = record_existing["id"]
        # Check if the title is similar to existing record
        title_indexing = record_indexing.get("title", "")
        title_existing = record_existing.get("title", "")
        if not title_indexing or (title_existing and checksimilarity(title_indexing, title_existing) < 0.4):
            self.logger.warning("<news> [ID=%s] found different title\n[EXSITING]\t%s\n[INDEXING]\t%s"
                                % (news_id, title_existing, title_indexing))
            # return False
        # Check if the datetime created is similar to existing record
        datetime_indexing = record_indexing.get("datetime_created", None)
        datetime_existing = record_existing.get("datetime_created", None)
        if datetime_indexing and datetime_existing and abs(datetime_indexing - datetime_existing) > timedelta(hours=24):
            self.logger.warning("<news> [ID=%s] found different timestamp\n[EXSITING]\t%s\n[INDEXING]\t%s"
                                % (news_id, datetime_existing, datetime_indexing))
            # return False
        # Check if the content can be found
        content = re.sub(re.compile(r'\s+'), '', record_indexing.get("content", ""))
        if len(content) < 20:
            self.logger.warning("<news> [ID=%s] cannot find content during indexing" % news_id)
            return False
        # Check if the category is the same as existing record
        # if "category" in record_indexing:
        #     record_indexing["category_id"] = self.category_db.get_category_id_by_name(record_indexing.pop("category"))
        #     if record_existing.get("category_id") and record_existing.get("category_id") != record_indexing.get("category_id"):
        #         self.logger.warning("<news> [ID=%s] found different category\n[EXSITING]\t%s\n[INDEXING]\t%s"
        #                             % (news_id, record_existing["category_id"], record_indexing["category_id"]))
                # return False
        return True

    def index(self):
        source_name = self.source_db.get_source_name_by_id(self.SOURCE_ID)
        self.logger.info("=====================  Indexing [%s] started  =====================" % source_name)
        self.indexing_news = self.get_candidates()
        for record_existing in self.indexing_news:
            news_id = record_existing.get("id")
            try:
                if self.is_valid_news_url(record_existing.get("url")):
                    self.go_to_page(record_existing.get("url"))
                    self.logger.info("LOADING PAGE [%s]" % record_existing.get("url"))
                    record_indexing = self.create_record_with_page_element()
                    if self.is_valid_indexing_record(record_indexing, record_existing):
                        self.logger.info("TIME STAMP BEFORE UPDATE")
                        if not DEBUGGING_TEST:
                            self.process_category(record_indexing, news_id)
                            self.logger.info("TIME STAMP AFTER CATEGORY")
                            self.process_image(record_indexing, news_id)
                            self.logger.info("TIME STAMP AFTER IMAGE")
                            self.process_text(record_indexing, record_existing)
                            self.logger.info("TIME STAMP AFTER TEXT")
                            record_indexing["is_indexed"] = True
                            if self.news_db.update_news_by_id(id=news_id, record=record_indexing):
                                self.logger.info("Completed <news> [ID=%s] indexing" % news_id)
                                self.total_indexed += 1
                                continue
                if not DEBUGGING_TEST and self.news_db.update_news_by_id(id=news_id, record=dict(is_valid=False)):
                    self.logger.warning("Mark <news> [ID=%s] invalid" % news_id)
                    self.total_invalid += 1
            except Exception as e:
                self.logger.warning("%s" % e)
                self.logger.warning("Error when indexing record[%d], skip to the next record......" % news_id)
                if not DEBUGGING_TEST and self.news_db.update_news_by_id(id=news_id, record=dict(debug=True)):
                    self.logger.warning("Mark <news> [ID=%s] as debug" % news_id)
            finally:
                self.total_record += 1

        self.logger.info("-------------  Total [%d/%d/%d] (indexed/invalid/total) Records  -----------" %
                         (self.total_indexed, self.total_invalid, self.total_record))
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
