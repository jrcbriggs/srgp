'''
Created on 8 Sep 2015

@author: julian

Crookes    Crookesmoor Road    odds        Broomhill    added (Spring Hill - Roslin Road) 
Crookes    Crookesmoor Road    evens    432-496    Broomhill    
Crookes    Crookesmoor Road    evens    356-430    Crookes & Crosspool    
Crookes    Crookesmoor Road    evens    2-428    Broomhill    
'''

import unittest
from ward_update import street_names2ward_street_name
class Test(unittest.TestCase):


    def setUp(self):
        self.street_names = [
                           {'ward_old': 'Crookes', 'street_name': 'Aldred Road' , 'odds_evens':'' , 'numbers':'' , 'ward_new': 'Crookes & Crosspool', 'notes': 'added (Spring Hill - Roslin Road)', },
                           {'ward_old': 'Crookes', 'street_name': 'Crookesmoor Road' , 'odds_evens':'odds' , 'numbers':'' , 'ward_new': 'Broomhill', 'notes': '', },
                           {'ward_old': 'Crookes', 'street_name': 'Crookesmoor Road' , 'odds_evens':'evens' , 'numbers':'490-496' , 'ward_new': 'Broomhill', 'notes': '', },
                           {'ward_old': 'Crookes', 'street_name': 'Crookesmoor Road' , 'odds_evens':'evens' , 'numbers':'356-460' , 'ward_new': 'Crookes & Crosspool', 'notes': '', },
                           {'ward_old': 'Crookes', 'street_name': 'Crookesmoor Road' , 'odds_evens':'evens' , 'numbers':'422-428' , 'ward_new': 'Broomhill', 'notes': '', },
                           ]
        self.street_spec = {
                            ('Crookes', 'Aldred Road'): [{'notes': 'added (Spring Hill - Roslin Road)', 'street_name': 'Aldred Road', 'ward_new': 'Crookes & Crosspool', 'numbers': (), 'ward_old': 'Crookes', 'odds_evens': ''}], 
                            ('Crookes', 'Crookesmoor Road'): [{'notes': '', 'street_name': 'Crookesmoor Road', 'ward_new': 'Broomhill', 'numbers': (), 'ward_old': 'Crookes', 'odds_evens': 'odds'}, 
                                                              {'notes': '', 'street_name': 'Crookesmoor Road', 'ward_new': 'Broomhill', 'numbers': tuple(range(490,497)), 'ward_old': 'Crookes', 'odds_evens': 'evens'}, 
                                                              {'notes': '', 'street_name': 'Crookesmoor Road', 'ward_new': 'Crookes & Crosspool', 'numbers': tuple(range(356,461)), 'ward_old': 'Crookes', 'odds_evens': 'evens'}, 
                                                              {'notes': '', 'street_name': 'Crookesmoor Road', 'ward_new': 'Broomhill', 'numbers': tuple(range(422,429)), 'ward_old': 'Crookes', 'odds_evens': 'evens'}]}


    def tearDown(self):
        pass


    def test_street_names2ward_street_name(self):
        street_spec = street_names2ward_street_name(self.street_names)
        print(self.street_spec)
        print(street_spec)        
        self.assertDictEqual(street_spec, self.street_spec)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
