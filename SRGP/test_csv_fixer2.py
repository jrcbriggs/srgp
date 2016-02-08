'''
Created on 7 Feb 2016

@author: julian
'''
from collections import OrderedDict as OD
import unittest

import configurations2
from csv_fixer2 import TableFixer


class Test(unittest.TestCase):

    def setUp(self):
        self.maxDiff = True
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
                    'Demographic':'stdt',
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
                    'tag_list': 'student15,,,,,',
                    }
        self.tag_map = {'':'', 'A':'a', 'B':'b', 'C':'c', 'D':'d', }
        self.tag_map1 = {'':'',
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
                            ('statefile_id', (TableFixer.merge_pd_eno, {'pd':'polldist', 'eno':'elect no', },)),
                            ('last_name', 'Surname'),
                            ('first_name', 'First name'),
                            ('registered_address1', (TableFixer.fix_address1, {
                                                          'housename':'Housename',
                                                          'street_number':'Number',
                                                          'street_name':'Road',
                                                          })),
                            ('registered_address2', (TableFixer.fix_address2, {
                                                          'block_name':'Block',
                                                          })),
                            ('registered_address3', None),
                            ('registered_city', 'Addend'),
                            ('registered_zip', 'Postcode'),
                            ('background', (TableFixer.background_merge, {'notes':'Notes',
                                                              'comments':'Comments'})),
                            ('phone_number', 'Phone'),
                            ('email', 'E-mail'),
                            ('tag_list', (TableFixer.tags_add, {'fieldnames': ('Demographic',
                                                                                  'national',
                                                                                  'Local',
                                                                                  'Post',
                                                                                  'Vote14',
                                                                                  'Vote12',
                                                                                  ),
                                                                    'tag_map': self.tag_map1, })),
#                             ('', 'Date'),
#                             ('', 'OnReg'),
#                             ('', 'Lastvote'),
                          ])
        self.table0 = [self.row0]
        self.table1 = [self.row1]
        self.tf = TableFixer(config=self.config, table0=self.table0)  # , table0=[self.row0])

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
        fieldname0 = 'First name'
        row0 = {'First name': self.first_name}
        actual = TableFixer.fix_field(fieldname0, row0)
        expected = self.first_name
        self.assertEqual(actual, expected)

    def test_fix_field_func(self):
        fieldname1 = 'statefile_id'
        fieldname0 = (TableFixer.merge_pd_eno, {'pd':'polldist', 'eno':'elect no'})
        row0 = {'polldist':self.pd, 'elect no':self.eno}
        actual = TableFixer.fix_field(fieldname0, row0)
        expected = self.statefile_id
        self.assertEqual(actual, expected)

    def test_field_fix_exception(self):
        fieldname1 = 'statefile_id'
        fieldname0 = (123, {'pd':'pd', 'eno':'eno'})
        row0 = {'pd': self.pd, 'eno':self.eno, }
        self.assertRaises(TypeError, TableFixer.fix_field, fieldname0, row0)

    def test_merge_pd_eno(self):
        actual = TableFixer.merge_pd_eno(self.row0, pd='polldist', eno='elect no')
        expected = self.statefile_id
        self.assertEqual(actual, expected)

    def test_fix_address1(self):
        actual = TableFixer.fix_address1(self.row0, housename='Housename',
                                             street_number='Number', street_name='Road')
        expected = self.street_number + ' ' + self.street_name
        self.assertEqual(actual, expected)

    def test_fix_address1_house_name(self):
        self.row0['Housename'] = self.housename
        self.row0['Number'] = ''
        actual = TableFixer.fix_address1(self.row0, housename='Housename',
                                             street_number='Number', street_name='Road')
        expected = self.housename + '  ' + self.street_name
        self.assertEqual(actual, expected)

    def test_fix_address2(self):
        actual = TableFixer.fix_address2(self.row0, block_name='Block')
        expected = self.block_name
        self.assertEqual(actual, expected)

    def test_background_merge(self):
        actual = TableFixer.background_merge(self.row0, notes='Notes', comments='Comments')
        expected = 'n1 c1'
        self.assertEqual(actual, expected)

    def test_tags_add(self):
        row0 = {            'fieldname1': 'A,B',
                    'fieldname2': 'C', }
        actual = TableFixer.tags_add(row0, fieldnames=self.fieldnames, tag_map=self.tag_map)
        expected = 'a,b,c'
        self.assertEqual(actual, expected)

    def test_tags_split(self):
        fieldvalue = 'A,B'
        actual = TableFixer.tags_split(fieldvalue, self.tag_map)
        expected = 'a,b'
        self.assertEqual(actual, expected, actual)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
