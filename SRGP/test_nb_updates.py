'''
Created on 4 Feb 2015

@author: julian
'''
import unittest
from nb_updates import NbUpdates


class Test(unittest.TestCase):

    def setUp(self):
        r0 = {'a': 0, 'b': 1, 'c': 2, }
        r1 = {'a': 3, 'b': 4, 'c': 5, }
        r2 = {'a': 6, 'b': 7, 'c': 8, }
        r3 = {'a': 9, 'b': 10, 'c': 11, }
        r11 = {'a': 3, 'b': 4, 'c': 999, }
        self.r2 = r2
        self.r3 = r3
        self.r11 = r11
        self.t0 = [r0, r1, ]
        self.t1 = [r0, r11, r2, r3, ]
        self.d0 = {
            0: r0,
            3: r1,
        }
        self.d1 = {
            0: r0,
            3: r11,
            6: r2,
            9: r3,
        }
        self.nbkey = 'a'
        self.nu = NbUpdates(self.t0, self.t1, self.nbkey)

    def test_NbUpdates(self):
        self.assertListEqual(self.nu.t0, self.t0)
        self.assertListEqual(self.nu.t1, self.t1)
        self.assertEqual(self.nu.nbkey, self.nbkey)
        self.assertDictEqual(self.nu.d0, self.d0)
        self.assertDictEqual(self.nu.d1, self.d1)

    def test_table2dict(self):
        actual = NbUpdates.table2dict(self.t0, 'a')
        expected = self.d0
        self.assertDictEqual(actual, expected)

    def test_new(self):
        actual = self.nu.new()
        expected = [self.r2, self.r3]
        self.assertListEqual(actual, expected)

    def test_mod(self):
        actual = self.nu.mods()
        expected = [self.r11]
        self.assertListEqual(actual, expected)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testtable2dict']
    unittest.main()
