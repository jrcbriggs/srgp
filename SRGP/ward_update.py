#!/usr/bin/python3
'''
Created on 5 Sep 2015

@author: julian

# Read in register and streets

'''
import csv
import itertools
from os.path import expanduser
import re


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
        return set(itertools.chain.from_iterable(ranges))
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


def get_ward_lookup(street_spec):
    ward_lookup = {}
    for row in street_spec:
        ward_lookup_by_number = ward_lookup.setdefault(row['ward_old'], {}).setdefault(row['street_name'], {})
        (odd_even, street_numbers) = rangeexpand_odd_even(row['odd_even'], row['numbers'])
        if street_numbers:
            for street_number in street_numbers:
#                 ward_lookup_by_number[street_number] = row['ward_new']
                ward_lookup_by_number.setdefault(street_number, row['ward_new'])
        else:
            ward_lookup_by_number[odd_even] = row['ward_new']
    return ward_lookup

class CsvWardUpdate(object):

    '''The top level class.
    Read register csv file into a table (list of dict)
    Read street_spec csv file into a table (list of dict)
    Create ward_street_spec: {(ward, street_name): [ street_number_spec, street_number_spec,...], ...}
    Update the wards
    Write  to a new csv file.

    SKIP first line of csv line:  Date Published: 01/05/2015
    '''

    def __init__(self, csv_register, csv_street_spec):
        fieldnames = ('PD', 'ENO', 'Status', 'Title', 'First Names', 'Initials', 'Surname', 'Suffix', 'Date of Attainment', 'Franchise Flag', 'Address 1', 'Address 2', 'Address 3', 'Address 4', 'Address 5', 'Address 6', 'Address 7', 'Address 8', 'Address 9', 'Postcode')
        skip_lines = 1
        filehandler = FileHandler()

        # Read register csv file into table (array of dict) register
        (register, unused) = filehandler.csv_read(csv_register, fieldnames, skip_lines)

        # Read street spec csv file into table (array of dict) street_spec
        fieldnames2 = ('ward_old', 'street_name', 'odd_even', 'numbers', 'ward_new', 'notes')
        (street_spec, unused) = filehandler.csv_read(csv_street_spec, fieldnames2)
        ward_street_spec = get_ward_lookup(street_spec)

        # Append new wards to register table
        twu = TableWardUpdate()
        number_fieldname = 'Address 2'
        street_fieldname = 'Address 4'
        register_updated = twu.csv_read(register, ward_street_spec, number_fieldname, street_fieldname)

        # Write the updated register to a new csv file
        self.csv_register_updated = csv_register.replace('.csv', 'WardUpdated.csv')
        fieldnames_new = fieldnames + ('ward_new',)
        filehandler.csv_write(register_updated, self.csv_register_updated, fieldnames_new)


class FileHandler(object):

    '''Handle reading and writing files, including the config file which is loaded as a Python module.
    '''

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
        dr = csv.DictReader(fh)
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
                                 + '\nn columns in csv file:{}'.format(len(fieldnames))
                                 + '\nn fields expected:{}'.format(len(fieldnames_expected))
                                 + '\nmismatch:' + ','.join(sorted(fields_odd)))
        return (table, fieldnames)

    def find_mismatch(self, set0, set1):
        '''return difference of 2 iterables (lists, sets, tuples)
        as sorted list'''
        return sorted(list(set(set0).difference(set(set1))))

    def csv_write(self, table, pathname, fieldnames2):
        with open(pathname, 'w') as fh:
            self. csv_write_fh(table, fh, fieldnames2)

    def csv_write_fh(self, table, fh, fieldnames2):
        dw = csv.DictWriter(fh, fieldnames2)
        dw.writeheader()
        dw.writerows(table)


class TableWardUpdate(object):

    def clean_street_number_and_name(self, street_number, street_name):
        '''In the register (2015-04-20):
        street number is usually in column: Address 2
        street name is usually in column: Address 4
        Sometimes the number (Address 2) looks like: 12A, 12-14, 12/3,
        For ward allocation we can strip all these down to 12.
        Sometimes Address 2 holds a flat number (or similar) and the street number is prepended to the street address (Address 4):
        3 Arran Road. In this case we extract the number for Address 4.
        '''
        # strip leading and trailing spaces
        street_number = street_number.strip()
        street_name = street_name.strip()

        # If Address 4 has a leading number split Address 4 into: street number and street name
        m = re.match('(\d+)(\S*)\s+(.+)', street_name)
        if m:
            (street_number, unused, street_name) = m.groups()

        # Remove all but leading digits from street number
        street_number = re.sub('^(\d+).*', '\\1', street_number)  # 123A -> 123
        street_number = re.sub('[^\d]', '', street_number)  # Ant House -> ''

        # If Address 2 held a house name (no digits) then street number may now be ''. Change it to 0. TODO: This might set wrong ward on Boundary or Cross Streets.
        street_number = int(street_number or '0')
        return (street_number, street_name)

    def is_in_ward_new(self, street_number, odd_even, numbers):
        ''' odd_even and numbers are pre-processed so either odd_even or numbers are set , never both
        '''
        if street_number == 0:
            return False  # Street number field likely held a house name. We cannot handle this.
        if odd_even == '':
                return street_number in numbers if numbers else True
        elif odd_even == 'odd':
                return (street_number % 2 == 1)
        elif odd_even == 'even':
                return (street_number % 2 == 0)
        else:
            raise Exception('Unexpected value for odd_even {}'.format (odd_even))

    def csv_read(self, register, ward_lookup, number_fieldname, street_fieldname):
        ''' register: [{'PD':...,...},...]
        ward_lookup: {(<ward_old>, <street_address>), [{'odd_even':..., 'numbers': (3,4,5,...)'
        odd_even: '', 'odd', 'even'
        street_fieldname: eg 'Address 4'
        '''
        for row in register:
            ward_old = pd2ward(row['PD'])
            (street_number, street_name) = self.clean_street_number_and_name(row[number_fieldname], row[street_fieldname])
            odd_even = 'odd' if street_number % 2 else 'even'
            ward_lookup_by_number = ward_lookup.get(ward_old, {}).get(street_name, {})
            row['ward_new'] = ward_lookup_by_number.get(street_number, ward_lookup_by_number.get(odd_even, ward_lookup_by_number.get('', ward_old)))
            if row['ward_new'] == ward_old:
                print('Street Name not matched:', street_name)
        return register


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
            csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
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

    def csv_read(self, csv_register, csv_street_spec):
        '''Update ward names in register
        '''
        csv_street_names = '/home/julian/SRGP/register/crookes/street_names.csv'
        cwu = CsvWardUpdate(csv_register, csv_street_spec)


if __name__ == '__main__':
    m = Main()
#     csv_register = expanduser('~/SRGP/register/all/CentralConstituency_crookes_ecclesall_Register2015-04-20.csv')
#     m.create_street_names_by_ward(csv_register)

    csv_register = expanduser('~/SRGP/register/crookes/CrookesWardRegister2015-04-20.csv')
#     csv_register = expanduser('~/SRGP/register/central/CentralConstituencyRegister2015-05-01.csv')
    csv_street_spec = expanduser('~/SRGP/register/crookes/CrookesStreetSpec.csv')
    m.csv_read(csv_register, csv_street_spec)
