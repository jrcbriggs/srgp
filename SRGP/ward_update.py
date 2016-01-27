#!/usr/bin/python3
'''
Created on 5 Sep 2015

@author: julian

# Read in register and streets

'''
import itertools
from re import IGNORECASE, search
import re
import sys

from file_handler import FileHandler


class RegisterUpdater(object):
    regex = '^(Above|Back [Oo]f|Bk|First Floor|Flat Above \\(Back\\)|Flat At Rear Of|Flat Over|Ground Floor|Over|Rear( [Oo]f)?)\s+'

    def street_field_clean(self, street_field):
        return re.sub(self.regex, '', street_field.strip())

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
        street_number = self.street_field_clean(street_number)
        street_name = self.street_field_clean(street_name)

        # If Address 4 has a leading number split Address 4 into: street number and street name
        m = re.match('(\d+),?(\S*)\s+(.+)', street_name)
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
            row['numbers'] = re.sub('[^-0-9,]', '', row['numbers'])
            try:
                (odd_even, street_numbers) = self.rangeexpand_odd_even(row['odd_even'], row['numbers'])
            except:
                print (row)
                raise
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
        elif odd_even == 'odds':
                return (street_number % 2 == 1)
        elif odd_even == 'evens':
                return (street_number % 2 == 0)
        else:
            raise ValueError('Unexpected value for odd_even {}'.format (odd_even))

    def pd2ward(self, pd):
        return {
            'E': 'Broomhill',
            'G': 'Central',
            # ~ 'H': 'Crookes & Crosspool',
            'H': 'Crookes',
            'L': 'Ecclesall',
            'O': 'Gleadless Valley',
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
            elif odd_even == 'odds':
                return ('', {e for e in r if e % 2 == 1})
            elif odd_even == 'evens':
                return ('', {e for e in r if e % 2 == 0})
        else:
            return (odd_even, set())

    def register_update(self, register, ward_lookup, number_fieldname, street_fieldname):
        ''' register: [{'PD':...,...},...]
        ward_lookup: {(<ward_old>, <street_address>), [{'odd_even':..., 'numbers': (3,4,5,...)'
        odd_even: '', 'odds', 'evens'
        street_fieldname: eg 'Address 4'
        '''
        errors = {}
        for row in register:
#             pd=row['PD']
#             pd = row['state_file_id'][:2]
#             ward_old = self.pd2ward(pd)
            ward_old = row['precinct_name']
            (street_number, street_name) = self.get_street_number_and_name(row[number_fieldname], row[street_fieldname])
            odd_even = 'odds' if street_number % 2 else 'evens'
            ward_lookup_by_number = ward_lookup.get(ward_old, {}).get(street_name, {})
            ward_old += '_OLD'
            row['ward_new'] = ward_lookup_by_number.get(street_number, ward_lookup_by_number.get(odd_even, ward_lookup_by_number.get('', ward_old)))
            if row['ward_new'] == ward_old:
                errors[street_name] = 'Street Name not matched'
        return (register, errors)

class Main(object):

    def __init__(self, fieldnames_register, fieldnames_street_spec):
        self.filehandler = FileHandler()
        self.register_updater = RegisterUpdater()
        self.fieldnames_register = fieldnames_register
        self.fieldnames_street_spec = fieldnames_street_spec

    '''The top level class.
    Read register csv file into a table (list of dict)
    Read street_spec csv file into a table (list of dict)
    Create ward_street_spec: {(ward, street_name): [ street_number_spec, street_number_spec,...], ...}
    Update the wards
    Write  to a new csv file.

    SKIP first line of csv line:  Date Published: 01/05/2015
    '''
    def register_update(self, csv_register, csv_street_spec, number_filename, street_fieldname):
        (register, street_spec) = self.csv_read(csv_register, csv_street_spec)

        # Create lookup
        ward_lookup = self.register_updater.get_ward_lookup(street_spec)

        # Append new wards to register table
        (register_updated, errors) = self.register_updater.register_update(register, ward_lookup, number_fieldname, street_fieldname)

        # Write the updated register to a new csv file
        self.filehandler.csv_write(register_updated, csv_register.replace('.csv', 'WardUpdated.csv'), fieldnames + ('ward_new',))

        for (k, v) in sorted(errors.items()):
            print(k, v)
    def csv_read(self, csv_register, csv_street_spec):
        '''Update ward names in register
        '''
        skip_lines = 0

        # Read register csv file into table (array of dict) register
        (register, unused) = self.filehandler.csv_read(csv_register, self.fieldnames_register, skip_lines)

        # Read street spec csv file into table (array of dict) street_spec
        (street_spec, unused) = self.filehandler.csv_read(csv_street_spec, self.fieldnames_street_spec)

        return (register, street_spec)


if __name__ == '__main__':
    # sys.argv = ['ward_update.py', '~/SRGP/register/2015_16/record_linking/TtwAndDevWardRegisters2015-12-01NB.csv', '~/SRGP/register/2014_15/ward_boundary_updates/streetspec/AllSorted.csv', ]
#     sys.argv = ['ward_update.py', '~/SRGP/civi/20160117/SRGP_MembersAll_20160117-2225NB.csv', '~/SRGP/register/2014_15/ward_boundary_updates/streetspec/AllSorted.csv', ]

    if len(sys.argv) != 3:
        print('Usage: ward_update.py <register.csv> <street_spec.csv>')
        exit()

    (csv_filename, csv_street_spec) = sys.argv[1:]

    if search('Register', csv_filename, IGNORECASE):
        fieldnames = tuple('state_file_id,prefix,first_name,middle_name,last_name,suffix,dob,registered_address1,registered_address2,registered_address3,registered_city,registered_zip,registered_country_code,is_voter,ward_name,registered_state,tag_list'.split(','))
#         number_fieldname = 'Address 2'
#         street_fieldname = 'Address 4'
        number_fieldname = 'registered_address1'
        street_fieldname = 'registered_address1'
    elif search('SRGP_', csv_filename, IGNORECASE):
        # civi
        fieldnames = tuple('first_name,last_name,email opt in,civicrm_id,membership_type,expires_on,started_at,membership_status,address_address1,address_address2,address_address3,address_city,address_zip,address_country_code,email,phone_number,mobile_number,precinct_name,party,is_deceased,party_member,support_level,registered_state,tag_list'.split(','))
#         number_fieldname = 'Address 2'
#         street_fieldname = 'Address 4'
        number_fieldname = 'address_address1'
        street_fieldname = 'address_address1'
    else:
        error('Unknown File type')
        exit

    fieldnames_street_spec = ('ward_old', 'street_name', 'odd_even', 'numbers', 'ward_new', 'notes')
    m = Main(fieldnames, fieldnames_street_spec)
    m.register_update(csv_filename, csv_street_spec, number_fieldname, street_fieldname)

