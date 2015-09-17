'''
Created on 8 Sep 2015

@author:  julian

Crookes    Crookesmoor Road    odd        Broomhill    added (Spring Hill - Roslin Road)
Crookes    Crookesmoor Road    even    432-496    Broomhill
Crookes    Crookesmoor Road    even    356-430    Crookes & Crosspool
Crookes    Crookesmoor Road    even    2-428    Broomhill
'''
import unittest
from ward_update import Main, RegisterUpdater


class Test(unittest.TestCase):

    def setUp(self):
        self.main = Main()
        self.register_updater = RegisterUpdater()
        self.street_spec = [
                           {'ward_old':  'Crookes', 'street_name':  'Ash Ave' , 'odd_even': '' , 'numbers': '1,2,3,5,7' , 'ward_new':  'Broomhill Prime', 'notes':  '', },
                           {'ward_old':  'Crookes', 'street_name':  'Ash Ave' , 'odd_even': 'odd' , 'numbers': '1-9' , 'ward_new':  'Broomhill Nine', 'notes':  '', },
                           {'ward_old':  'Crookes', 'street_name':  'Ash Ave' , 'odd_even': 'even' , 'numbers': '1-9' , 'ward_new':  'Broomhill Even', 'notes':  '', },
                           {'ward_old':  'Crookes', 'street_name':  'Ash Ave' , 'odd_even': '' , 'numbers': '' , 'ward_new':  'Broomhill Ten', 'notes':  '', },
                           {'ward_old':  'Crookes', 'street_name':  'Beech Blvd' , 'odd_even': '' , 'numbers': '' , 'ward_new':  'Crookes & Crosspool', 'notes':  'added (Spring Hill - Roslin Road)', },
                           ]
        self.ward_lookup = {'Crookes': {
                             'Ash Ave': {'': 'Broomhill Ten', 1: 'Broomhill Prime', 2: 'Broomhill Prime', 3: 'Broomhill Prime', 4: 'Broomhill Even',
                                              5: 'Broomhill Prime', 6: 'Broomhill Even', 7: 'Broomhill Prime', 8: 'Broomhill Even', 9: 'Broomhill Nine', },
                             'Beech Blvd': {'': 'Crookes & Crosspool'},
                                        }}
        self.number_fieldname = 'add1'
        self.street_fieldname = 'add3'
        self.register = [
                       {'PD': 'HA', 'add1': '2', 'add2': '', 'add3': 'Ash Ave', },
                       {'PD': 'HA', 'add1': '3', 'add2': '', 'add3': 'Ash Ave', },
                       {'PD': 'HA', 'add1': '4a', 'add2': '', 'add3': 'Ash Ave', },
                       {'PD': 'HA', 'add1': '5', 'add2': '', 'add3': 'Ash Ave', },
                       {'PD': 'HA', 'add1': '', 'add2': '', 'add3': '6a Ash Ave', },
                       {'PD': 'HA', 'add1': '7', 'add2': '', 'add3': 'Ash Ave', },
                       {'PD': 'HA', 'add1': 'Flat 3', 'add2': '', 'add3': '8a Ash Ave', },
                       {'PD': 'HA', 'add1': '9', 'add2': '', 'add3': 'Ash Ave', },
                       {'PD': 'HA', 'add1': '10', 'add2': '', 'add3': 'Ash Ave', },
                       {'PD': 'HA', 'add1': '1', 'add2': '', 'add3': 'Beech Blvd', },
                       ]
        self.register_updated = [
                       {'PD': 'HA', 'add1': '2', 'add2': '', 'add3': 'Ash Ave', 'ward_new': 'Broomhill Prime', },
                       {'PD': 'HA', 'add1': '3', 'add2': '', 'add3': 'Ash Ave', 'ward_new': 'Broomhill Prime', },
                       {'PD': 'HA', 'add1': '4a', 'add2': '', 'add3': 'Ash Ave', 'ward_new': 'Broomhill Even', },
                       {'PD': 'HA', 'add1': '5', 'add2': '', 'add3': 'Ash Ave', 'ward_new': 'Broomhill Prime', },
                       {'PD': 'HA', 'add1': '', 'add2': '', 'add3': '6a Ash Ave', 'ward_new': 'Broomhill Even', },
                       {'PD': 'HA', 'add1': '7', 'add2': '', 'add3': 'Ash Ave', 'ward_new': 'Broomhill Prime', },
                       {'PD': 'HA', 'add1': 'Flat 3', 'add2': '', 'add3': '8a Ash Ave', 'ward_new': 'Broomhill Even', },
                       {'PD': 'HA', 'add1': '9', 'add2': '', 'add3': 'Ash Ave', 'ward_new': 'Broomhill Nine', },
                       {'PD': 'HA', 'add1': '10', 'add2': '', 'add3': 'Ash Ave', 'ward_new': 'Broomhill Ten', },
                       {'PD': 'HA', 'add1': '1', 'add2': '', 'add3': 'Beech Blvd', 'ward_new': 'Crookes & Crosspool', },
                       ]

    def test_RegisterUpdater_get_ward_lookup(self):
        ward_lookup = self.register_updater.get_ward_lookup(self.street_spec)
        print(ward_lookup)
        print(self.ward_lookup)
        self.assertDictEqual(ward_lookup, self.ward_lookup)

    def test_RegisterUpdater_get_street_number_and_name(self):
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
            actual = self.register_updater.get_street_number_and_name(row['street_number'], row['street_name'])
            self.assertTupleEqual(actual, row['expected'])

    def test_RegisterUpdater_is_in_ward(self):
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
            self.assertEqual(self.register_updater.is_in_ward_new(row['street_number'], row['odd_even'], row['numbers']), row['expected'],
                             (row['street_number'], row['odd_even'], row['numbers']))

    def test_RegisterUpdater_pd2ward(self):
        d = {'G': 'Central',
             'H': 'Crookes',
             'L': 'Ecclesall',
             'R': 'Manor Castle',
             'T': 'Nether Edge',
             'Z': 'Walkley',
        }
        for (k, v) in d.items():
            self.assertEqual(self.register_updater.pd2ward(k), v)

    def test_RegisterUpdater_rangeexpand(self):
        txt = '1-3,6,8-10'
        expected = {1, 2, 3, 6, 8, 9, 10}
        actual = self.register_updater.rangeexpand(txt)
        self.assertSetEqual(actual, expected)

    def test_RegisterUpdater_rangeexpand_odd_even(self):
        rows = [
              {'odd_even': '', 'numbers': '', 'expected': ('', set())},
              {'odd_even': '', 'numbers': '1-4', 'expected': ('', {1, 2, 3, 4, })},
              {'odd_even': 'odd', 'numbers': '', 'expected': ('odd', set())},
              {'odd_even': 'odd', 'numbers': '1-4', 'expected': ('', {1, 3, })},
              {'odd_even': 'even', 'numbers': '', 'expected': ('even', set())},
              {'odd_even': 'even', 'numbers': '1-4', 'expected': ('', {2, 4, })},
              ]
        for row in rows:
            actual = self.register_updater.rangeexpand_odd_even(row['odd_even'], row['numbers'])
            self.assertTupleEqual(actual, row['expected'])

    def test_RegisterUpdater_register_update(self):
        register_updated = self.register_updater.register_update(self.register, self.ward_lookup,
                                                                 self.number_fieldname, self.street_fieldname)
        self.assertListEqual(register_updated, self.register_updated)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
