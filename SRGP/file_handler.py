#!/usr/bin/python3
'''
Created on 13 Sep 2015

@author: julian

# Read write csv from/to Dict (list dict)

'''
import csv
from os.path import expanduser
import re


class FileHandler(object):

    '''Handle reading and writing files, including the config file which is loaded as a Python module.
    '''

    def csv_read(self, pathname, fieldnames_expected, skip_lines=0):
        '''Read csv file (excluding 1st row) into self.table.
        Populate self.fieldnames with fields from 1st row in order
        Expands ~ in pathname to /home/<user>'''
        with open(expanduser(pathname), 'r', encoding='utf-8', errors='ignore') as fh:
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
                                 + '\nmismatch:' + ','.join(sorted(fields_odd))
                                 + 'type: actual:{}, expected:{}'.format(type(fieldnames), type(fieldnames_expected)))
        return (table, fieldnames)

    def find_mismatch(self, set0, set1):
        '''return difference of 2 iterables (lists, sets, tuples)
        as sorted list'''
        return sorted(list(set(set0).difference(set(set1))))

    def csv_write(self, table, pathname, fieldnames2):
        '''
                Expands ~ in pathname to /home/<user>
        '''
        with open(expanduser(pathname), 'w') as fh:
            self. csv_write_fh(table, fh, fieldnames2)

    def csv_write_fh(self, table, fh, fieldnames2):
        dw = csv.DictWriter(fh, fieldnames2)
        dw.writeheader()
        dw.writerows(table)
