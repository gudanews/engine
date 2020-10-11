# from util import nlp_util
# from processor import Processor as BaseProcessor
from database.news import NewsDB
from util.nlp_util import similar


# fix and add headline check
# algorithm change
class DuplicateProcessor():

    def __init__(self, headine_id):
        self.headline_id = headine_id

    def _get_heading(self):

        self.db = NewsDB()
        column = ["title", "id", "duplicate_id", "source_id"]
        output = NewsDB().get_news_by_id(id=self.headline_id, column=column, record_as_dict=True)
        return output

    def _get_all_entries(self):
        column = ["title", "id", "duplicate_id", "source_id"]
        existing = NewsDB().get_latest_news(column=column, record_as_dict=True)
        return existing

    def _find_duplicates(self):
        entries = self._get_all_entries()
        search = self._get_heading()
        output = []

        for i in entries:

            if similar(i['title'], search['title']) > 0.7 and i['id'] != search['id'] and i['source_id'] == search["source_id"]:#i['duplicate_id'] == 0 and
                a = {}
                a[i['id']] = self.headline_id
                output.append(a)
        return output

    def _update_record_duplicate_id(self, li):
        for i in li:
            for a in i.keys():
                ID = a
            for b in i.values():
                value = b

            NewsDB().update_news_by_id(id=ID, record=dict(duplicate_id=value))

    def process(self):
        data = self._find_duplicates()
        self._update_record_duplicate_id(data)


if __name__ == "__main__":


    cd = DuplicateProcessor(1)
    cd.process()
