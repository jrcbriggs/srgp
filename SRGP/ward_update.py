#!/usr/bin/python3
'''
Created on 5 Sep 2015

@author: julian

# Read in register and streets

'''
import itertools
import re

from file_handler import FileHandler


class RegisterUpdater(object):

    def get_street_number_and_name(self, street_number, street_name):
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

    def get_ward_lookup(self, street_spec):
        ward_lookup = {}
        for row in street_spec:
            ward_lookup_by_number = ward_lookup.setdefault(row['ward_old'], {}).setdefault(row['street_name'], {})
            (odd_even, street_numbers) = self.rangeexpand_odd_even(row['odd_even'], row['numbers'])
            if street_numbers:
                for street_number in street_numbers:
                    ward_lookup_by_number.setdefault(street_number, row['ward_new'])
            else:
                ward_lookup_by_number[odd_even] = row['ward_new']
        return ward_lookup

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

    def pd2ward(self, pd):
        return {'G': 'Central',
            # ~ 'H': 'Crookes & Crosspool',
            'H': 'Crookes',
            'L': 'Ecclesall',
            'R': 'Manor Castle',
            'T': 'Nether Edge',
            'Z': 'Walkley',
        }[pd[0]]

    def rangeexpand(self, numbers):
        ''''1-3,6,8-10' -> {1, 2, 3, 6, 8, 9, 10}
        '' -> {} #empty set
        '''
        if numbers:
            spans = (el.partition('-')[::2] for el in numbers.split(','))
            ranges = (range(int(s), int(e) + 1 if e else int(s) + 1) for s, e in spans)
            return set(itertools.chain.from_iterable(ranges))
        else:
            return set()

    def rangeexpand_odd_even(self, odd_even, numbers):
        ''''1-3,6,8-10' -> {1, 2, 3, 6, 8, 9, 10}
        TODO
        '''
        r = self.rangeexpand(numbers)
        if r:
            if odd_even == '':
                return ('', r)
            elif odd_even == 'odd':
                return ('', {e for e in r if e % 2 == 1})
            elif odd_even == 'even':
                return ('', {e for e in r if e % 2 == 0})
        else:
            return (odd_even, set())

    def register_update(self, register, ward_lookup, number_fieldname, street_fieldname):
        ''' register: [{'PD':...,...},...]
        ward_lookup: {(<ward_old>, <street_address>), [{'odd_even':..., 'numbers': (3,4,5,...)'
        odd_even: '', 'odd', 'even'
        street_fieldname: eg 'Address 4'
        '''
        for row in register:
            ward_old = self.pd2ward(row['PD'])
            (street_number, street_name) = self.get_street_number_and_name(row[number_fieldname], row[street_fieldname])
            odd_even = 'odd' if street_number % 2 else 'even'
            ward_lookup_by_number = ward_lookup.get(ward_old, {}).get(street_name, {})
            row['ward_new'] = ward_lookup_by_number.get(street_number, ward_lookup_by_number.get(odd_even, ward_lookup_by_number.get('', ward_old)))
            if row['ward_new'] == ward_old.upper() :
                print('Street Name not matched:', street_name)
        return register
 
class Main(object):

    def __init__(self):
        self.filehandler = FileHandler()
        self.register_updater = RegisterUpdater()

    '''The top level class.
    Read register csv file into a table (list of dict)
    Read street_spec csv file into a table (list of dict)
    Create ward_street_spec: {(ward, street_name): [ street_number_spec, street_number_spec,...], ...}
    Update the wards
    Write  to a new csv file.

    SKIP first line of csv line:  Date Published: 01/05/2015
    '''
    def register_update(self, csv_register, fieldnames_register, csv_street_spec, fieldnames_street_spec):
        (register, street_spec) = self.csv_read(csv_register, csv_street_spec)

        # Create lookup
        ward_lookup = self.register_updater.get_ward_lookup(street_spec)

        # Append new wards to register table
        number_fieldname = 'Address 2'
        street_fieldname = 'Address 4'
        register_updated = self.register_updater.register_update(register, ward_lookup, number_fieldname, street_fieldname)

        # Write the updated register to a new csv file
        self.csv_write(register_updated, csv_register.replace('.csv', 'WardUpdated.csv'), fieldnames_register + ('ward_new',))

    def csv_read(self, csv_register, fieldnames_register, csv_street_spec, fieldnames_street_spec):
        '''Update ward names in register
        '''
        skip_lines = 1

        # Read register csv file into table (array of dict) register
        (register, unused) = self.filehandler.csv_read(csv_register, fieldnames_register, skip_lines)

        # Read street spec csv file into table (array of dict) street_spec
        (street_spec, unused) = self.filehandler.csv_read(csv_street_spec, fieldnames_street_spec)

        return (register, street_spec)

    def csv_write(self, register, csv_register, fieldnames_register):
        self.filehandler.csv_write(register, csv_register, fieldnames_register)



if __name__ == '__main__':
    fieldnames_register = ('PD', 'ENO', 'Status', 'Title', 'First Names', 'Initials', 'Surname', 'Suffix', 'Date of Attainment', 'Franchise Flag', 'Address 1', 'Address 2', 'Address 3', 'Address 4', 'Address 5', 'Address 6', 'Address 7', 'Address 8', 'Address 9', 'Postcode')
    fieldnames_street_spec = ('ward_old', 'street_name', 'odd_even', 'numbers', 'ward_new', 'notes')
#     csv_register = '~/SRGP/register/all/CentralConstituency_crookes_ecclesall_Register2015-04-20.csv'

    csv_register = '~/SRGP/register/crookes/CrookesWardRegister2015-04-20.csv'
#     csv_register = '~/SRGP/register/central/CentralConstituencyRegister2015-05-01.csv'
    csv_street_spec = '~/SRGP/register/crookes/CrookesStreetSpec.csv'
    m = Main(csv_register, csv_street_spec)
