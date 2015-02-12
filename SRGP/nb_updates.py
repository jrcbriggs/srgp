#!/usr/bin/python

'''
Created on 4 Feb 2015

@author: julian
'''
from collections import OrderedDict as OD
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
        Populate self.nb_fieldnames with fields from 1st row in order'''
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


class NbUpdates(object):

    def __init__(self, t0, t1, nbkey, fieldmap, fieldnames_mods):
        self.t0 = t0
        self.t1 = t1
        self.nbkey = nbkey
        self.d0 = self.table2dict(self.t0, nbkey)
        self.d1 = self.table2dict(self.t1, nbkey)
        self.fieldmap = fieldmap
        self.nb_fieldnames = tuple(sorted(self.fieldmap.keys()))
        self.fieldnames_mods = fieldnames_mods
        self.mods = []

    @staticmethod
    def invert_fieldmap(fm):
        fm_new = OD()
        for (k, v) in fm.items():
            fm_new[v] = k
        del fm_new[None]
        return fm_new

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

    def find_mods(self):
        '''Return list of modified rows.
        When checking for mods, ignore fields in the omits lists
        Ie rows in t1 but not in t0
        Iterate over nb keys in both old and new dicts.
        '''
        mods = []
        for k in sorted(set(self.d0.keys()) & set(self.d1.keys())):
            row_old = self.d0[k]
            row_new = self.d1[k]
            for f in self.nb_fieldnames:
                if row_old[f] != row_new[f]:
                    update = {
                        'CIVICRM_ID': row_new['civicrm_id'],
                        'FIRST_NAME': row_new['first_name'],
                        'LAST_NAME': row_new['last_name'],
                        'UPDATE': f,
                        'OLD_VALUE': row_old[f],
                        'NEW_VALUE': row_new[f], }
                    row_new.update(update)
                    mods.append(row_new)
                    self.mods.append(update)
                    print(k, row_old['civicrm_id'], row_old['first_name'],
                          row_old['last_name'], ':', f, row_old[f], row_new[f])
                    break
        return mods

if __name__ == '__main__':
    #     civi = '/home/julian/SRGP/civi/'
    #     stem = civi + 'test/nationbuilder-people-export-'
    #     fn0 = stem + '29-2015-02-05.csv'
    #     fn1 = stem + '31-2015-02-07.csv'
    (fn0, fn1) = sys.argv[1:3]
    nbkey = 'nationbuilder_id'
    ch = CsvHandler(fn0, fn1)
    config = configurations.config_members
    fieldmap = NbUpdates.invert_fieldmap(config['fieldmap'])
    omits = ['expires_on', 'membership_status', 'membership_type',
             #              'mobile_number', 'phone_number',
             'precinct_name', 'started_at', 'tag_list', ]
    fieldnames_mods = [
                       'CIVICRM_ID', 
                       'FIRST_NAME',
                       'LAST_NAME',
                       'UPDATE',
                       'OLD_VALUE',
                       'NEW_VALUE',
                       ]
    for omit in omits:
        del fieldmap[omit]
    nu = NbUpdates(ch.t0, ch.t1, nbkey, fieldmap, fieldnames_mods)
    new = nu.new()
    ch.csv_write(new, fn1.replace('.csv', 'NEW.csv'))
    mods = nu.find_mods()
    ch.fieldnames.insert(0, 'NEW_VALUE')
    ch.fieldnames.insert(0, 'OLD_VALUE')
    ch.fieldnames.insert(0, 'UPDATE')
    ch.fieldnames.insert(0, 'LAST_NAME')
    ch.fieldnames.insert(0, 'FIRST_NAME')
    ch.fieldnames.insert(0, 'CIVICRM_ID')
    ch.csv_write(mods, fn1.replace('.csv', 'MODS.csv'))
    ch.csv_write(nu.mods, fn1.replace('.csv', 'MODS2.csv'), fieldnames=fieldnames_mods)
    print('Done')
