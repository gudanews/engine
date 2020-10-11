# from util import nlp_util
# from processor import Processor as BaseProcessor
from database.news import NewsDB
from database.topic import TopicDB
import time
from datetime import datetime

# fix and add headline check
# algorithm change
now = time.time()

from util.nlp_test_similarity import find_similarity


class GroupingProcessor():

    def __init__(self):
        self.news = NewsDB()

    def _get_heading(self):

        self.db = NewsDB()
        column = ["title", "id", "duplicate_id", "source_id"]
        output = NewsDB().get_news_by_id(id=self.headline_id, column=column, record_as_dict=True)
        return output

    def _get_all_entries(self):
        column = ["title", "id", "duplicate_id", "source_id", "is_valid", "is_valid", "category_id",
                  "datetime_created", "datetime_updated", "topic_id"]
        existing = NewsDB().get_latest_news(column=column, record_as_dict=True, number_of_days=3)
        return existing

    def _find_matching(self):
        search = self._get_all_entries()
        entries = self._get_all_entries()
        for j in search:
            validation = True
            searches = self.news.get_news_by_id(j['id'], record_as_dict=True)
            if searches['topic_id'] == 0:
                for i in entries:
                    searching = self.news.get_news_by_id(i['id'], record_as_dict=True)
                    if find_similarity(searching['title'], searches['title']) > 0.7 and searching['id'] != searches[
                        'id'] and \
                            searching[
                                'duplicate_id'] == 0 and searching[
                        'source_id'] != searches["source_id"] and searches['duplicate_id'] == 0 and searching[
                        'topic_id'] == 0:
                        if validation == True:
                            topicid = TopicDB().add_topic(
                                dict(news_id=j['id'], category_id=searches['category_id'],
                                     datetime_created=datetime.now()))
                            self.news.update_news_by_id(id=searches['id'], record=dict(topic_id=int(topicid)))
                            validation = False
                        self.news.update_news_by_id(id=searching['id'], record=dict(topic_id=topicid))
                    elif find_similarity(searching['title'], searches['title']) > 0.7 and searching['id'] != searches[
                        'id'] and \
                            searching[
                                'duplicate_id'] == 0 and searching[
                        'source_id'] != searches["source_id"] and searches['duplicate_id'] == 0 and searching[
                        'topic_id'] != 0:
                        self.news.update_news_by_id(id=searches['id'], record=dict(topic_id=int(searching['topic_id'])))
                entries.remove(j)

    def process(self):

        self._find_matching()


if __name__ == "__main__":
    cd = GroupingProcessor()
    cd.process()

    end = time.time() - now
    print(end)
