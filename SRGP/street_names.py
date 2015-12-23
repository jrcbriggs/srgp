#!/usr/bin/python3
'''
Created on 13 Sep 2015

@author: julian

# Extract street names from a register

'''
import csv
from os.path import expanduser
import re

from file_handler import FileHandler


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

class StreetName(object):
    '''Create street names by ward.
    {ward:{street_name, street_name, ...}} dict of set of street names
    '''
    def __init__(self, csv_register, street_fieldname):
        fieldnames = ('PD', 'ENO', 'Status', 'Title', 'First Names', 'Initials', 'Surname', 'Suffix', 'Date of Attainment', 'Franchise Flag', 'Address 1', 'Address 2', 'Address 3', 'Address 4', 'Address 5', 'Address 6', 'Address 7', 'Address 8', 'Address 9', 'Postcode')
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
        with open(expanduser(csv_street_names), 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in street_names_table:
                csv_writer.writerow(row)


class Main(object):

    def create_street_names_by_ward(self, csv_register):
        ''' Extract street names by ward from register and write to csv
        '''
        street_fieldname = 'Address 4'
        sn = StreetName(csv_register, street_fieldname)
        csv_street_names = csv_register.replace('.csv', '_Steet_Names.csv')
        sn.write(csv_street_names)


if __name__ == '__main__':
    m = Main()
    csv_register = '~/SRGP/register/all/CentralConstituency_crookes_ecclesall_Register2015-04-20.csv'
    m.create_street_names_by_ward(csv_register)
