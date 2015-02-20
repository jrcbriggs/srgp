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


class NbUpdates(object):

    def __init__(self, t0, t1, nbkey, fieldmap):
        self.d0 = self.table2dict(t0, nbkey)
        self.d1 = self.table2dict(t1, nbkey)
<<<<<<< HEAD
        self.nb_fieldnames = tuple(sorted(fieldmap.keys()))
=======
        self.fieldmap = fieldmap
        self.fieldnames = tuple(sorted(self.fieldmap.keys()))
>>>>>>> 3266fcdcc9e3d2010ef31d2df14c2e0601130924

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
        Ie rows in CSV1 but not in CSV0'''
        k0 = set(self.d0.keys())
        k1 = set(self.d1.keys())
        k_new = sorted(k1 - k0)
        return [self.d1[k] for k in k_new]

    def find_mods(self):
        '''Return list of modified fields:
        {NB_ID,CIVICRM_ID,FIRST_NAME,LAST_NAME,FIELDNAME,OLD_VALUE,NEW_VALUE,}
        Where record exists (smae nb_key) in old and new CSV
        '''
        mods = []
        for k in sorted(set(self.d0.keys()) & set(self.d1.keys())):
            row_old = self.d0[k]
            row_new = self.d1[k]
            for f in self.fieldnames:
                if row_old[f] != row_new[f]:
                    mods.append({
                        'NB_ID': row_new['nationbuilder_id'],
                        'CIVICRM_ID': row_new['civicrm_id'],
                        'FIRST_NAME': row_new['first_name'],
                        'LAST_NAME': row_new['last_name'],
                        'FIELDNAME': f,
                        'OLD_VALUE': row_old[f],
<<<<<<< HEAD
                        'NEW_VALUE': row_new[f], }
                    row_new.update(update)
                    mods.append(row_new)
                    break
=======
                        'NEW_VALUE': row_new[f], })
>>>>>>> 3266fcdcc9e3d2010ef31d2df14c2e0601130924
        return mods


class Main(object):

    def __init__(self, fn0, fn1):
        nbkey = 'nationbuilder_id'
        ch = CsvHandler(fn0, fn1)
        config = configurations.config_members
        fieldmap = NbUpdates.invert_fieldmap(config['fieldmap'])
        omits = 'expires_on,membership_status,membership_type,mobile_number,phone_number,precinct_name,started_at,tag_list'.split(
            ',')
        for omit in omits:
            del fieldmap[omit]
        nu = NbUpdates(ch.t0, ch.t1, nbkey, fieldmap)
        new = nu.new()
        ch.csv_write(new, fn1.replace('.csv', 'NEW.csv'))
        mods = nu.find_mods()
        fieldnames_mods = 'NB_ID,CIVICRM_ID,FIRST_NAME,LAST_NAME,FIELDNAME,OLD_VALUE,NEW_VALUE'.split(',')
        ch.csv_write(mods, fn1.replace('.csv', 'MODS.csv'), fieldnames=fieldnames_mods)
        ch.csv_print(mods, fieldnames=fieldnames_mods)

if __name__ == '__main__':
    (fn0, fn1) = sys.argv[1:3]
<<<<<<< HEAD
    nbkey = 'nationbuilder_id'
    ch = CsvHandler(fn0, fn1)
    config = configurations.config_members
    fieldmap = NbUpdates.invert_fieldmap(config['fieldmap'])
    omits = ['expires_on', 'membership_status', 'membership_type',
             #              'mobile_number', 'phone_number',
             'precinct_name', 'started_at', 'tag_list', ]
    fieldnames_mods = 'CIVICRM_ID FIRST_NAME LAST_NAME UPDATE OLD_VALUE NEW_VALUE'.split()
    for omit in omits:
        del fieldmap[omit]
    fieldnames_mods0 = ch.fieldnames + fieldnames_mods
    nu = NbUpdates(ch.t0, ch.t1, nbkey, fieldmap, fieldnames_mods)
    new = nu.new()
    ch.csv_write(new, fn1.replace('.csv', 'NEW.csv'))
    mods = nu.find_mods()

    ch.csv_write(
        mods, fn1.replace('.csv', 'MODS.csv'), fieldnames=fieldnames_mods)
    ch.csv_write(
        nu.mods, fn1.replace('.csv', 'MODS2.csv'), fieldnames=fieldnames_mods)
=======
    m = Main(fn0, fn1)
>>>>>>> 3266fcdcc9e3d2010ef31d2df14c2e0601130924
    print('Done')
