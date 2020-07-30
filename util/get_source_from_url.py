from database.news_headline import SourceDB
from util.common import LoggedTestCase


def get_sources_from_url(url):
    sdb = SourceDB()
    output = []
    for data in sdb.fetch_db_records(column=["website"]):
        existing_data = ''
        for i in range(2, len((str(data))) - 3):
            existing_data += str(data)[i]
        output.append(existing_data)
    output2 = []
    for data in sdb.fetch_db_records(column=["name"]):
        existing_data = ''
        for i in range(2, len((str(data))) - 3):
            existing_data += str(data)[i]
        output2.append(existing_data)

    for entry in range(len(output)):
        if output[entry].lower() in url.lower() or output2[entry].lower() in url.lower():#.replace(' news','').replace('.com','').replace(' ','').replace('the','')
            return True
    return False

import unittest

sdb = SourceDB()
output = []

for data in sdb.fetch_db_records(column=["website"]):
    existing_data = ''
    for i in range(2, len((str(data))) - 3):
        existing_data += str(data)[i]
    output.append(existing_data)

#print(get_sources_from_url('https://www.upi.com/Top_News/'))
class TestGetSources(LoggedTestCase):
    def test_sources(self):
        for i in output:
            a = get_sources_from_url(i.lower())
            self.assertEqual(a,True)
    def test_certain(self):
        b = get_sources_from_url('https://www.nytimes.com/')
        self.assertEqual(b, True)
if __name__ == '__main__':
    unittest.main()

