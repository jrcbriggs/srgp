'''
Created on 24 Feb 2015

@author: ph1jb
'''
from copy import deepcopy
from csv import DictReader, DictWriter
import sys

import configurations


class CsvHandler(object):

    def __init__(self, fn0, fn1):
        self.t0 = self.csv_read(fn0)
        self.t1 = self.csv_read(fn1)

    def csv_read(self, pathname):
        '''Read csv file (excluding 1st row) into self.table.
        Populate self.fieldnames with fields from 1st row in order'''
        with open(pathname, 'r') as fh:
            dr = DictReader(fh)
            self.fieldnames = dr.fieldnames
            return [row for row in dr]

    def csv_write(self, table, pathname, fieldnames=[]):
        with open(pathname, 'w') as fh:
            self. csv_write_fh(table, fh, fieldnames=fieldnames)

    def csv_write_fh(self, table, fh, fieldnames=[]):
        dw = DictWriter(fh, fieldnames if fieldnames else self.fieldnames)
        dw.writeheader()
        dw.writerows(table)

    def csv_print(self, table, fieldnames=[]):
        self. csv_write_fh(table, sys.stdout, fieldnames=fieldnames)


class UpdateRegister(object):

    def __init__(self, ld0, ld1, k0, k1, status):
        d0 = self.ld2dd(ld0, k0, k1)
        d1 = self.ld2dd(ld1, k0, k1)
        d2 = self.update(d0, d1, status)
        self.ld2 = self.dd2ld(d2)

    def ld2dd(self, l0, k0, k1):
        '''Create a dict of rows from a table of rows.
        {(row[k0], row[k1]):row, ...}
        '''
        return {(row[k0], row[k1]): row for row in l0}

    def update(self, d0, d1, status):
        '''Update table d0 with table d1.
        d0 and d1 list of rows where a row is a dictionary {colname:value, ...}
        d1 contains rows with Status='D'. Delete these rows from d0. 
        '''
        d2 = deepcopy(d0)
        d2.update(d1)
        # Delete records with Status='D'
        return {k: v for (k, v) in d2.items() if v[status] != 'D'}

    def dd2ld(self, dd):
        return sorted(dd.values())


class Main(object):

    def __init__(self, fn0, fn1):
        ch = CsvHandler(fn0, fn1)
        ud = UpdateRegister(ch.t0, ch.t1, status='Status')
        ch.csv_write(ud.ld2, fn0.replace('.csv', 'NEW.csv'))

if __name__ == '__main__':
    (fn0, fn1) = sys.argv[1:3]
    m = Main(fn0, fn1)
    print('Done')
