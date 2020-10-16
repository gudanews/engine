# from util import nlp_util
# from processor import Processor as BaseProcessor
from database.news import NewsDB
from database.topic import TopicDB
import time
from datetime import datetime

# fix and add headline check
# algorithm change
now = time.time()
from util.nlp_util import similar


class GroupingProcessor():

    def __init__(self, headline):
        self.headline_id = headline
        self.news = NewsDB()

    def _get_heading(self):

        self.db = NewsDB()
        column = ["title", "id", "duplicate_id", "source_id", "topic_id", "category_id"]
        output = NewsDB().get_news_by_id(id=self.headline_id, column=column, record_as_dict=True)
        return output

    def _get_all_entries(self):
        column = ["title", "id", "duplicate_id", "source_id", "is_valid", "is_valid", "category_id",
                  "datetime_created", "datetime_updated", "topic_id"]
        existing = NewsDB().get_latest_news(column=column, record_as_dict=True, number_of_days=14)
        return existing

    def _find_matching(self):
        search = self._get_heading()
        entries = self._get_all_entries()
        validation = True
        if search['topic_id'] == 0:
            for entry in entries:
                if similar(search['title'], entry['title']) > 0.7 and search['id'] != entry[
                    'id'] and \
                        search[
                            'duplicate_id'] == 0 and search[
                    'source_id'] != entry["source_id"] and entry['duplicate_id'] == 0 and entry['topic_id']==0:
                    if validation == True:
                        topicid = TopicDB().add_topic(
                            dict(news_id=search['id'], category_id=search['category_id'],
                                 datetime_created=datetime.now()))
                        self.news.update_news_by_id(id=search['id'], record=dict(topic_id=int(topicid)))
                        validation = False
                    self.news.update_news_by_id(id=entry['id'], record=dict(topic_id=topicid))
                elif similar(search['title'], entry['title']) > 0.7 and search['id'] != entry[
                    'id'] and \
                        search[
                            'duplicate_id'] == 0 and search[
                    'source_id'] != entry["source_id"] and entry['duplicate_id'] == 0 and entry[
                    'topic_id'] != 0:
                    self.news.update_news_by_id(id=search['id'], record=dict(topic_id=int(entry['topic_id'])))
                    break

    def process(self):

        self._find_matching()


if __name__ == "__main__":
    cd = GroupingProcessor(2)
    cd.process()
    end = time.time() - now
    print(end)
