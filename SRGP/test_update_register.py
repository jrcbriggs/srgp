'''
Created on 24 Feb 2015

@author: ph1jb
'''
import unittest
from update_register import UpdateRegister
from pprint import pprint
from plainbox.impl.commands import selftest


class Test(unittest.TestCase):

    def setUp(self):
        self.k0 = 'a'
        self.k1 = 'b'
        self.status = 's'
        self.row0 = {'s': 'E', 'a': 0, 'b': 1, 'c': 2, }  # update deletes this
        # update changes c from 5 to 9
        self.row1 = {'s': 'E', 'a': 3, 'b': 4, 'c': 5, }
        # update ignores this
        self.row2 = {'s': 'E', 'a': 13, 'b': 14, 'c': 15, }
        self.l0 = [self.row0, self.row1, self.row2]

        self.row3 = {'s': 'A', 'a': 6, 'b': 7, 'c': 8, }  # updates adds this
        self.row4 = {'s': 'D', 'a': 0, 'b': 1, 'c': 2, }  # delete row0
        self.row5 = {'s': 'M', 'a': 3, 'b': 4, 'c': 9, }  # modify row1
        self.l1 = [self.row3, self.row4, self.row5]
        self.ud = UpdateRegister(self.l0, self.l1, self.k0, self.k1, self.status)
        self.d0 = {(0, 1): self.row0, (3, 4): self.row1, (13, 14): self.row2}
        self.d1 = {(6, 7): self.row3, (0, 1): self.row4, (3, 4): self.row5}

    def tearDown(self):
        pass

    def test_ld2dd(self):
        actual = self.ud.table2dict(self.l0, self.k0, self.k1)
        expected = self.d0
        self.assertDictEqual(actual, expected)
        actual = self.ud.table2dict(self.l1, self.k0, self.k1)
        expected = self.d1
        self.assertDictEqual(actual, expected)

    def test_update(self):
        actual = self.ud.update(self.d0, self.d1, self.status)
        expected = {(13, 14): self.row2, (6, 7): self.row3,
                    (3, 4): self.row5, }
        self.assertDictEqual(actual, expected)

    def test_dict2table(self):
        actual = self.ud.dict2table(self.d0)
        expected = [self.row0, self.row1, self.row2]
        self.assertListEqual(actual, expected)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
