#!/usr/bin/python

'''
Created on 4 Feb 2015

@author: julian
'''
from csv import DictReader, DictWriter
import sys


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

    def csv_write(self, table, pathname):
        with open(pathname, 'w') as fh:
            self. csv_write_fh(table, fh)

    def csv_write_fh(self, table, fh):
        dw = DictWriter(fh, self.fieldnames)
        dw.writeheader()
        dw.writerows(table)


class NbUpdates(object):

    def __init__(self, t0, t1, nbkey):
        self.t0 = t0
        self.t1 = t1
        self.nbkey = nbkey
        self.d0 = self.table2dict(self.t0, nbkey)
        self.d1 = self.table2dict(self.t1, nbkey)

    @staticmethod
    def table2dict(table, nbkey):
        '''Takes table of rows (dicts). Returns dict of dicts.
        Key of outer dict is value row[nbkey]
        Value of outer dict is row'''
        return {int(row[nbkey]): row for row in table}

    def new(self):
        '''Return list of new rows.
        Ie rows in t1 but not in t0'''
        k0 = set(self.d0.keys())
        k1 = set(self.d1.keys())
        k_new = sorted(k1 - k0)
        return [self.d1[k] for k in k_new]

    def mods(self):
        '''Return list of modified rows.
        Ie rows in t1 but not in t0'''
        return [self.d1[k]
                for k in sorted(self.d0.keys())
                if k in self.d1 and (set(self.d0[k].items()) - set(self.d1[k].items()))]

if __name__ == '__main__':
    fn0 = '/home/julian/SRGP/civi/20150202/nationbuilder-people-export-members-25-2015-02-03.csv'
    fn1 = '/home/julian/SRGP/civi/20150204/nationbuilder-people-export-members-28-2015-02-04.csv'
    nbkey = 'nationbuilder_id'
    ch = CsvHandler(fn0, fn1)
    nu = NbUpdates(ch.t0, ch.t1, nbkey)
    new = nu.new()
    ch.csv_write(new, fn1.replace('.csv', 'NEW.csv'))
    mods = nu.mods()
    ch.csv_write(mods, fn1.replace('.csv', 'MODS.csv'))
    print('Done')
