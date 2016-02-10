#!/usr/bin/python3
'''
Created on 1 Nov 2014

@author: julian
'''
from collections import OrderedDict as OD
from csv import DictReader, DictWriter
from datetime import datetime as dt
from datetime import timedelta
import datetime
from importlib import import_module
from io import StringIO
import mmap
import os
from os.path import basename, splitext
from re import compile, IGNORECASE, sub
from re import search
from sys import argv
from sys import stdout
import xlrd

import configurations2 as cf2


class FileHandler(object):

    '''Handle reading and writing files, including the config file which is loaded as a Python module.
    '''

    def config_load(self, modulename):
        mods = import_module(modulename)
        return mods.config

    def csv_read(self, pathname, fieldnames_expected, skip_lines=0):
        '''Read csv file (excluding 1st row) into self.table.
        Populate self.fieldnames with fields from 1st row in order'''
        with open(pathname, 'r', encoding='utf-8', errors='ignore') as fh:
            return self.csv_read_fh(fh, fieldnames_expected, skip_lines)

    def csv_read_fh(self, fh, fieldnames_expected, skip_lines=0):
        '''Read csv file (excluding 1st row) into self.table.
        Populate self.fieldnames with fields from 1st row in order'''
        for unused in range(skip_lines):
            next(fh)
        dr = DictReader(fh)
        table = [row for row in dr]
        fieldnames = tuple(dr.fieldnames)
        if len(fieldnames) == len(fieldnames_expected):
            if fieldnames != fieldnames_expected:
                fields_odd = self.find_mismatch(
                    fieldnames, fieldnames_expected)
                raise ValueError('Unexpected fieldnames:\nactual  : '
                                 + ','.join(sorted(fieldnames))
                                 + '\nexpected: ' +
                                 ','.join(sorted(fieldnames_expected))
                                 + '\nmismatch:' + ','.join(sorted(fields_odd)))
        return (table, fieldnames)

    def find_mismatch(self, set0, set1):
        '''return difference of 2 iterables (lists, sets, tuples)
        as sorted list'''
        return sorted(list(set(set0).difference(set(set1))))

    def csv_print(self, table, fieldnames2):
        self.csv_write_fh(table, stdout, fieldnames2)

    def csv_write(self, table, pathname, fieldnames2):
        with open(pathname, 'w') as fh:
            self. csv_write_fh(table, fh, fieldnames2)

    def csv_write_fh(self, table, fh, fieldnames2):
        dw = DictWriter(fh, fieldnames2)
        dw.writeheader()
        dw.writerows(table)

    def xlsx_read(self, pathname, fieldnames_expected, skip_lines=0, sheet_index=1):
        with open(pathname, 'r') as fh:

            data = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
            book = xlrd.open_workbook(file_contents=data)
            sheet = book.sheet_by_index(sheet_index)

            def cell_value(i, j):
                '''Convert xls date from days since ~1900 to '31/12/2014' '''
                cell = sheet.cell(i, j)
                value = cell.value
                if cell.ctype == 3 and value:  # XL_CELL_DATE
                    return datetime.datetime(*xlrd.xldate_as_tuple(value, book.datemode)).strftime('%d/%m/%Y')
                else:
                    return str(value).replace(',', '')

            csv = (','.join([cell_value(i, j) for j in range(sheet.ncols)])
                   for i in range(sheet.nrows))
            return self.csv_read_fh(csv, fieldnames_expected, skip_lines)


class CsvFixer(object):

    '''The top level class.
    Read csv data file into a table
    Fix the data in table
    Create new table: with NB table column headings
    Write the table to a new csv file for import to NB.
    '''
    def __init__(self, csv_register, config, filereader):
        fieldnames = config.keys()

        # Read csv data file into a table
        (table, unused) = filereader(csv_register, fieldnames)

        # Fix the data in table
        (csv_basename, _) = splitext(basename(csv_register))
        vh = TableFixer(table0=table, config=config)
        table_fixed = vh.fix_table()

        # Write the table to a new csv file for import to NB.
        self.csv_filename_new = csv_register.replace('.csv', 'NB.csv')
        filehandler.csv_write(table_fixed, self.csv_filename_new, fieldnames)


class TableFixer(object):

    def __init__(self, config=None, table0=None):
        self.config = config
        self.table0 = table0

    def fix_table(self):
        '''Returns new table given old table
        '''
        try:
            return [self.fix_row(row0) for row0 in self.table0]
        except (IndexError, TypeError) as e:
            e.args += ('config:', self.config,)
            raise

    def fix_row(self, row0):
        '''Creates new row from old row
        '''
        try:
            return {fieldname1: self.fix_field(row0, arg0)
                for (fieldname1, arg0) in self.config.items()}
        except (AttributeError, IndexError, TypeError) as e:
            e.args += ('row0:', row0,)
            raise

    @classmethod
    def fix_field(self, row0, arg0):
        '''Creates new field from old field(s)
        '''
        try:
            if arg0 == None:
                return None
            elif isinstance(arg0, str):
                return row0.get(arg0).strip()
            elif isinstance(arg0, tuple):
                 func = arg0[0]
                 args = arg0[1]
                 kwargs0 = arg0[2]
                 if callable(func):
                     kwargs = {k:row0.get(v) for (k, v) in kwargs0.items()}
                     return func(row0, *args, **kwargs)
            raise TypeError('TableFixer.fix_field: expected str or (func, kwargs). Got:{}'.format(arg0))
        except (AttributeError, IndexError, TypeError) as e:
            e.args += ('arg0:', arg0,)
            raise

    @classmethod
    def background_merge(cls, row0, key_notes='', key_comments=''):
        return ' '.join([row0.get(key_notes), row0.get(key_comments)])

    @classmethod
    def doa2dob(cls, row0, key_doa=None):
        '''Convert date of attainment (ie reach 18years old) to DoB in US format: mm/dd/yyyy.
            Use after converting to NB date format.
            yoa: year of attainment, yob: year of birth'''
        doa = row0.get(key_doa)
        if doa:
            (day, month, yoa) = doa.split('/')
            yob = str(int(yoa) - 18)
            return '/'.join([month, day, yob])
        else:
            return doa

    @classmethod
    def fix_address1(cls, row0, key_housename='', key_street_number='', key_street_name=''):
        return ' '.join([row0.get(key_housename), row0.get(key_street_number),
                         row0.get(key_street_name)]).strip()

    @classmethod
    def fix_address2(cls, row0, key_block_name=''):
        return row0.get(key_block_name)

    @classmethod
    def fix_party(cls, row0, party_map, key_party=None):
        return party_map.get(row0.get(key_party))

    @classmethod
    def fix_support_level(cls, row0, support_level_map, key_support_level=None):
        return support_level_map.get(row0.get(key_support_level))

    @classmethod
    def merge_pd_eno(cls, row0, pd=None, eno=None):
        '''Merged PD & zero padded eno,
        takes: pd key_old and eno key_old.eg:
        {'pd':'polldist', 'eno':'elect no',} -> {'statefile_id':EA0012',}
        '''
        eno_padded = None
        try:
            pd = pd.lstrip('!')
            eno_padded = cls.pad_eno(eno)
            return pd + eno_padded
        except (AttributeError, TypeError) as e:
            e += ('pd:{} eno:{} eno_padded:{}'.format(pd, eno, eno_padded))
            raise

    @classmethod
    def pad_eno(cls, eno):
        return '%04d' % (int(eno),)

    @classmethod
    def tags_add(cls, row0, tag_map, fieldnames=[]):
        '''For each field in fieldnames. Eg: 'Demographic','national', 'Local','Post', 'Vote14', 'Vote12'
        return tag_list as string, eg: 'ResidentsParking,StreetsAhead,Vote14'
        '''
        return ','.join(sorted([k for k in [cls.tags_split(row0.get(fieldname), tag_map) for fieldname in fieldnames] if k]))

    @classmethod
    def tags_split(cls, fieldvalue, tag_map):
        '''Split fieldvalue into tags. Eg: value='ResPark, StrtAhed'
        return tag_list as string, eg: 'ResidentsParking,StreetsAhead'
        '''
        if fieldvalue == None:
            return ''
        tag_list0 = fieldvalue.split(',')
        tag_list0 = [k.strip() for k in tag_list0 if k.strip()]
        tag_list = [tag_map.get(k) or k for k in tag_list0 if k]
        return ','.join(tag_list)


if __name__ == '__main__':
    config = None
    argv.append('/home/julian/SRGP/canvassing/2014_15/broomhill/csv/BroomhillCanvassData2015-03EA-H.csv')
    for csv_filename in argv[1:]:  # skip scriptname in argv[0]
        # Find config varname to match csv filename
        if search('registerUpdate', csv_filename, IGNORECASE):
            config = config_register_update
        if search('WardUpdated', csv_filename, IGNORECASE):
            config = config_register_update
        elif search('Marked', csv_filename, IGNORECASE):
            config = config_marked
        elif search('RegisterPV', csv_filename, IGNORECASE):
            config = config_register_postal
        elif search('CentralConsituencyPostal', csv_filename, IGNORECASE):
            config = config_register_postal
        elif search('CentralWardPostal', csv_filename, IGNORECASE):
            config = config_register_postal
        elif search('Crookes_Ecclesall_Postal', csv_filename, IGNORECASE):
            config = config_register_postal
        elif search('register', csv_filename, IGNORECASE):
            config = config_register
        elif search('SearchAdd', csv_filename, IGNORECASE):
            config = config_search_add
        elif search('SearchMod', csv_filename, IGNORECASE):
            config = config_search_mod
        elif search('textable', csv_filename, IGNORECASE):
            config = config_textable
        elif search('support1_2', csv_filename, IGNORECASE):
            config = config_support1_2
#         elif search('MembersNew', csv_filename,):
#             config = config_members_new
        elif search('Members', csv_filename, IGNORECASE):
            config = config_members
        elif search('Officers', csv_filename, IGNORECASE):
            config = config_officers
        elif search('Supporters', csv_filename, IGNORECASE):
            config = config_supporters
        elif search('Volunteers', csv_filename, IGNORECASE):
            config = config_volunteers
        elif search('YoungGreens', csv_filename, IGNORECASE):
            config = config_young_greens
        elif search('Search', csv_filename, IGNORECASE):
            config = config_search
        elif search('BroomhillCanvassData', csv_filename):
            config = cf2.config_robin_latimer
        elif search('canvass', csv_filename, IGNORECASE):
            config = canvassing
        elif search('nationbuilder.+NB', csv_filename):
            config = config_nationbuilderNB
        elif search('nationbuilder', csv_filename):
            config = config_nationbuilder
        else:
            raise Exception(
                'Cannot find config for csv {}'.format(csv_filename))

        filehandler = FileHandler()
        reader = None
        if csv_filename.endswith('.csv'):
            reader = filehandler.csv_read
        elif csv_filename.endswith('.xls'):
            reader = filehandler.xlsx_read
        elif csv_filename.endswith('.xlsx'):
            reader = filehandler.xlsx_read
        xls_pw = os.getenv('XLS_PASSWORD')

        print('config_name: ', config['config_name'])
        del config['config_name']
        csvfixer = CsvFixer(csv_filename, config, reader)
        print(csvfixer.csv_filename_new)
