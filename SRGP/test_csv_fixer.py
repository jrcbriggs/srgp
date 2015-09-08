#!/usr/bin/python3
'''
Created on 18 Nov 2014
@author: julian
'''
from collections import OrderedDict as OD
import os
import sys
import unittest
from csv_fixer import TableFixer, FileHandler, TableMapper, ConfigHandler


class Test(unittest.TestCase):

    def setUp(self):
        self.config = {
            'address_fields': OD([
                ('a1', 'A1'), ('a2', 'A2'),
                ('a3', 'A3'), ('a4', 'A4'),
                ('city', 'A5'), ('zip', 'A6'),
                ('country_code', 'A7'), ]),
            'date_fields': ('c',),  # Date fields
            'doa_fields': ('c',),  # Date of Attainment field
            'date_format': '%d/%m/%Y',  # _electoral_roll
            'fieldmap': OD([
                ('a', 'A'),
                ('b', 'B'),
                ('c', 'C'),  # Date of Attainment
                ('d', 'tag_list'),
                ('e', 'tag_list'),
                ('f', None),
            ]),
            'fields_extra': OD([]),
            'fields_flip': (),
            'tagfields': ('e', 'f'),
        }
        self.params = self.config.copy()
        self.params.update({'fieldnames': ('a', 'b', 'c', 'd', 'e', 'f',), })
        self.config_r2nb = self.config.copy()
        self.config_r2nb.update({
            'fieldnames': ('a', 'b', 'c', 'd', 'e', 'f',),
            'fieldnames_new': ('A', 'B', 'C', 'tag_list',),
            'fieldmap_new': OD([
                ('a', 'A'),
                ('b', 'B'),
                ('c', 'C'),
                ('tag_list', 'tag_list'),
            ]),
        })
        self.address_fields = self.config['address_fields']
        self.doa_fields = ('c',)
        self.fieldnames = ('a', 'b', 'c', 'd', 'e', 'f',)
        self.fieldnames_new = ('A', 'B', 'C', 'tag_list',)
        self.fieldmap = OD([('a', 'A',), ('b', 'B',), ('c', 'C',), ])
        self.tagfields = ('d', 'e',)
        # filehandler
        self.filehandler = FileHandler()
        # TableMapper
        self.row0 = {'a': '0', 'b': '1', 'c': '2', 'd': '3', 'e': '4', 'f': '5', }
        self.row1 = {'a': '6', 'b': '7', 'c': '8', 'd': '9', 'e': '10', 'f': '11', }
        self.data = [self.row0, self.row1]
        self.tm = TableMapper(self.data, self.fieldmap)
        # OD
        self.od = OD([('a', 0), ('b', 1), ('c', 2), ])
        self.od1 = OD([('z', 9), ('y', 8), ('x', 7), ])
        # TableFixer
        self.doa = '31/12/2014'
        self.dob_nb = '12/31/1996'  # Date of Birth = Date of Attainment less 18 years
        self.date_fields = ['Election_Date']
        self.pathname = '/tmp/config_electoralregister_test.py'
        self.table = [self.row0, self.row1]
        self.table_fixed = [
            {'col0': 'a', 'col1': 'b', },
        ]
        self.csv_basename = 'SRGP_MembersAll_2015-02-13'
        self.tf = TableFixer(table=self.table, csv_basename=self.csv_basename, **self.config)
    # ConfigHandler

    def test_confighandler(self):
        ch = ConfigHandler(**self.config)
        self.assertTupleEqual(ch.fieldnames, ('a', 'b', 'c', 'd', 'e', 'f',))
        self.assertTupleEqual(ch.fieldnames_new, ('A', 'B', 'C', 'tag_list'))
        self.assertDictEqual(
            ch.fieldmap_new, {'a': 'A', 'b': 'B', 'c': 'C', 'tag_list': 'tag_list'})
        self.assertListEqual(list(ch.fieldmap_new.keys()), ['a', 'b', 'c', 'tag_list'])
        self.assertTupleEqual(ch.tagfields, ('d', 'e',))
    # FileHandler

    def test_config_load(self):
        with open(self.pathname, 'w') as fh:
            fh.write('config={"var0": 123}\n')
            modulename = os.path.basename(self.pathname).replace('.py', '')
            sys.path.append('/tmp')
        config = self.filehandler.config_load(modulename)
        self.assertEquals(config['var0'], 123)

    def test_csv_print(self):
        self.filehandler.csv_print(self.table, self.fieldnames)

    def test_csv_read(self):
        self.filehandler.csv_write(self.table, self.pathname, self.fieldnames)
        (table, fieldnames) = self.filehandler.csv_read(self.pathname, self.fieldnames)
        self.assertEqual(len(table), len(self.table))
        for i in range(len(table)):
            self.assertDictEqual(table[i], self.table[i])
        self.assertTupleEqual(fieldnames, self.fieldnames)

    def test_csv_read_skiplines(self):
        with open(self.pathname, 'w') as fh:
            fh.write('Line0\nLine1\nLine2\na,b,c,d,e,f\n0,1,2,3,4,5\n6,7,8,9,10,11\n')
        (table, fieldnames) = self.filehandler.csv_read(
            self.pathname, self.fieldnames, skip_lines=3)
        self.assertEqual(len(table), len(self.table))
        for i in range(len(table)):
            self.assertDictEqual(table[i], self.table[i])
        self.assertTupleEqual(fieldnames, self.fieldnames)

    def test_csv_read_err(self):
        self.filehandler.csv_write(self.table, self.pathname, self.fieldnames)
        fieldnames_new = self.fieldnames[: -1] + ('Junk',)
        self.assertRaises(ValueError, self.filehandler.csv_read, self.pathname,
                          fieldnames_new)
    # TableMapper

    def test_maprow(self):
        expected = {'A': '0', 'B': '1', 'C': '2', }
        actual = self.tm.maprow(self.row0, self.fieldmap)
        self.assertDictEqual(actual, expected)

    def test_mapdata(self):
        expected = [{'A': '0', 'B': '1', 'C': '2', }, {'A': '6', 'B': '7', 'C': '8', }]
        actual = self.tm.mapdata(self.data, self.fieldmap)
        self.assertListEqual(actual, expected)

    def test_TableMapper(self):
        expected = [{'A': '0', 'B': '1', 'C': '2', }, {'A': '6', 'B': '7', 'C': '8', }, ]
        actual = self.tm.data_new
        self.assertListEqual(actual, expected)
    # OD

    def test_ordereddict(self):
        expected = ['a', 'b', 'c']
        actual = list(self.od.keys())
        self.assertListEqual(actual, expected)
        expected = [0, 1, 2]
        actual = list(self.od.values())
        self.assertListEqual(actual, expected)

    def test_ordereddict1(self):
        expected = ['z', 'y', 'x']
        actual = list(self.od1.keys())
        self.assertListEqual(actual, expected)
        expected = [9, 8, 7]
        actual = list(self.od1.values())
        self.assertListEqual(actual, expected)
    # TableFixer

    def test_append_fields_other(self):
        for isness in ('is_supporter', 'is_volunteer'):
            fields_extra = OD([(isness, isness), ])
            row0 = self.row0.copy()
            row0.update({'Status': 'New', isness: False})
            self.tf.extra_fields(row0, fields_extra)
            self.assertTrue(row0[isness], '{} {}'.format(isness, row0[isness]))

    def test_clean_value(self):
        fixtures = {
            'asdf': 'asdf',
            ' asdf': 'asdf',
            'asdf ': 'asdf',
            '  asdf  ': 'asdf',
            'asdf jkl': 'asdf jkl',
            'asdf,jkl': 'asdf jkl',
        }
        for fixture, expected in fixtures.items():
            actual = self.tf.clean_value(fixture)
            self.assertEqual(actual, expected, '' + actual + '!=' + expected)

    def test_clean_row(self):
        row = {'a': '0', 'b': ' 1', 'c': '2 ', 'd ': ' 3 ', 'e': '4 4', 'f': '5'}
        expected = {'a': '0', 'b': '1', 'c': '2', 'd ': '3', 'e': '4 4', 'f': '5'}
        self.tf.clean_row(row)
        self.assertDictEqual(row, expected)

    def test_doa2dob(self):
        doa = '31/12/2014'
        expected = '31/12/1996'
        actual = self.tf.doa2dob(doa)
        self.assertEqual(actual, expected)

    def test_fix_addresses(self):
        row = {'junk': 1, 'A1': '220 SVR', 'A2': 'Sheffield',
               'A3': 'S10 1ST', 'A4': '', 'A5': '', 'A6': '', 'A7': '', }
        exp = {'junk': 1, 'A1': '220 SVR', 'A2': '', 'A3': '',
               'A4': '', 'A5': 'Sheffield', 'A6': 'S10 1ST', 'A7': 'GB', }
        self.tf.fix_addresses_city_postcode_countrycode(row, self.address_fields)
        self.assertDictEqual(row, exp)

    def test_fix_addresses1(self):
        row = {'junk': 1, 'A1': 'Attic', 'A2': '220 SVR', 'A3': 'Sheffield',
               'A4': 'S10 1ST', 'A5': '', 'A6': '', 'A7': '', }
        exp = {'junk': 1, 'A1': 'Attic', 'A2': '220 SVR', 'A3': '',
               'A4': '', 'A5': 'Sheffield', 'A6': 'S10 1ST', 'A7': 'GB', }
        self.tf.fix_addresses_city_postcode_countrycode(row, self.address_fields)
        self.assertDictEqual(row, exp)

    def test_fix_addresses2(self):
        row = {'junk': 1, 'A1': 'Flat 1', 'A2': 'Crookes Hall', 'A3': '220 SVR',
               'A4': 'Sheffield', 'A5': 'S10 1ST', 'A6': '', 'A7': '', }
        exp = {'junk': 1, 'A1': 'Flat 1', 'A2': 'Crookes Hall', 'A3': '220 SVR',
               'A4': '', 'A5': 'Sheffield', 'A6': 'S10 1ST', 'A7': 'GB', }
        self.tf.fix_addresses_city_postcode_countrycode(row, self.address_fields)
        self.assertDictEqual(row, exp)

    def test_fix_address_street_1(self):
        '''Apartment 22, Victoria House, Victoria Street, City Centre, Sheffield, S3 7QL
        '''
        row = {'junk': 1, 'A1': '220 SV Road', 'A2': 'Crookes', 'A3': '',
               'A4': '', 'A5': 'Sheffield', 'A6': 'S10 1ST', 'A7': 'GB', }
        exp = {'junk': 1, 'A1': '220 SV Road','A2': 'Crookes', 'A3': '',
               'A4': '', 'A5': 'Sheffield', 'A6': 'S10 1ST', 'A7': 'GB', }
        self.tf.fix_address_street(row, self.address_fields)
        print('row',row)
        self.assertDictEqual(row, exp)

    def test_fix_address_street_2(self):
        '''Apartment 22, Victoria House, Victoria Street, City Centre, Sheffield, S3 7QL
        '''
        row = {'junk': 1, 'A1': 'Flat 1', 'A2': '220 SV Road', 'A3': 'Crookes',
               'A4': '', 'A5': 'Sheffield', 'A6': 'S10 1ST', 'A7': 'GB', }
        exp = {'junk': 1, 'A1': '220 SV Road','A2': 'Flat 1', 'A3': 'Crookes',
               'A4': '', 'A5': 'Sheffield', 'A6': 'S10 1ST', 'A7': 'GB', }
        self.tf.fix_address_street(row, self.address_fields)
        print('row',row)
        self.assertDictEqual(row, exp)
        
    def test_fix_address_street_3(self):
        '''Apartment 22, Victoria House, Victoria Street, City Centre, Sheffield, S3 7QL
        '''
        row = {'junk': 1, 'A1': 'Flat 1', 'A2': 'Crookes Hall', 'A3': '220 SV Road',
               'A4': 'Crookes', 'A5': 'Sheffield', 'A6': 'S10 1ST', 'A7': 'GB', }
        exp = {'junk': 1, 'A1': '220 SV Road','A2': 'Flat 1', 'A3': 'Crookes Hall',
               'A4': 'Crookes', 'A5': 'Sheffield', 'A6': 'S10 1ST', 'A7': 'GB', }
        self.tf.fix_address_street(row, self.address_fields)
        print('row',row)
        self.assertDictEqual(row, exp)

    def test_fix_addresses_other_electors(self):
        row = {'junk': 1, 'A1': 'Other Electors', 'A2': '',
               'A3': '', 'A4': '', 'A5': '', 'A6': '', 'A7': '', }
        exp = {'junk': 1, 'A1': 'Other Electors', 'A2': '',
               'A3': '', 'A4': '', 'A5': '', 'A6': '', 'A7': 'GB', }
        self.tf.fix_addresses_city_postcode_countrycode(row, self.address_fields)
        self.assertDictEqual(row, exp)

    def test_fix_append_fields(self):
        fields_new = {'fn0': 0, 'fn1': 1}
        expected = self.row0.copy()
        expected.update({'fn0': 0, 'fn1': 1})
        self.tf.extra_fields(self.row0, fields_new)
        self.assertDictEqual(self.row0, expected)

    def test_fix_append_fields_named(self):
        for fieldname in ('is_voter', 'is_deceased', 'party_member'):
            expected = self.row0.copy()
            expected.update({fieldname: False})
            self.tf.extra_fields(self.row0, {fieldname: fieldname})
            self.assertEqual(self.row0, expected)

    def test_fix_append_fields_party(self):
        expected = self.row0.copy()
        expected.update({'party': 'G'})
        self.tf.extra_fields(self.row0, {'party': 'party'})
        self.assertDictEqual(self.row0, expected)

    def test_fix_append_fields_support_level_member(self):
        self.row0.update({'Status': 'New'})
        expected = self.row0.copy()
        expected.update({'support_level': 1})
        self.tf.extra_fields(self.row0, {'support_level': 'support_level'})
        self.assertDictEqual(self.row0, expected)

    def test_fix_append_fields_support_level_not_member(self):
        self.row0.update({'Status': 'Deceased'})
        expected = self.row0.copy()
        expected.update({'support_level': 1})
        self.tf.extra_fields(self.row0, {'support_level': 'support_level'})
        self.assertDictEqual(self.row0, expected)

    def test_fix_city(self):
        row = {'junk': 1, 'A1': '220 SVR', 'A2': 'Sheffield',
               'A3': 'S10 1ST', 'A4': '', 'A5': '', 'A6': '', 'A7': '', }
        exp = {'junk': 1, 'A1': '220 SVR', 'A2': '', 'A3': 'S10 1ST',
               'A4': '', 'A5': 'Sheffield', 'A6': '', 'A7': '', }
        self.tf.fix_city(row, self.address_fields, 'A5')
        self.assertDictEqual(row, exp)

    def test_fix_contact_name(self):
        row = {'Contact Name': 'Briggs Julian'}
        expected = {'Contact Name': 'Julian Briggs'}
        self.tf.fix_contact_name(row)
        self.assertDictEqual(row, expected)

    def test_fix_date(self):
        expected = '12/31/2014'
        actual = self.tf.fix_date(self.doa)
        self.assertEqual(actual, expected)
        #
        actual = self.tf.fix_date('   ')
        self.assertEqual(actual, '')

    def test_fix_dates(self):
        row = {'a': '0', 'b': '1', 'c': self.doa}  # Date of Attainment
        expected = {'a': '0', 'b': '1', 'c': '12/31/2014'}
        self.tf.fix_dates(row)
        self.assertDictEqual(row, expected)

    def test_fix_deceased(self):
        self.row0.update({'Status': 'Deceased'})
        self.tf.fix_deceased(self.row0)
        expected = self.row0.copy()
        expected.update({'is_deceased': True})
        self.assertDictEqual(self.row0, expected)

    def test_fix_deceased_no(self):
        self.row0.update({'Status': 'Current'})
        self.tf.fix_deceased(self.row0)
        expected = self.row0.copy()
        expected.update({'is_deceased': False})
        self.assertDictEqual(self.row0, expected)

    def test_fix_doa(self):
        row = {'a': '0', 'b': '1', 'c': self.doa}
        expected = {'a': '0', 'b': '1', 'c': '31/12/1996'}
        self.tf.fix_doa(row, self.doa_fields)
        self.assertDictEqual(row, expected)

    def test_fix_local_party(self):
        self.row0.update({'Local party': None})
        self.tf.fix_local_party(self.row0)
        expected = self.row0.copy()
        expected.update({'Local party': 'G'})
        self.assertDictEqual(self.row0, expected)

    def test_fix_local_party_no(self):
        self.row0.update({'Local partyXXX': 123})
        self.tf.fix_local_party(self.row0)
        expected = self.row0.copy()
        expected.update({'Local partyXXX': 123})
        self.assertDictEqual(self.row0, expected)

    def test_fix_postcode(self):
        row = {'junk': 1, 'A1': '220 SVR', 'A2': 'Sheffield',
               'A3': 'S10 1ST', 'A4': '', 'A5': '', 'A6': '', 'A7': '', }
        exp = {'junk': 1, 'A1': '220 SVR', 'A2': 'Sheffield',
               'A3': '', 'A4': '', 'A5': '', 'A6': 'S10 1ST', 'A7': '', }
        self.tf.fix_postcode(row, self.address_fields, 'A6')
        self.assertDictEqual(row, exp)

    def test_fix_table(self):
        '''put a valid doa in the Date of Attainment field'''
        self.row0.update({'c': self.doa, 'A1': '220 SVR', 'A2': 'Sheffield',
                          'A3': 'S10 1ST', 'A4': '', 'A5': '', 'A6': '', 'A7': '', })
        self.row1.update({'c': self.doa, 'A1': '220 SVR', 'A2': 'Sheffield',
                          'A3': 'S10 1ST', 'A4': '', 'A5': '', 'A6': '', 'A7': '', })
        addresses_dict = dict(zip(self.address_fields, self.address_fields))
        # put a valid doa in the Date of Attainment field
        self.params['fieldmap'].update(addresses_dict)
        tf = TableFixer(table=self.table, csv_basename=self.csv_basename, **self.params)
        table_fixed = tf.fix_table()
        row0 = self.row0.copy()
        row0.update({'c': self.dob_nb, 'A1': '220 SVR', 'A2': '', 'A3': '',
                     'A4': '', 'A5': 'Sheffield', 'A6': 'S10 1ST', 'A7': 'GB', })
        row1 = self.row1.copy()
        row1.update({'c': self.dob_nb, 'A1': '220 SVR', 'A2': '', 'A3': '',
                     'A4': '', 'A5': 'Sheffield', 'A6': 'S10 1ST', 'A7': 'GB', })
        table_expected = [row0, row1]
        self.assertListEqual(table_fixed, table_expected)
        self.assertDictEqual(table_fixed[0], self.row0)
        self.assertDictEqual(table_fixed[1], self.row1)

    def test_flip_fields(self):
        row = {'k0': 'v0', 'Do not mail': 1, 'Do not Phone': 1}
        fieldnames = ('Do not mail', 'Do not Phone')
        self.tf.flip_fields(row, fieldnames)
        expected = {'k0': 'v0', 'Do not mail': 0, 'Do not Phone': 0}
        self.assertDictEqual(row, expected)
        #
        row = {'k0': 'v0', 'Do not mail': 0, 'Do not Phone': 0}
        fieldnames = ('Do not mail', 'Do not Phone')
        self.tf.flip_fields(row, fieldnames)
        expected = {'k0': 'v0', 'Do not mail': 1, 'Do not Phone': 1}
        self.assertDictEqual(row, expected)
        #
        row = {'k0': 'v0', 'Do not mail': 1, 'Do not Phone': 0}
        fieldnames = ('Do not mail', 'Do not Phone')
        self.tf.flip_fields(row, fieldnames)
        expected = {'k0': 'v0', 'Do not mail': 0, 'Do not Phone': 1}
        self.assertDictEqual(row, expected)

    def test_get_status(self):
        for k, v in {'Cancelled': 'canceled', 'Current': 'active', 'Deceased': 'expired', 'Expired': 'expired', 'New': 'active'}.items():
            self.row0.update({'Status': k})
            self.tf.fix_status(self.row0)
            actual = self.row0['Status']
            expected = v
            self.assertEqual(actual, expected, 'k {} v {}'.format(k, v))

    def test_iscity(self):
        self.assertTrue(self.tf.iscity('Sheffield'), 'expected match:' + 'Sheffield')
        self.assertTrue(self.tf.iscity('sheffield'), 'expected match:' + 'Sheffield')
        self.assertFalse(self.tf.iscity('XSheffield'), 'unexpected match:' + 'ShefXield')
        self.assertFalse(self.tf.iscity('ShefXield'), 'unexpected match:' + 'ShefXield')
        self.assertFalse(self.tf.iscity('SheffieldX'), 'unexpected match:' + 'SheffieldX')

    def test_iscounty(self):
        self.assertTrue(self.tf.iscounty('South Yorks'), 'expected match:' + 'South Yorks')

    def test_isdeceased_true(self):
        self.row0.update({'Status': 'Deceased'})
        actual = self.tf.isdeceased(self.row0)
        self.assertTrue(actual)

    def test_isdeceased_false(self):
        for status in ('Cancelled', 'Current', 'Expired', 'New'):
            self.row0.update({'Status': status})
            actual = self.tf.isdeceased(self.row0)
            self.assertFalse(actual)

    def test_isdeceased_no_field(self):
        actual = self.tf.isdeceased(self.row0)
        self.assertFalse(actual)
        self.assertFalse(self.tf.iscounty('XSouth Yorks'), 'unexpected match:' + 'XSouth Yorks')

    def test_ishouse(self):
        for house in ('Barn', 'Building', 'College',):
            self.assertTrue(self.tf.ishouse('123' + house), 'expected match:' + house)
        for house in('Sheffield', 'South Yorks', 'Approach', 'S10 1ST',):
            self.assertFalse(self.tf.ishouse(house), 'unexpected match:' + house)

    def test_ismember_true(self):
        '''is_member is called after fix_status so call fix_status in test
        before testing is_member
        '''
        for status in ('Current', 'New'):
            self.row0.update({'Status': status})
            self.tf.fix_status(self.row0)
            actual = self.tf.is_party_member(self.row0)
            self.assertTrue(actual, 'status {}'.format(status))

    def test_ismember_false(self):
        for status in ('Cancelled', 'Deceased', 'Expired'):
            self.row0.update({'Status': status})
            actual = self.tf.is_party_member(self.row0)
            self.assertFalse(actual)

    def test_ismember_no_field(self):
        actual = self.tf.is_party_member(self.row0)
        self.assertFalse(actual)

    def test_ispostcode(self):
        for postcode in('S10 1ST', 'S1 1ST', 'S1 2ST',):
            self.assertTrue(self.tf.ispostcode(postcode), 'expected match:' + postcode)
        for postcode in('SX10 1ST', 'S1 12ST', 'S1 1STX', 'S1 X1ST',):
            self.assertFalse(self.tf.ispostcode(postcode), 'unexpected match:' + postcode)

    def test_isstreet(self):
        for street in 'Approach Drive Place'.split():
            self.assertTrue(self.tf.isstreet('123' + street), 'expected match:' + street)
#         self.assertTrue(self.tf.isstreet('Kelham Island'), 'expected match:' + street)
        self.assertTrue(self.tf.isstreet('220 Stannington View Road'), 'expected match:' + street)
        for street in 'Sheffield S10 Yorks'.split():
            self.assertFalse(self.tf.isstreet(street), 'unexpected match:' + street)

    def test_isvoter_register_true(self):
        for status in ('E'):
            self.row0.update({'Status': status})
            actual = self.tf.isvoter(self.row0)
            self.assertTrue(actual)

    def test_isvoter_register_false(self):
        for status in (''):
            self.row0.update({'Status': status})
            actual = self.tf.isvoter(self.row0)
            self.assertFalse(actual)

    def test_isvoter_register_no_field(self):
        actual = self.tf.isvoter(self.row0)
        self.assertFalse(actual)

    def test_isvoter_canvassing_true(self):
        self.row0.update({'Electoral roll number': 'GA123'})
        actual = self.tf.isvoter(self.row0)
        self.assertTrue(actual)

    def test_isvoter_canvassing_false(self):
        actual = self.tf.isvoter(self.row0)
        self.assertFalse(actual)

    def test_is_matching_row(self):
        skip_dict = {'a': '0'}
        actual = self.tf.is_matching_row(self.row0, skip_dict)
        self.assertListEqual(actual, [self.row0])

    def test_is_matching_row_no_match(self):
        skip_dict = {'a': 'XXX'}
        actual = self.tf.is_matching_row(self.row0, skip_dict)
        self.assertListEqual(actual, [])

    def test_merge_pd_eno_register(self):
        row = {'PD': 'GA', 'ENO': 123}
        expected = 'GA123'
        self.tf.merge_pd_eno(row)
        actual = row['ENO']
        self.assertEqual(expected, actual)

    def test_merge_pd_eno_canvassing(self):
        row = {'Polling district': 'GA', 'Electoral roll number': 123}
        expected = 'GA123'
        self.tf.merge_pd_eno(row)
        actual = row['Electoral roll number']
        self.assertEqual(expected, actual)

    def test_pd2ward(self):
        d = {
            'EA': 'Broomhill',
            'GB': 'Central',
            'RC': 'Manor Castle',
            'TD': 'Nether Edge',
            'ZE': 'Walkley',
        }
        for (k, v) in d.items():
            self.assertEqual(TableFixer.pd2ward(k), v)

    def test_set_ward(self):
        d = {
            'EA': 'Broomhill',
            'GB': 'Central',
            'RC': 'Manor Castle',
            'TD': 'Nether Edge',
            'ZE': 'Walkley',
        }
        for (k, v) in d.items():
            row = {}
            row['PD'] = k
            self.tf.set_ward(row)
            self.assertEqual(row['ward_name'], v)

    def test_tags_create(self):
        row = self.row0
        csv_basename = 'SRGP_MembersAll_2015-01-13'
        expected = {'tag_list': 'd=3,e=4,SRGP_MembersAll_2015-01-13'}
        actual = self.tf.tags_create(row, self.tagfields, csv_basename)
        self.assertEqual(expected, actual)
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
