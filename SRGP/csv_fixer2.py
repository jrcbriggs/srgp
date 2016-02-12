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
from io import StringIO
import mmap
import os
from os.path import basename, splitext
from re import compile, IGNORECASE, sub
from re import search
from sys import argv
from sys import stdout
import xlrd


class FileHandler(object):

    '''Handle reading and writing files, including the config file which is loaded as a Python module.
    '''

    def csv_read(self, pathname):
        '''Read csv file (excluding 1st row) into self.table.
        Populate self.fieldnames with fields from 1st row in order'''
        with open(pathname, 'r', encoding='utf-8', errors='ignore') as fh:
            return self.csv_read_fh(fh)

    def csv_read_fh(self, fh):
        '''Read csv file (excluding 1st row) into self.table.
        Populate self.fieldnames with fields from 1st row in order'''
        dr = DictReader(fh)
        return [row for row in dr]

    def csv_print(self, table, fieldnames2):
        self.csv_write_fh(table, stdout, fieldnames2)

    def csv_write(self, table, pathname, fieldnames2):
        with open(pathname, 'w') as fh:
            self. csv_write_fh(table, fh, fieldnames2)

    def csv_write_fh(self, table, fh, fieldnames2):
        dw = DictWriter(fh, fieldnames2)
        dw.writeheader()
        dw.writerows(table)

class CsvFixer(object):

    '''The top level class.
    Read csv data file into a table
    Fix the data in table
    Create new table: with NB table column headings
    Write the table to a new csv file for import to NB.
    '''
    def fix_csv(self, filename, config, filereader, filewriter):

        # Read csv data file into a table
        table0 = filereader(filename)

        # Fix the data in table
        table1 = TableFixer(config=config).fix_table(table0)

        # Write the table to a new csv file for import to NB.
        filename_new = filename.replace('.csv', 'NB.csv')
        fieldnames = config.keys()
        filewriter(table1, filename_new, fieldnames)
        return filename_new

class TableFixer(object):

    def __init__(self, config=None):
        self.config = config

    def fix_table(self, table0):
        '''Returns new table given old table
        '''
        try:
            return [self.fix_row(row0) for row0 in table0]
        except (IndexError, KeyError, TypeError) as e:
            e.args += ('config:', self.config,)
            raise

    def fix_row(self, row0):
        '''Creates new row from old row
        '''
        try:
            return {fieldname1: self.fix_field(row0, arg0)
                for (fieldname1, arg0) in self.config.items()}
        except (IndexError, KeyError, TypeError) as e:
            e.args += ('row0:', row0,)
            raise

    def fix_field(self, row0, arg0):
        '''Creates new field from old field(s)
        '''
        try:
            if arg0 == None:
                return None
            elif isinstance(arg0, str):
                return row0.get(arg0).strip()
            elif isinstance(arg0, tuple):
                 (func, args, kwargs0) = arg0
                 if callable(func):
                     kwargs = {k: row0[v] for (k, v) in kwargs0.items()}
                     return func(*args, **kwargs)
            raise TypeError('TableFixer.fix_field: expected str or (func, kwargs). Got:{}'.format(arg0))
        except (IndexError, KeyError, TypeError) as e:
            e.args += ('fix_field', 'row0:', row0, 'arg0:', arg0,)
            raise

    @classmethod
    def background_merge(cls, notes='', comments=''):
        return ' '.join([notes, comments])

    @classmethod
    def doa2dob(cls, doa=None):
        '''Convert date of attainment (ie reach 18years old) to DoB in US format: mm/dd/yyyy.
            Use after converting to NB date format.
            yoa: year of attainment, yob: year of birth'''
        if doa:
            (day, month, yoa) = doa.split('/')
            yob = str(int(yoa) - 18)
            return '/'.join([month, day, yob])
        else:
            return doa

    @classmethod
    def fix_address1(cls, housename='', street_number='', street_name=''):
        return ' '.join([housename, street_number, street_name]).strip()

    @classmethod
    def fix_address2(cls, block_name=''):
        return block_name

    @classmethod
    def fix_party(cls, party_map, party=None):
        return party_map[party]

    @classmethod
    def fix_support_level(cls, support_level_map, support_level=None):
        return support_level_map[support_level]

    @classmethod
    def merge_pd_eno(cls, pd=None, eno=None):
        '''Merged PD & zero padded eno,
        takes: pd old and eno old.eg:
        {'pd':'polldist', 'eno':'elect no',} -> {'statefile_id':EA0012',}
        '''
        eno_padded = None
        try:
            pd = pd.lstrip('!')
            eno_padded = cls.pad_eno(eno)
            return pd + eno_padded
        except (TypeError) as e:
            e.args += ('pd:{} eno:{} eno_padded:{}'.format(pd, eno, eno_padded))
            raise

    @classmethod
    def pad_eno(cls, eno):
        return '%04d' % (int(eno),)

    @classmethod
    def tags_add(cls, tag_map, **kwargs):
        '''For tag_str0 in tag_lists0 (values in kwargs), eg: 'ResidentsParking,StreetsAhead','Ben, Bins', '','', 'Vote14', 'Vote12'}
            Split into tag0 elements in tag_list0:
              Strip (leading and trailing) white space from tag0
              Convert tag0 tag1 elements in tag_list1
              Merge into tag_list1 removing empty tags ('')
              Sort
              Convert to string tag_str1
            Return tags_str1
        '''
        try:
            tag_lists0 = kwargs.values()
            tag_lists1 = [cls.tags_split(tag_map, tag_str0) for tag_str0 in tag_lists0]
            tag_str1 = ','.join(sorted([tag for tag_list in tag_lists1 for tag in tag_list if tag != '']))
            return tag_str1
        except (KeyError) as e:
            e.args += ('tags_add', 'tag_map:', tag_map, 'kwargs:', kwargs,)
            raise

    @classmethod
    def tags_split(cls, tag_map, tag_str0):
        '''For a single tag_str0:
              Split into tag0 elements in tag_list0
              Strip (leading and trailing) white space from tag0
              Convert tag0 to tag1 elements in tag_list1
           Return tag_list as string, eg: 'ResidentsParking,StreetsAhead'
        '''
        try:
            tag_list0 = tag_str0.split(',')  # 'stdt,ResPark' -> ['stdt','ResPark']
            tag_list1 = [tag_map[tag0.strip()] for tag0 in tag_list0]  # ['Student','ResidentsParking']
            return tag_list1
        except (KeyError) as e:
            e.args += ('tags_split', 'tag_map:', tag_map, 'tag_str0:', tag_str0,)
            raise


class Main():

    def __init__(self, filereader=None, filewriter=None):
        '''Create filereader and fielwriter unless given in kwargs
        '''
        fh = FileHandler()
        self.filereader = filereader or fh.csv_read
        self.filewriter = filereader or fh.csv_write

    def main(self):
        '''Fix one or more files for input to NB
        Lookup config using part of filename in order
        '''
        config_lookup = [
                         ('BroomhillCanvassData', config_rl),
                         ]
        for filename in argv[1:]:  # skip scriptname in argv[0]
            # Find config varname to match csv filename
            for (name , config) in config_lookup:
                if search(name, filename):
                    print('Using config: {}'.format(config.get('config_name')))
                    del config['config_name']
                    self.fix_csv(filename, config)
                    break
            else:
                raise Exception('config not found for filename:{}'.format(filename))

    def fix_csv(self, filename, config):
        filename_new = CsvFixer().fix_csv(filename, config, filereader=self.filereader, filewriter=self.filewriter)
        print(filename_new)

if __name__ == '__main__':
    from configurations2 import config_rl
    argv.append('/home/julian/SRGP/canvassing/2014_15/broomhill/csv/BroomhillCanvassData2015-03EA-H.csv')
    Main().main()
