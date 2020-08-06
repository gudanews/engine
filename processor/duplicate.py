from database.headline import HeadlineDB
from util.common import LoggedTestCase
from util.clean_list import clean_list
from database.headline import HeadlineDB
from util import checksimilarity
from processor import Processor as BaseProcessor
import logging


# fix and add headline check
# algorithm change
class DuplicateProcessor(BaseProcessor):
    logger = logging.getLogger("Processor.Duplicate")

    def __init__(self, headine_id):
        self.headline_id = headine_id

    def _get_heading(self):

        self.db = HeadlineDB()
        output = {}
        column = ["heading", "id"]
        existing = self.db.get_latest_news(column=column, condition="duplicate_id = 0 AND id=" + str(self.headline_id))
        for data in existing:
            output[data[1]] = data[0]
        return output

    def _get_processed(self):
        self.db = HeadlineDB()
        column = ["heading", "id"]
        output = {}
        existing = self.db.get_latest_news(column=column, condition="is_processed=1")
        for data in existing:
            output[data[1]] = data[0]
        return output

    def _find_duplicate(self):
        output = []
        check = self._get_heading()
        all_processed = self._get_processed()
        # print(check)
        checker = self._getKeysByValue(check, list(check.values())[0])
        all_processed.pop(checker[0])
        list_of_check_values = []
        list_of_processed_values = []
        for i in check.values():
            list_of_check_values.append(i)
        # print(list_of_check_values)

        for i in all_processed.values():
            list_of_processed_values.append(i)
        # list_of_processed_values.remove(list_of_check_values[0])
        for item in list_of_processed_values:
            if checksimilarity(list_of_check_values[0], item) >= 75 or checksimilarity(item,list_of_check_values[0]) >= 75:
                output.append(list(all_processed.keys())[list(all_processed.values()).index(item)])
                output.append(checker[0])
                return output
        return False
    def _update_records(self, li):
        if li != False:
            self.db.update_record_with_id(dict(duplicate_id=li[0]), li[1])
    def _getKeysByValue(self, dictOfElements, valueToFind):
        listOfKeys = list()
        listOfItems = dictOfElements.items()
        for item in listOfItems:
            if item[1] == valueToFind:
                listOfKeys.append(item[0])
        return listOfKeys

    def process(self):
        # print(self._get_processed())
        # print(self._get_heading())
        dup = self._find_duplicate()
        #print(dup)
        self._update_records(dup)


if __name__ == "__main__":

    def get_random_string(length):
        import string
        import random
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str


    def create_test(li):
        import random
        db = HeadlineDB()
        for a in li:
            b = random.randint(0, 1)
            db.insert_db_record(dict(heading=a, is_processed=1))


    li = []
    for i in range(40):
        li.append(get_random_string(1))
    #create_test(li)
    cd = DuplicateProcessor(26)
    cd.process()
