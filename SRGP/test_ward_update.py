'''
Created on 8 Sep 2015

@author: julian
'''

import unittest
from ward_update import street_names2ward_street_name
class Test(unittest.TestCase):


    def setUp(self):
        self.street_names = [
                           {'ward_old': 'Crookes', 'street_name': 'Aldred Road' , 'odds_evens':'' , 'numbers':'' , 'ward_new': 'Crookes & Crosspool', 'notes': '', },
                           ]
        self.street_spec = {
                            ('Crookes', 'Aldred Road'): [{'notes': '',
                                                         'numbers': '',
                                                         'odds_evens': '',
                                                         'street_name': 'Aldred Road',
                                                         'ward_new': 'Crookes & Crosspool',
                                                         'ward_old': 'Crookes'}]}

    def tearDown(self):
        pass


    def test_street_names2ward_street_name(self):
        street_spec = street_names2ward_street_name(self.street_names)
        self.assertDictEqual(street_spec, self.street_spec)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
