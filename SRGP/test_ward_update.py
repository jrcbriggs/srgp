'''
Created on 8 Sep 2015

@author:  julian

Crookes    Crookesmoor Road    odd        Broomhill    added (Spring Hill - Roslin Road)
Crookes    Crookesmoor Road    even    432-496    Broomhill
Crookes    Crookesmoor Road    even    356-430    Crookes & Crosspool
Crookes    Crookesmoor Road    even    2-428    Broomhill
'''

import numbers
import unittest

from csv_read import get_ward_lookup, TableWardUpdate, rangeexpand, \
    rangeexpand_odd_even, pd2ward


class Test(unittest.TestCase):


    def setUp(self):
        self.twu = TableWardUpdate()
        self.street_spec = [
                           {'ward_old':  'Crookes', 'street_name':  'Aldred Road' , 'odd_even': '' , 'numbers': '' , 'ward_new':  'Crookes & Crosspool', 'notes':  'added (Spring Hill - Roslin Road)', },
                           {'ward_old':  'Crookes', 'street_name':  'Boswell Road' , 'odd_even': '' , 'numbers': '1,2,3,5,7' , 'ward_new':  'Broomhill Prime', 'notes':  '', },
                           {'ward_old':  'Crookes', 'street_name':  'Boswell Road' , 'odd_even': 'odd' , 'numbers': '1-9' , 'ward_new':  'Broomhill Nine', 'notes':  '', },
                           {'ward_old':  'Crookes', 'street_name':  'Boswell Road' , 'odd_even': 'even' , 'numbers': '1-9' , 'ward_new':  'Broomhill Even', 'notes':  '', },
                           {'ward_old':  'Crookes', 'street_name':  'Boswell Road' , 'odd_even': '' , 'numbers': '' , 'ward_new':  'Broomhill Ten', 'notes':  '', },
                           ]
        self.ward_lookup = {'Crookes': {
                             'Aldred Road': {'': 'Crookes & Crosspool'},
                             'Boswell Road': {'': 'Broomhill Ten', 1: 'Broomhill Prime', 2: 'Broomhill Prime', 3: 'Broomhill Prime', 4: 'Broomhill Even',
                                              5: 'Broomhill Prime', 6: 'Broomhill Even', 7: 'Broomhill Prime', 8: 'Broomhill Even', 9: 'Broomhill Nine', }}}

    def tearDown(self):
        pass


    def test_pd2ward(self):
        d = {
            'EA': 'Broomhill',
            'GB': 'Central',
            'RC': 'Manor Castle',
            'TD': 'Nether Edge',
            'ZE': 'Walkley',
        }
        for (k, v) in d.items():
            self.assertEqual(pd2ward(k), v)

    def test_rangeexpand(self):
        txt = '1-3,6,8-10'
        expected = {1, 2, 3, 6, 8, 9, 10}
        actual = rangeexpand(txt)
        self.assertSetEqual(actual, expected)

    def test_rangeexpand_odd_even(self):
        rows = [
              {'odd_even': '', 'numbers': '', 'expected': ('', set())},
              {'odd_even': '', 'numbers': '1-4', 'expected': ('', {1, 2, 3, 4, })},
              {'odd_even': 'odd', 'numbers': '', 'expected': ('odd', set())},
              {'odd_even': 'odd', 'numbers': '1-4', 'expected': ('', {1, 3, })},
              {'odd_even': 'even', 'numbers': '', 'expected': ('even', set())},
              {'odd_even': 'even', 'numbers': '1-4', 'expected': ('', {2, 4, })},
              ]
        for row in rows:
            actual = rangeexpand_odd_even(row['odd_even'], row['numbers'])
            self.assertTupleEqual(actual, row['expected'])

    def test_get_ward_lookup(self):
        ward_lookup = get_ward_lookup(self.street_spec)
        print(ward_lookup)
        print(self.ward_lookup)
        self.assertDictEqual(ward_lookup, self.ward_lookup)

    def testTableWardUpdate_is_in_ward(self):
        ''' odd_even and numbers are pre-processed so either odd_even or numbers are set , never both
        '''
        rows = [
               {'street_number':  3, 'odd_even':  '', 'numbers':  [], 'expected': True},
               {'street_number': 3, 'odd_even':  '', 'numbers':  [1, 2, 3], 'expected': True},
               {'street_number': 3, 'odd_even':  '', 'numbers':  [1, 2], 'expected': False},

               {'street_number': 3, 'odd_even':  'odd', 'numbers':  [], 'expected': True},
               {'street_number': 2, 'odd_even':  'odd', 'numbers':  [], 'expected': False},
               #
               {'street_number': 2, 'odd_even':  'even', 'numbers':  [], 'expected': True},
               {'street_number': 3, 'odd_even':  'even', 'numbers':  [], 'expected': False},
               #
               ]
        for row in rows:
            self.assertEqual(self.twu.is_in_ward_new(row['street_number'], row['odd_even'], row['numbers']), row['expected'],
                             (row['street_number'], row['odd_even'], row['numbers']))

    def testTableWardUpdate_clean_street_number_and_name(self):
        rows = [
              {'street_number': '12', 'street_name': 'Ash Road', 'expected': (12, 'Ash Road')},
              {'street_number': '12a', 'street_name': 'Ash Road', 'expected': (12, 'Ash Road')},
              {'street_number': '12A', 'street_name': 'Ash Road', 'expected': (12, 'Ash Road')},
              {'street_number': '12-14', 'street_name': 'Ash Road', 'expected': (12, 'Ash Road')},
              {'street_number': '12/14', 'street_name': 'Ash Road', 'expected': (12, 'Ash Road')},
              {'street_number': '', 'street_name': 'Ash Road', 'expected': (0, 'Ash Road')},
              {'street_number': 'Ant House', 'street_name': 'Ash Road', 'expected': (0, 'Ash Road')},
              {'street_number': 'Flat 7', 'street_name': '12 Ash Road', 'expected': (12, 'Ash Road')},
              {'street_number': 'Flat 7', 'street_name': '12a Ash Road', 'expected': (12, 'Ash Road')},
              {'street_number': 'Flat 7', 'street_name': '12A Ash Road', 'expected': (12, 'Ash Road')},
              {'street_number': 'Flat 7', 'street_name': '12-14 Ash Road', 'expected': (12, 'Ash Road')},
              {'street_number': 'Flat 7', 'street_name': '12/14 Ash Road', 'expected': (12, 'Ash Road')},
              ]
        for row in rows:
            actual = self.twu.clean_street_number_and_name(row['street_number'], row['street_name'])
            self.assertTupleEqual(actual, row['expected'])


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
