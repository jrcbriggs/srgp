'''
Created on 2 Nov 2014

@author: julian
'''
import unittest

from civimember2nb import MembersHandler

class Test(unittest.TestCase):

    def setUp(self):
        self.fieldnames = ['col0', 'col1'],
        self.table = [
                    {'col0':0, 'col1':1},
                    ]
        self.mh = MembersHandler(table=self.table, FIELDNAMES=self.fieldnames)

    def test_append_columns(self):
        row = self.table[0]
        self.mh.append_fields(row)
        result = row
        expected = {'col0':0, 'col1':1, 'StatusNB':'active', 'Membership Type':'Current'}  # .update(self.mh.columns_new)
        self.assertDictEqual(result, expected)
        
    def test_fix_date(self):
        date = '2014-12-31'
        result = self.mh.fix_date(date)
        expected = '12/31/2014'
        self.assertEqual(result, expected)
        
    def test_fix_date_blank(self):
        date = '  '
        result = self.mh.fix_date(date)
        expected = ''
        self.assertEqual(result, expected)
        
    def test_fix_dates(self):
        row = {'col0':0, 'Start Date': '2014-12-29', 'End Date': '2014-12-30', 'Member Since': '2014-12-31'}
        self.mh.fix_dates(row)
        expected = row.copy()
        expected.update({'Start Date': '12/29/2014', 'End Date': '12/30/2014', 'Member Since': '12/31/2014'})
        self.assertDictEqual(row, expected)
        
    def tearDown(self):
        pass


    def testName(self):
        pass


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
