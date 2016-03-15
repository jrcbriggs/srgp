#!/usr/bin/env python

"""
Parse CSV dump from NationBuilder, remove UTF-8 accents and generate another
CSV containing only the fields we want to use
"""

import csv
import sys
import unicodedata

fields = [
    'nationbuilder_id',
    'state_file_id',
    'prefix',
    'first_name',
    'middle_name',
    'last_name',
    'suffix',
    'registered_address1',
    'registered_address2',
    'registered_address3',
    'registered_city',
    'registered_zip',
    'registered_state',
    'precinct_name',
    'tag_list',
]


def strip_mn(ustring):
    return u''.join(c for c in unicodedata.normalize('NFD', ustring)
                    if unicodedata.category(c) != 'Mn')


def unicode_reader(unicode_csv_data):
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data))
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        line = unicode(line, 'utf-8')
        line = strip_mn(line)
        try:
            yield line.encode('utf-8')
        except UnicodeError as e:
            print(line)
            raise e


if __name__ == '__main__':
    if os.getenv('DATADIR'):
        datadir = os.getenv('DATADIR')
        if not os.path.exists(datadir):
            print("Data directory %d does not exist" % datadir)
            sys.exit(1)

    datadir = os.path.expanduser('~/SRGP/register/2015_16/CentralConstituency')
    output_file = os.path.join(datadir, 'NationBuilder2016-03-01NB.csv')
    output = open(output_file)
    output.write(",".join(fields))
    output.write("\n")


    nationbuilder_csv = os.path.join(
        datadir, 'nationbuilder-people-export-373-2016-03-03.csv')

    with open(nationbuilder_csv, 'rU') as f:
        reader = unicode_reader(f)
        firstrow_read = False
        headers = []
        for row in reader:
            if not firstrow_read:
                headers = row
                firstrow_read = True
                continue

            lineData = []
            for field in fields:
                data = row[headers.index(field)]
                if data:
                    lineData.append('"%s"' % data)
                else:
                    lineData.append('')

            try:
                output.write(",".join(lineData))
            except UnicodeEncodeError as e:
                print(u','.join(lineData))
                raise e

            output.write("\n")

    output.close()
