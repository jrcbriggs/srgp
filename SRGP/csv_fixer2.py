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

import configurations2


# from configurations2 import config_robin_latimer
class ConfigHandler(object):

    '''Parse the config dict to extract input params to table fixer and csv fixer:
    fieldmap: ordered dict maps old to new fieldnames
    fieldnames: for reading original csv
    fieldnames_new: fieldnames for writing new csv
    tagfields: fieldnames from original csv to add to tag_list
    '''

    def __init__(self,
                 address_fields,
                 date_fields,
                 date_format,
                 doa_fields,
                 fieldmap,
                 fields_extra,
                 fields_flip,
                 **kwargs
                 ):
        self.fieldnames = tuple(fieldmap.keys())  # for reading csv
        self.fields_extra = fields_extra

        # Derive things from fieldmap
        self.tagfields = ()
        # for writing csv (append new fields later)
        self.fieldmap_new = OD()
#         self.fieldmap_new.update(fields_extra)
        for k, v in fieldmap.items():
            if v == 'tag_list':
                self.tagfields += (k,)  # Put original fieldname on taglist
            elif(v is None):
                pass
            else:
                self.fieldmap_new[k] = v

        # Update properties
        self.fieldmap_new.update(fields_extra)
        self.fieldmap_new.update({'tag_list': 'tag_list', })
        self.fieldnames_new = tuple(self.fieldmap_new.values())

        # Populate params
        self.params = {
            'address_fields': address_fields,
            'date_fields': date_fields,
            'date_format': date_format,
            'doa_fields': doa_fields,
            'fieldnames': self.fieldnames,
            'fields_extra': self.fields_extra,
            'fields_flip': fields_flip,
            'tagfields': self.tagfields,
        }


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
    defaults = {
              'address_fields':{},
              'date_fields':(),
              'date_format':'',
              'doa_fields':(),
              'fields_extra':{},
              'fields_flip':(),
              }
    def __init__(self, csv_register, config, filereader):
        for (k, v) in self.defaults.items():
            config.setdefault(k, v)

        ch = ConfigHandler(**config)

        # Read csv data file into a table
        skip_lines = config.get('skip_lines', 0)
        (table, unused) = filereader(
            csv_register, ch.fieldnames, skip_lines)

        # Fix the data in table
        (csv_basename, _) = splitext(basename(csv_register))
        vh = TableFixer(table=table, csv_basename=csv_basename, **ch.params)
        table_fixed = None
        if 'nationbuilder' in csv_basename:
            table_fixed = vh.fix_table_street_address()
        else:
            table_fixed = vh.fix_table()

        # Create new table: with NB table column headings
        d2d = TableMapper(table_fixed, ch.fieldmap_new)
        table_new = d2d.data_new

        # Write the table to a new csv file for import to NB.
        self.csv_filename_new = csv_register.replace(
            '.csv', 'NB.csv').replace('.xlsx', 'NB.csv')
        filehandler.csv_write(
            table_new, self.csv_filename_new, ch.fieldnames_new)
#         filehandler.csv_print(table_new, fieldnames_new)


class TableFixer(object):

    def __init__(self, config=None, table0=None):
        self.config = config
        self.table0 = table0

    def fix_table(self):
        '''Returns new table given old table
        '''
        return [self.fix_row(row0) for row0 in self.table0]

    def fix_row(self, row0):
        '''Creates new row from old row
        '''
        return {fieldname1: self.fix_field(fieldname0, row0)
                for (fieldname1, fieldname0) in self.config.items()}

    @classmethod
    def fix_field(self, fieldname0, row0):
        '''Creates new field from old field(s)
        '''
        if fieldname0 == None:
            return None
        elif isinstance(fieldname0, str):
            return row0.get(fieldname0)
        elif isinstance(fieldname0, tuple):
             func = fieldname0[0]
             kwargs = fieldname0[1]
             if callable(func):
                 return func(row0, **kwargs)
        raise TypeError('TableFixer.fix_field: expected str or (func, kwargs). Got:{}'.format(fieldname0))

    @classmethod
    def merge_pd_eno(cls, row0, pd=None, eno=None):
        '''Merged PD & zero padded eno,
        takes: pd key_old and eno key_old.eg:
        {'pd':'polldist', 'eno':'elect no',} -> {'statefile_id':EA0012',}
        '''
        pd = row0.get(pd)
        eno = row0.get(eno)
        eno_padded = cls.pad_eno(eno)
        try:
            return pd + eno_padded
        except TypeError as e:
            print('pd:{} eno:{} eno_padded:{}'.format(pd, eno, eno_padded))
            raise

    @classmethod
    def pad_eno(cls, eno):
        return '%04d' % (int(eno),)

    @classmethod
    def fix_address1(cls, row, housename='', street_number='', street_name=''):
        return ' '.join([row.get(housename), row.get(street_number),
                         row.get(street_name)]).strip()

    @classmethod
    def fix_address2(cls, row, block_name=''):
        return row.get(block_name)

    @classmethod
    def background_merge(cls, row, notes='', comments=''):
        return ' '.join([row.get(notes), row.get(comments)])

    @classmethod
    def tags_add(cls, row, fieldnames=[], tag_map={}):
        '''For each field in fieldnames. Eg: 'Demographic','national', 'Local','Post', 'Vote14', 'Vote12'
        return tag_list as string, eg: 'ResidentsParking,StreetsAhead,Vote14'
        '''
        return ','.join([cls.tags_split(row.get(fieldname), tag_map) for fieldname in fieldnames])

    @classmethod
    def tags_split(cls, fieldvalue, tag_map):
        '''Split value into tags. Eg: value='ResPark, StrtAhed'
        return tag_list as string, eg: 'ResidentsParking,StreetsAhead'
        '''
        tag_list0 = fieldvalue.split(',')
        tag_list = [tag_map.get(k) for k in tag_list0]
        return ','.join(tag_list)


class TableMapper(object):

    '''Map original table (row of dicts) to new table (row of dicts).
    Read original table and field mapper. Write new table with new field names.
    Values unchanged'''

    def __init__(self, data, fieldmap):
        self.data_new = self.mapdata(data, fieldmap)

    def maprow(self, row, fieldmap):
        return {key_new: row[key_old] for key_old, key_new in fieldmap.items()}

    def mapdata(self, data, fieldmap):
        return [self.maprow(row, fieldmap) for row in data]

if __name__ == '__main__':
    config = None
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
        elif search('canvass', csv_filename, IGNORECASE):
            config = canvassing
        elif search('nationbuilder.+NB', csv_filename):
            config = config_nationbuilderNB
        elif search('nationbuilder', csv_filename):
            config = config_nationbuilder
        elif search('BroomhillCanvassData', csv_filename):
            config = config_robin_latimer
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
        csvfixer = CsvFixer(csv_filename, config, reader)
        print(csvfixer.csv_filename_new)
