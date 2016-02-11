#!/usr/bin/python3
'''
Created on 7 Feb 2016

@author: julian
'''
from collections import OrderedDict as OD
import unittest

from csv_fixer2 import TableFixer

class Test(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.pd = 'EA'
        self.eno = '12'
        self.statefile_id = 'EA0012'
        self.first_name = 'Julian'
        self.last_name = 'Briggs'
        self.fieldnames = ['fieldname1', 'fieldname2']
        self.housename = 'Avalon'
        self.street_number = '34'
        self.street_name = 'Acacia Ave'
        self.block_name = 'Millsands'
        self.party_map = {'LD':'D', }
        self.support_level_map = {'LD':5, }
        self.row0 = {'polldist': self.pd,
                    'elect no': self.eno,
                    'Notes': 'n1',
                    'Surname': self.last_name,
                    'First name': self.first_name,
                    'Comments': 'c1',
                    'Housename': '',
                    'Number': self.street_number,
                    'Road': self.street_name,
                    'Block': self.block_name,
                    'Addend': '',
                    'Postcode': '',
                    'Party':'LD',
                    'Demographic':'stdt,Post',
                    'national':'',
                    'Local':'',
                    'Post':'',
                    'Vote14':'',
                    'Phone':'',
                    'E-mail':'',
                    'Vote12':'',
                    }
        self.row1 = {'statefile_id': self.statefile_id,
                    'last_name': self.last_name,
                    'first_name': self.first_name,
                    'registered_address1': self.street_number + ' ' + self.street_name,
                    'registered_address2': self.block_name,
                    'registered_address3': None,
                    'registered_city': '',
                    'registered_zip': '',
                    'background': 'n1 c1',
                    'phone_number': '',
                    'email': '',
                    'party': 'D',
                    'support_level': 5,
                    'tag_list': 'Postal14,student15',
                    }
        self.tag_map = {'':'', 'A':'a', 'B':'b', 'C':'c', 'D':'d', }
        self.tag_map1 = {
                         '':'',
                         'Case': 'casework15 ',
                        'Poster': 'poster15',
                        'stdt': 'student15',
                        'Ben': 'Benefits',
                        'Crime':'Crime',
                        'Litter':'Litter',
                        'Recyc':'Recycling',
                        '20mph': '20mph',
                        'Lib':'Library',
                        'Plan':'Planning',
                        'ResPark':'ResidentsParking',
                        'StrtAhed':'StreetsAhead',
                        'Traf': 'Traffic',
                        'Post': 'Postal14',
                        'Vote14': 'Vote14',
                        'Vote12': 'Vote12',
                        }
        # 1st element in tuple is class method
        self.config = OD([
                            ('statefile_id', (TableFixer.merge_pd_eno, [], {'pd':'polldist', 'eno':'elect no', },)),
                            ('last_name', 'Surname'),
                            ('first_name', 'First name'),
                            ('registered_address1', (TableFixer.fix_address1, [], {
                                                          'housename':'Housename',
                                                          'street_number':'Number',
                                                          'street_name':'Road',
                                                          })),
                            ('registered_address2', (TableFixer.fix_address2, [], {
                                                          'block_name':'Block',
                                                          })),
                            ('registered_address3', None),
                            ('registered_city', 'Addend'),
                            ('registered_zip', 'Postcode'),
                            ('background', (TableFixer.background_merge, [], {'notes':'Notes',
                                                              'comments':'Comments'})),
                            ('phone_number', 'Phone'),
                            ('email', 'E-mail'),
                            ('party', (TableFixer.fix_party, [self.party_map], {'party':'Party', })),
                            ('support_level', (TableFixer.fix_support_level, [self.support_level_map], {'support_level':'Party', })),
                            ('tag_list', (TableFixer.tags_add, [self.tag_map1], {'k0': 'Demographic',
                                                                                 'k1': 'national',
                                                                                 'k2': 'Local',
                                                                                 'k3': 'Post',
                                                                                 'k4': 'Vote14',
                                                                                 'k5': 'Vote12',
                                                                                 })),
                          ])
        self.table0 = [self.row0]
        self.table1 = [self.row1]
        self.tf = TableFixer(config=self.config, table0=self.table0)  # , table0=[self.row0])

    def test_background_merge(self):
        actual = TableFixer.background_merge(notes='n1', comments='c1')
        expected = 'n1 c1'
        self.assertEqual(actual, expected)

    def test_fix_table(self):
        actual = self.tf.fix_table()
        expected = self.table1
        self.assertListEqual(actual, expected)

    def test_fix_row(self):
        actual = self.tf.fix_row(self.row0)
        expected = self.row1
        self.assertDictEqual(actual, expected)

    def test_fix_field_str(self):
        fieldname1 = 'first_name'
        arg0 = 'First name'
        row0 = {'First name': self.first_name}
        actual = TableFixer.fix_field(row0, arg0)
        expected = self.first_name
        self.assertEqual(actual, expected)

    def test_fix_field_func(self):
        fieldname1 = 'statefile_id'
        row0 = {'polldist':self.pd, 'elect no':self.eno}
        arg0 = (TableFixer.merge_pd_eno, [], {'pd':'polldist', 'eno':'elect no'})
        actual = TableFixer.fix_field(row0, arg0)
        expected = self.statefile_id
        self.assertEqual(actual, expected)

    def test_fix_field_exception(self):
        '''First element  of tuple should be str or a callable
        '''
        fieldname1 = 'statefile_id'
        arg0 = (123, {'pd':'pd', 'eno':'eno'})
        row0 = {'pd': self.pd, 'eno':self.eno, }
        self.assertRaises(TypeError, TableFixer.fix_field, arg0, row0)

    def test_fix_address1(self):
        actual = TableFixer.fix_address1(housename='', street_number=self.street_number, street_name=self.street_name)
        expected = self.street_number + ' ' + self.street_name
        self.assertEqual(actual, expected)

    def test_fix_address1_house_name(self):
        actual = TableFixer.fix_address1(housename=self.housename, street_number='', street_name=self.street_name)
        expected = self.housename + '  ' + self.street_name
        self.assertEqual(actual, expected)

    def test_fix_address2(self):
        actual = TableFixer.fix_address2(block_name=self.block_name)
        expected = self.block_name
        self.assertEqual(actual, expected)

    def test_doa2dob(self):
        actual = TableFixer.doa2dob(doa='31/12/2018')
        expected = '12/31/2000'
        self.assertEqual(actual, expected)

    def test_fix_party(self):
        actual = TableFixer.fix_party(self.party_map, 'LD')
        expected = 'D'
        self.assertEqual(actual, expected)

    def test_fix_support_level(self):
        actual = TableFixer.fix_support_level(self.support_level_map, 'LD')
        expected = 5
        self.assertEqual(actual, expected)

    def test_merge_pd_eno(self):
        actual = TableFixer.merge_pd_eno(pd=self.pd, eno=self.eno)
        expected = self.statefile_id
        self.assertEqual(actual, expected)

    def test_merge_pd_eno_bad_eno(self):
        self.row0['elect no'] = None
        self.assertRaises(TypeError, TableFixer.merge_pd_eno, pd=self.pd, eno=None)

    def test_merge_pd_eno_bad_pd(self):
        self.row0['polldist'] = None
        self.assertRaises(TypeError, TableFixer.merge_pd_eno, pd=None, eno=self.eno)

    def test_tags_add(self):
        actual = TableFixer.tags_add(self.tag_map, k0='A,B', k1='C', k2='')
        expected = 'a,b,c'
        self.assertEqual(actual, expected)

    def test_tags_split(self):
        fieldvalue = 'A,B'
        actual = TableFixer.tags_split(self.tag_map, fieldvalue)
        expected = ['a', 'b']
        self.assertEqual(actual, expected, actual)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
