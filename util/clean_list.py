from util.common import LoggedTestCase

def clean_list(list):
    output = []
    for data in list:
        existing_data = ''
        for i in range(2, len((str(data))) - 3):
            existing_data += str(data)[i]
        output.append(existing_data)
    return output
import unittest


class TestGetSources(LoggedTestCase):
    def test_sources(self):
        a = clean_list([('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',), ('hello',)])
        print(a)
        self.assertIn('hello',a)

if __name__ == '__main__':
    unittest.main()
    pass
