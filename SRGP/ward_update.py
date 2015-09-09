#!/usr/bin/python3
'''
Created on 5 Sep 2015

@author: julian

# Read in register and streets

'''
from _csv import writer
from copy import deepcopy
from csv import DictReader, DictWriter
import csv
from importlib import import_module
from itertools import chain
import re
from sys import argv
from sys import stdout


def pd2ward(pd):
    return {
        'E': 'Broomhill',
        'G': 'Central',
        # ~ 'H': 'Crookes & Crosspool',
        'H': 'Crookes',
        'L': 'Ecclesall',
        'R': 'Manor Castle',
        'T': 'Nether Edge',
        'Z': 'Walkley',
    }[pd[0]]


def rangeexpand(numbers):
    ''''1-3,6,8-10' -> {1, 2, 3, 6, 8, 9, 10}
    '' -> {} #empty set
    '''
    if numbers:
        spans = (el.partition('-')[::2] for el in numbers.split(','))
        ranges = (range(int(s), int(e) + 1 if e else int(s) + 1) for s, e in spans)
        return set(chain.from_iterable(ranges))
    else:
        return set()


def rangeexpand_odd_even(odd_even, numbers):
    ''''1-3,6,8-10' -> {1, 2, 3, 6, 8, 9, 10}
    TODO
    '''
    r = rangeexpand(numbers)
    if r:
        if odd_even == '':
            return ('', r)
        elif odd_even == 'odd':
            return ('', {e for e in r if e % 2 == 1})
        elif odd_even == 'even':
            return ('', {e for e in r if e % 2 == 0})
    else:
        return (odd_even, set())


def street_spec2ward_street_name(street_spec):
    ward_street_name = {}
    for row in street_spec:
        row['numbers'] = rangeexpand(row['numbers'])
        ward_street_name.setdefault((row['ward_old'], row['street_name']), []).append(row)
    return ward_street_name


class CsvWardUpdate(object):

    '''The top level class.
    Read csv data file into a table
    Update the wards
    Write  to a new csv file.
    '''

    def __init__(self, csv_register, csv_street_spec):
        fieldnames = ['PD', 'ENO', 'Status', 'Title', 'First Names', 'Initials', 'Surname', 'Suffix', 'Date of Attainment', 'Franchise Flag', 'Address 1', 'Address 2', 'Address 3', 'Address 4', 'Address 5', 'Address 6', 'Address 7', 'Address 8', 'Address 9', 'Postcode']
        skip_lines = 1
        filehandler = FileHandler()

        # Read csv data file into a table
        (table, unused) = filehandler.csv_read(csv_register, fieldnames, skip_lines)

        # Read csv street spec into a dict
        (street_spec_array, unused) = filehandler.csv_read(csv_street_spec, ['street_name'])
        street_names = {row['street_name'] for row in street_spec_array}  # set

        # Update table
        twu = TableWardUpdate()
        street_fieldname = 'Address 4'
        table_new = twu.ward_update(table, street_names, street_fieldname)

        # Write the updated table to a new csv file
        self.csv_filename_new = csv_register.replace('.csv', 'WardUpdated.csv')
        fieldnames_new = fieldnames + ['ward_new']
        filehandler.csv_write(
            table_new, self.csv_filename_new, fieldnames_new)


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
#         if len(fieldnames) == len(fieldnames_expected):
#             if fieldnames != fieldnames_expected:
#                 fields_odd = self.find_mismatch(
#                     fieldnames, fieldnames_expected)
#                 raise ValueError('Unexpected fieldnames:\nactual  : '
#                                  + ','.join(sorted(fieldnames))
#                                  + '\nexpected: ' +
#                                  ','.join(sorted(fieldnames_expected))
#                                  + '\nmismatch:' + ','.join(sorted(fields_odd)))
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


class TableWardUpdate(object):

    def ward_update(self, register, street_spec, street_fieldname):
        ''' register: [{'PD':...,...},...]
        street_spec: {(<ward_old>, <street_address>), [{'odd_even':..., 'numbers': (3,4,5,...)'
        odd_even: '', 'odd', 'even'
        street_fieldname: eg 'Address 4'
        '''
        table_new = deepcopy(register)
        for row in table_new:
            street_address = row[street_fieldname].strip()
            pd = row['PD']
            ward_old = pd2ward(pd)
            try:
                (street_number,) = re.match('(\d+)\s+(.+)', street_address)
                street_name = re.sub('^\d+[-/\d]+\s+', '', street_address)
                specs = street_spec.get((ward_old, street_name), [])
                for spec in specs:
                    odd_even = spec['odd_even']
                    numbers = spec['numbers']
                    ward_new = spec['ward_new']

                    if self.is_in_ward(street_number, odd_even, numbers):
                        row['ward'] = ward_new
                    else:
                        pass  # leave ward field unchanged
                if not specs:
                    print('Street Name not matched:', street_address)
            except:
                pass
            return table_new

    def is_in_ward(self, street_number, odd_even, numbers):
        ''' odd_even and numbers are pre-processed so either odd_even or numbers are set , never both
        '''
        if odd_even == '':
                return street_number in numbers if numbers else True
        elif odd_even == 'odd':
                return (street_number % 2 == 1)
        elif odd_even == 'even':
                return (street_number % 2 == 0)
        else:
            raise Exception('Unexpected value for odd_even {}'.format (odd_even))


class StreetName(object):
    '''Create street names by ward.
    {ward:{street_name, street_name, ...}} dict of set of street names
    '''
    def __init__(self, csv_register, street_fieldname):
        fieldnames = ['PD', 'ENO', 'Status', 'Title', 'First Names', 'Initials', 'Surname', 'Suffix', 'Date of Attainment', 'Franchise Flag', 'Address 1', 'Address 2', 'Address 3', 'Address 4', 'Address 5', 'Address 6', 'Address 7', 'Address 8', 'Address 9', 'Postcode']
        skip_lines = 1
        self.filehandler = FileHandler()

        # Read csv data file into a table
        (register, unused) = self.filehandler.csv_read(csv_register, fieldnames, skip_lines)
        self.street_names_set = {}
        for row in register:
            ward = pd2ward(row['PD'])
            street_name = row[street_fieldname].strip()
            street_name = re.sub('^\d+\w*\s+', '', street_name)
            street_name = re.sub('^[-/\s\d]+', '', street_name)
            if street_name:
                self.street_names_set.setdefault(ward, set()).add(street_name)

    def write(self, csv_street_names):
        street_names_array2d = []
        for (ward, street_names) in sorted(self.street_names_set.items()):
            row = [ward] + sorted(list(street_names))
            street_names_array2d.append(row)
        # Pad
        nrows = max([len(row)for row in street_names_array2d])
        for ward_row in street_names_array2d:
            ward_row += [''] * (nrows - len(ward_row))
        # Transpose
        street_names_table = zip(*street_names_array2d)
        # Write
        with open(csv_street_names, 'w', newline='') as csvfile:
            csv_writer = writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in street_names_table:
                csv_writer.writerow(row)


class Main(object):

    def create_street_names_by_ward(self, csv_register):
        ''' Extract street names by ward from register and write to csv
        '''
        street_fieldname = 'Address 4'
        sn = StreetName(csv_register, street_fieldname)
        csv_street_names = csv_register.replace('.csv', '_St.csv')
        sn.write(csv_street_names)

    def ward_update(self, csv_register, csv_street_spec):
        '''Update ward names in register
        '''
        csv_street_names = '/home/julian/SRGP/register/crookes/street_names.csv'
        cwu = CsvWardUpdate(csv_register, csv_street_spec)


if __name__ == '__main__':
    m = Main()
    csv_register = '/home/julian/SRGP/register/all/CentralConstituency_crookes_ecclesall_Register2015-04-20.csv'
#     m.create_street_names_by_ward(csv_register)

    csv_register = '/home/julian/SRGP/register/crookes/CrookesWardRegister2015-04-20.csv'
    csv_street_spec = '/home/julian/SRGP/register/crookes/CrookesStreetSpec.csv'
    m.ward_update(csv_register, csv_street_spec)

