# from util import nlp_util
# from processor import Processor as BaseProcessor
from database.news import NewsDB
from util.nlp_util import similar


# fix and add headline check
# algorithm change
class DuplicateProcessor():

    def __init__(self):
        self.db = NewsDB()

    def _get_heading(self, h_id):

        self.db = NewsDB()
        column = ["title", "id", "duplicate_id", "source_id", "image_id", "author"]
        output = NewsDB().get_news_by_id(id=h_id, column=column, record_as_dict=True)
        return output

    def _get_all_entries(self):
        column = ["title", "id", "duplicate_id", "source_id", "image_id", "author"]
        existing = NewsDB().get_latest_news(column=column, record_as_dict=True, number_of_days=14)
        return existing

    def find_duplicates(self, headline_id):

        entries = self._get_all_entries()
        search = self._get_heading(headline_id)
        for i in entries:
            if i['id'] > search['id'] or search['duplicate_id'] !=0:
                break
            if self.get_similarity_score(i, search) >= 0.7 and i['id'] != search['id'] and i['source_id'] == search[
                "source_id"]:  # i['duplicate_id'] == 0
                self.db.update_news_by_id(id=i['id'], record=dict(duplicate_id=search['id']))

    def get_similarity_score(self, a, b):
        total = 2.5
        if a['image_id'] == b['image_id']:
            image_score = 1
        else:
            image_score = 0
        if a['image_id'] == 0 or b['image_id'] == 0:
            image_score = 0
            total -= 1
        if a['author'] == b['author']:
            author_score = 0.5
        else:
            author_score = 0
        if a['author'] == None or b['author'] == None:
            author_score = 0
            total -= 0.5
        similar_score = (similar(a['title'], b['title']) + author_score + image_score) / total
        return float(similar_score)


if __name__ == "__main__":
    import time

    cd = DuplicateProcessor()
    for news_id in range(50000, 55000):
        cd.find_duplicates(news_id)
