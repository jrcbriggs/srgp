#!/usr/bin/python3
'''
Created on 7 Feb 2016

@author: julian
'''
from collections import OrderedDict as OD
import unittest
from unittest.mock import MagicMock

from csv_fixer2 import AddressHandler as AD, Canvass as CN, Generic as GN, Member as MB, Register as RG, TableFixer as TF, Voter as VT
from csv_fixer2 import CsvFixer, FileHandler, Main
import csv_fixer2
from unittest.case import skip

class TestFileHandler(unittest.TestCase):
    def setUp(self):
        self.fieldnames = ('A', 'B',)
        self.filehandler = FileHandler()
        self.pathname = '/tmp/test.py'
        self.table0 = [{'A':'a', 'B':'b', },
                      {'A':'c', 'B':'d', }]

    def test_csv_read(self):
        self.filehandler.csv_write(self.table0, self.pathname, self.fieldnames)
        table1 = self.filehandler.csv_read(self.pathname)
        self.assertListEqual(table1, self.table0)

class TestCsvFixer(unittest.TestCase):
    def setUp(self):
        self.csvfixer = CsvFixer()
        self.fieldnames = ('A', 'B',)
        self.fh = FileHandler()
        self.pathname = '/tmp/test.py'
        self.config = OD([
                          ('AA', 'A'),
                          ('BB', 'B'), ])
        self.table0 = [{'A':'a', 'B':'b', },
                      {'A':'c', 'B':'d', }]

        self.table0 = [{'AA':'a', 'BB':'b', },
                      {'AA':'c', 'BB':'d', }]

    def test_csv_read(self):
        self.csvfixer.fix_csv(self.pathname, self.config, self.fh.csv_read, self.fh.csv_write)
        table1 = self.fh.csv_read(self.pathname)
        self.assertListEqual(table1, self.table0)

class TestTableFixer(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.pd = 'EA'
        self.eno = '12'
        self.statefile_id = 'EA0012'
        self.first_name = 'Julian'
        self.row0 = {'polldist': self.pd,
                    'elect no': self.eno,
                    'First name': self.first_name,
                    'TagCol0': 'A,B',
                    'TagCol1': 'C,D',
                    }
        self.row1 = {'statefile_id': self.statefile_id,
                    'first_name': self.first_name,
                    'tag_list': 'a,b,c,d',
                    }
        self.tag_map = {'':'', 'A':'a', 'B':'b', 'C':'c', 'D':'d', }
        self.config = OD([
                            # 1st element in tuple is class method
                            ('statefile_id', (VT.merge_pd_eno, [], {'pd':'polldist', 'eno':'elect no', },)),
                            ('first_name', 'First name'),
                            ('tag_list', (GN.tags_add, [self.tag_map], {'k0': 'TagCol0',
                                                                        'k1': 'TagCol1',
                                                                         })),
                          ])
        self.table0 = [self.row0]
        self.table1 = [self.row1]
        self.tf = TF(config=self.config)

    def test_fix_table(self):
        actual = self.tf.fix_table(table0=self.table0)
        expected = self.table1
        self.assertListEqual(actual, expected)

    @skip
    def test_fix_table_bad(self):
        self.row0['TagCol0'] = 'XXX'
        self.assertRaises(KeyError, self.tf.fix_table, table0=self.table0)

    def test_fix_row(self):
        actual = self.tf.fix_row(self.row0)
        expected = self.row1
        self.assertDictEqual(actual, expected)

    @skip
    def test_fix_row_bad(self):
        self.row0['TagCol0'] = 'XXX'
        self.assertRaises(KeyError, self.tf.fix_row, self.row0)

    def test_fix_field_str(self):
        arg0 = 'First name'
        row0 = {'First name': self.first_name}
        actual = self.tf.fix_field(row0, arg0)
        expected = self.first_name
        self.assertEqual(actual, expected)

    def test_fix_field_arg0_none(self):
        arg0 = None
        row0 = {'First name': self.first_name}
        actual = self.tf.fix_field(row0, arg0)
        expected = None
        self.assertEqual(actual, expected)

    def test_fix_field_func(self):
        row0 = {'polldist':self.pd, 'elect no':self.eno}
        arg0 = (VT.merge_pd_eno, [], {'pd':'polldist', 'eno':'elect no'})
        actual = self.tf.fix_field(row0, arg0)
        expected = self.statefile_id
        self.assertEqual(actual, expected)

    def test_fix_field_bad_key1(self):
        '''First element  of tuple should be str or a callable
        '''
        row0 = {'pd': self.pd, 'eno':self.eno, }
        arg0 = (123, [], {'pd':'pd', 'eno':'eno'})
        self.assertRaises(TypeError, self.tf.fix_field, row0, arg0)

    def test_fix_field_bad_key0(self):
        '''First element  of tuple should be str or a callable
        '''
        row0 = {'pd': self.pd, 'eno':self.eno, }
        arg0 = (123, [], {'pd':'pdXXX', 'eno':'eno'})
        self.assertRaises(TypeError, self.tf.fix_field, row0, arg0)

class TestMain(unittest.TestCase):
    def setUp(self):
        self.fieldnames = ('A', 'B',)
        self.fh = FileHandler()
        self.pathname = '/tmp/test.py'
        self.config_test = OD([
                          ('config_name', 'config_test'),
                          ('AA', 'A'),
                          ('BB', 'B'), ])
        self.table0 = [{'A':'a', 'B':'b', },
                      {'A':'c', 'B':'d', }]

        self.table0 = [{'AA':'a', 'BB':'b', },
                      {'AA':'c', 'BB':'d', }]
        csv_fixer2.config_test = self.config_test
        self.config_lookup = [
                         ('BroomhillCanvassData', self.config_test),
                         ]
        self.main = Main(config_lookup=self.config_lookup)
        self.filename = 'BroomhillCanvassData'

    def test__init__(self):
        fh = self.main.fh
        self.assertIsInstance(fh, FileHandler)
        self.assertEqual(self.main.filereader, fh.csv_read)
        self.assertEqual(self.main.filewriter, fh.csv_write)

    def test_main(self):
        filenames = [t[0] for t in self.config_lookup]
        self.main.fix_csv = MagicMock()
        self.main.main(filenames)
        self.main.fix_csv.assert_called_any_with('BroomhillCanvassData', self.config_test)

    def test_main_config_not_found(self):
        self.assertRaises(AttributeError, self.main.main, 'XXX')

    def test_fix_csv(self):
        self.main.csv_fixer.fix_csv = MagicMock()
        self.main.fix_csv(self.filename, self.config_test)
        self.main.csv_fixer.fix_csv.assert_called_once_with(self.filename, self.config_test,
                                                            filereader=self.main.filereader, filewriter=self.main.filewriter)

#########################################################################################################
# #Field Mapping class methods
#########################################################################################################

class TestGeneric(unittest.TestCase):
    def setUp(self):
        self.tag_map = {'':'', 'A':'a', 'B':'b', 'C':'c', 'D':'d', }

    def test_doa2dob(self):
        actual = GN.doa2dob(doa='31/12/2018')
        expected = '12/31/2000'
        self.assertEqual(actual, expected)

    def test_doa2dob_empty(self):
        actual = GN.doa2dob(doa='')
        expected = ''
        self.assertEqual(actual, expected)

    def test_fix_date(self):
        actual = GN.fix_date(date='31/12/1956')
        expected = '12/31/1956'
        self.assertEqual(actual, expected)
        
    def test_fix_date_empty(self):
        actual = GN.fix_date(date='')
        expected = ''
        self.assertEqual(actual, expected)
        
    def test_tags_add(self):
        actual = GN.tags_add(self.tag_map, k0='A,B', k1='C', k2='')
        expected = 'a,b,c'
        self.assertEqual(actual, expected)
    
    @skip
    def test_tags_add_key_error(self):
        self.assertRaises(KeyError, GN.tags_add, self.tag_map, k0='A,B,XXX')

    def test_tags_split(self):
        fieldvalue = 'A,B'
        actual = GN.tags_split(self.tag_map, fieldvalue)
        expected = ['a', 'b']
        self.assertEqual(actual, expected, actual)

    def test_tags_split_bad_key(self):
        k0 = 'A,B,XXX'
        self.assertRaises(KeyError, GN.tags_split, self.tag_map, k0)

class TestVoter(unittest.TestCase):
    '''Common to register and canvassing
    '''
    def setUp(self):
        self.pd = 'EA'
        self.eno = '12'
        self.statefile_id = 'EA0012'
        self.party_map = {'LD':'D', }
        self.support_level_map = {'LD':5, }

    def test_merge_pd_eno(self):
        actual = VT.merge_pd_eno(pd=self.pd , eno=self.eno)
        expected = self.statefile_id
        self.assertEqual(actual, expected)

    def test_merge_pd_eno_bad_eno(self):
        self.assertRaises(TypeError, VT.merge_pd_eno, pd=self.pd, eno=None)

    def test_eno_pad_bad_eno(self):
        self.assertRaises(TypeError, VT.eno_pad, eno=None)

    def test_fix_party(self):
        actual = VT.fix_party(self.party_map, 'LD')
        expected = 'D'
        self.assertEqual(actual, expected)

    def test_fix_support_level(self):
        actual = VT.fix_support_level(self.support_level_map, 'LD')
        expected = 5
        self.assertEqual(actual, expected)

    def test_state_get(self):
        actual = VT.state_get()
        expected = 'Sheffield'
        self.assertEqual(actual, expected)

class TestCanvass(unittest.TestCase):
    def setUp(self):
        self.housename = 'Avalon'
        self.street_number = '34'
        self.street_name = 'Acacia Ave'
        self.block_name = 'Millsands'
        self.party_map = {'LD':'D', }
        self.support_level_map = {'LD':5, }

    def test_background_merge(self):
        actual = CN.background_merge(notes='n1', comments='c1')
        expected = 'n1 c1'
        self.assertEqual(actual, expected)

    def test_fix_address1(self):
        actual = CN.fix_address1(housename='', street_number=self.street_number, street_name=self.street_name)
        expected = self.street_number + ' ' + self.street_name
        self.assertEqual(actual, expected)

    def test_fix_address1_house_name(self):
        actual = CN.fix_address1(housename=self.housename, street_number='', street_name=self.street_name)
        expected = self.housename + '  ' + self.street_name
        self.assertEqual(actual, expected)

    def test_fix_address2(self):
        actual = CN.fix_address2(block_name=self.block_name)
        expected = self.block_name
        self.assertEqual(actual, expected)

class TestRegister(unittest.TestCase):
    
    def setUp(self):
        self.kwargs = {'add1':'A', 'add2':'B', 'add3':'C', 'add4':'D', 'add5':'E'}

    def test_tags_add_voter(self):
        tag_map_voter = {'K':'k', 'E':'European', }
        pd = 'EA'
        status = 'K'
        franchise = 'E'
        actual = RG.tags_add_voter(tag_map_voter, PD=pd, Status=status, Franchise=franchise)
        expected = 'Franchise=European,PD=EA,Status=k'
        self.assertEqual(actual, expected)

    def test_country_code_get(self):
        self.assertEqual(RG.country_code_get(), 'GB')

    def test_city_get(self):
        self.assertEqual(RG.city_get(), 'Sheffield')

    def test_ward_get(self):
        ward_lookup = {'E': 'Broomhill', }
        self.assertEqual(RG.ward_get(ward_lookup, pd='EA'), 'Broomhill')
        self.assertRaises(KeyError, RG.ward_get, ward_lookup, pd='9')
        self.assertRaises(IndexError, RG.ward_get, ward_lookup, pd='')

class TestAddressHandler(unittest.TestCase):
    '''
    Split register addresses into NationBuilder fields (address1, address2, address3, city, postcode)
    Sample addresses:
    [['21, Botanical Road', 'Sheffield' ],
    ['1, Woodbank Croft', '51, Botanical Road', 'Sheffield' ],
    ['Flat 9', 'Broomgrove Trust N H', '30, Broomgrove Road', 'Sheffield' ],
    ['Mackenzie House', '6, Mackenzie Crescent', 'Broomhall', 'Sheffield', 'Sheffield' ],
    ['Flat 110', 'Watsons Chambers', '5 - 15, Market Place', 'City Centre', 'Sheffield', 'Sheffield'],
    ['Flat 4', '108, Sellers Wheel', 'Arundel Lane', 'Sheffield',],
    ['220', 'Stannington View Road', 'Sheffield',],
    ]
    '''
    def setUp(self):
        self.addresses = [
                    {'k0':'21, Botanical Road', 'k1': 'Sheffield', },
                    {'k0':'1, Woodbank Croft', 'k1': '51, Botanical Road', 'k2': 'Sheffield', },
                    {'k0':'Flat 9', 'k1': 'Broomgrove Trust N H', 'k2': '30, Broomgrove Road', 'k3': 'Sheffield', },
                    {'k0':'Mackenzie House', 'k1': '6, Mackenzie Crescent', 'k2': 'Broomhall', 'k3': 'Sheffield', 'k4': 'S1 1AB' , },
                    {'k0':'Flat 110', 'k1': 'Watsons Chambers', 'k2': '5 - 15 Market Place', 'k3': 'City Centre', 'k4': 'Sheffield', 'k5': 'S1 1AB', },
                    {'k0':'Flat 4', 'k1': '108, Sellers Wheel', 'k2': 'Arundel Lane', 'k3': 'Sheffield', 'k4': 'S1 1AB', },
                    {'k0':'220', 'k1': 'Stannington View Road', 'k2': 'Sheffield', 'k3':'S10 1ST', },  # k3 is null value
                    {'k0':'220', 'k1': 'Stannington View Road', 'k2': '', 'k3':'Sheffield', 'k4': '', },  # k2 is block
                    ]
        self.nb_fields = [
                {'address1': '21, Botanical Road', 'city':'Sheffield', 'postcode':None, },
                {'address1': '51, Botanical Road', 'address2': '1, Woodbank Croft', 'city':'Sheffield', },
                {'address1': '30, Broomgrove Road', 'address2': 'Flat 9 Broomgrove Trust N H', 'city':'Sheffield', },
                {'address1': '6, Mackenzie Crescent', 'address2': 'Mackenzie House', 'address3': 'Broomhall', 'city':'Sheffield', 'postcode':'S1 1AB', },
                {'address1': '5 - 15 Market Place', 'address2': 'Flat 110 Watsons Chambers', 'address3': 'City Centre', 'city':'Sheffield', 'postcode':'S1 1AB', },
                {'address1': 'Arundel Lane', 'address2': 'Flat 4 108, Sellers Wheel', 'city':'Sheffield', 'postcode':'S1 1AB', },
                {'address1': '220 Stannington View Road', 'city':'Sheffield', 'postcode':'S10 1ST', },
                {'address1': '220 Stannington View Road', 'city':'Sheffield',  },
                ]

    def test_address_get(self):
        for (kwargs, expected) in zip(self.addresses, self.nb_fields):
            for key in ('address1', 'address2', 'address3', 'city', 'postcode',):
                actual = AD.address_get(key, **kwargs)
                self.assertEqual(actual, expected.get(key), 'key:{}  kwargs:{}'.format(key, kwargs))
    
class TestMember(unittest.TestCase):
    def test_fix_date(self):
        actual = MB.fix_date(date='1956-12-31')
        expected = '12/31/1956'
        self.assertEqual(actual, expected)
        
    def test_fix_date_empty(self):
        actual = MB.fix_date(date='')
        expected = ''
        self.assertEqual(actual, expected)

    def test_get_party(self):
        actual = MB.get_party()
        expected = 'G'
        self.assertEqual(actual, expected)

    def test_get_party_member(self):
        for (k,v) in {
                'Current':True,
                'Cancelled':False,
                'Deceased':False,
                'Expired':False,
                'Grace':True,
                'New':True,
                }.items():
            actual = MB.get_party_member(status=k)
            expected = v
            self.assertEqual(actual, expected)

    def test_get_status(self):
        for (k,v) in {
                'Current':'active',
                'Cancelled':'canceled',
                'Deceased':'deceased',
                'Expired':'expired',
                'Grace':'grace period',
                'New':'active',
                }.items():
            actual = MB.get_status(status=k)
            expected = v
            self.assertEqual(actual, expected)

    def test_get_support_level(self):
        for (k,v) in {
                'Current':1,
                'Cancelled':4,
                'Deceased':None,
                'Expired':2,
                'Grace':1,
                'New':1,
                }.items():
            actual = MB.get_support_level(status=k)
            expected = v
            self.assertEqual(actual, expected)

    def test_is_deceased(self):
        for (k,v) in {
                'Current':False,
                'Cancelled':False,
                'Deceased':True,
                'Expired':False,
                'Grace':False,
                'New':False,
                }.items():
            actual = MB.is_deceased(status=k)
            expected = v
            self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()
