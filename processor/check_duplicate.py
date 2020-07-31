from database.headline import HeadlineDB
from util.common import LoggedTestCase
from util.clean_list import clean_list
from database.headline import
class checkDuplicate:
    def get_headings(self):
        db = HeadlineDB()
        column = ["heading"]
        existing = db.fetch_db_records(column=column)
        existing = clean_list(existing)
        return existing

cd = checkDuplicate()
print(cd.get_headings())
for i in range(5):
    #db.insert_db_record(dict(heading='hello'))
    pass
