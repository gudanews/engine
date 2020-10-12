# from util import nlp_util
# from processor import Processor as BaseProcessor
from database.news import NewsDB
from util.nlp_util import similar


# fix and add headline check
# algorithm change
class DuplicateProcessor():

    def __init__(self, headine_id):
        self.headline_id = headine_id
        self.db = NewsDB()
    def _get_heading(self):

        self.db = NewsDB()
        column = ["title", "id", "duplicate_id", "source_id"]
        output = NewsDB().get_news_by_id(id=self.headline_id, column=column, record_as_dict=True)
        return output

    def _get_all_entries(self):
        column = ["title", "id", "duplicate_id", "source_id"]
        existing = NewsDB().get_latest_news(column=column, record_as_dict=True,number_of_days=10000)
        return existing

    def find_duplicates(self):
        entries = self._get_all_entries()
        search = self._get_heading()
        for i in entries:
            if i['id'] > search['id']:
                break
            if similar(i['title'], search['title']) > 0.7 and i['id'] != search['id'] and i['source_id'] == search["source_id"]:#i['duplicate_id'] == 0 and
                self.db.update_news_by_id(id=i['id'], record=dict(duplicate_id=search['id']))


if __name__ == "__main__":


    cd = DuplicateProcessor(4)
    cd.find_duplicates()
