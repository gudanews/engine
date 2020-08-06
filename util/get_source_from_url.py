from database.source import SourceDB
from util.common import LoggedTestCase
from furl import furl

def get_sources_from_url(url):
    sdb = SourceDB()
    output = []
    for data in sdb.fetch_db_records(column=["crawling_url"]):
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
        #print(output[entry])
        f = furl(output[entry])
        u = furl(url)
        if f.host in u.host:
            return f.host
    return False

import unittest

sdb = SourceDB()
output = []
url ='https://www.google.com'
print(get_sources_from_url(url))
for data in sdb.fetch_db_records(column=["crawling_url"]):
    existing_data = ''
    for i in range(2, len((str(data))) - 3):
        existing_data += str(data)[i]
    output.append(existing_data)

#print(get_sources_from_url('https://www.upi.com/Top_News/'))
class TestGetSources(LoggedTestCase):
    def test_sources(self):
        for i in output:
            a = get_sources_from_url(i.lower())
            self.assertNotEqual(a,False)

if __name__ == '__main__':
    unittest.main()
    pass
