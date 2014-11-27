#!/usr/bin/python
'''
Created on 1 Nov 2014

@author: julian
'''
from collections import OrderedDict
from csv import DictReader, DictWriter
from datetime import datetime as dt
from importlib import import_module
from sys import stdout
import sys


# from xlrd import xlsx
class ConfigHandler(object):
    '''Derive fields from the config dict:
    fieldnames: for reading original csv
    fieldnames_new: fieldnames for writing new csv 
    fieldmap_new: ordered dict mapping selected original fieldnames to fieldnames_new
    tagfields: fieldnames from original csv to add to tag_list
    '''
    def __init__(self,
                 address_fields,
                 date_fields,
                 doa_field,
                 fieldmap,
                 **kwargs
                 ):
        self.fieldnames = tuple(fieldmap.keys())  # for reading csv
        
        # Derive things from fieldmap
        self.tagfields = ()
        self.fieldmap_new = OrderedDict()  # for writing csv (append new fields later)
        for k, v in fieldmap.items():
            if v == 'tag_list':
                self.tagfields += (k,)  # Put original fieldname on taglist
            elif(v is None):
                pass
            else:
                self.fieldmap_new[k] = v
                
        # Update properties
        self.fieldnames_new = tuple(self.fieldmap_new.values())
        self.fieldnames_new += ('tag_list',)
        self.fieldmap_new.update({'tag_list':'tag_list', })
        
        # Populate config_new
        self.config_new = {
                         'address_fields':address_fields,
                         'date_fields': date_fields,
                         'doa_field':doa_field,
                         'fieldnames':self.fieldnames,
                         'tagfields':self.tagfields,
                         }

class Dict2Dict(object):
    '''Map an old dict to a new dict: rename keys, values unchanged'''
    def __init__(self, data, fieldmap):
        self.data_new = self.mapdata(data, fieldmap)
    
    def maprow(self, row, fieldmap):
        return {key_new:row[key_old] for key_old, key_new in fieldmap.items()}
    
    def mapdata(self, data, fieldmap):
        return [self.maprow(row, fieldmap) for row in data]    

class FileHandler(object):
    
    def config_load(self, modulename):
        mod = import_module(modulename)
        return mod.config
    
    def csv_read(self, pathname, fieldnames_expected, skip_lines=0):
        '''Read csv file (excluding 1st row) into self.table.
        Populate self.fieldnames with fields from 1st row in order'''
        with open(pathname, 'r') as fh:
            return self.csv_read_fh(fh, fieldnames_expected, skip_lines)

    def csv_read_fh(self, fh, fieldnames_expected, skip_lines=0):
        '''Read csv file (excluding 1st row) into self.table.
        Populate self.fieldnames with fields from 1st row in order'''
        for i in range(skip_lines):
            next(fh)
        dr = DictReader(fh)
        table = [row for row in dr]
        fieldnames = tuple(dr.fieldnames)           
        if fieldnames != fieldnames_expected:
            fields_odd = self.find_mismatch(fieldnames, fieldnames_expected)
            raise ValueError('Unexpected fieldnames:\n' + ','.join(fieldnames)
                             + '\n' + ','.join(fieldnames_expected)
                             + '\n' + 'mismatch:' + ','.join(fields_odd))
        return (table, fieldnames)
    
    def find_mismatch(self, set0, set1):
        '''find the difference of 2 iterables (lists, sets, tuples), return as sorted list'''
        return sorted(list(set(set0).difference(set(set1))))

#     def xls_read(self, pathname, fieldnames_expected):
#         '''Read xls file (excluding 1st row) into self.table.
#         Populate self.fieldnames with fields from 1st row in order'''
#         with xlsx.
#         with open(pathname, 'r') as fh:
#             dr = DictReader(fh)
#             table = [row for row in dr]
#             fieldnames = tuple(dr.fieldnames)           
#             if fieldnames != fieldnames_expected:
#                 raise ValueError('Unexpected fieldnames:\n' + ','.join(fieldnames)
#                                  + '\n' + ','.join(fieldnames_expected))
#             return (table, fieldnames)

    def csv_print(self, table, fieldnames2):
        self.csv_write_fh(table, stdout, fieldnames2)
        
    def csv_write(self, table, pathname, fieldnames2):
        with open(pathname, 'w') as fh:
            self. csv_write_fh(table, fh, fieldnames2)

    def csv_write_fh(self, table, fh, fieldnames2):
            dw = DictWriter(fh, fieldnames2)   
            dw.writeheader()
            dw.writerows(table)          

class RegisterFixer(object):
    date_format_electoral_roll = '%d/%m/%Y'
    date_format_nb = '%m/%d/%Y'
   
    def __init__(self,
                address_fields=(),
                date_fields=(),
                doa_field='',
                fieldnames={},
                fieldmap={},
                regexes={},
                table=(),
                tagfields=None,
                tagtail=None
                 ):
        self.address_fields = address_fields
        self.date_fields = date_fields
        self.doa_field = doa_field
        self.fieldnames = fieldnames
        self.regexes = regexes
        self.table = table
        self.tagfields = tagfields
        self.tagtail = tagtail

    def clean_value(self, value):
        return value.replace(',', ' ').strip()

    def clean_row(self, row):
        '''Clean all the values (but not the keys) in a row'''
        for k, v in row.items():
            row[k] = self.clean_value(v)
            
    def doa2dob(self, doa):
        '''Convert date of attainment (ie reach 18years old) to DoB. 
            Use after converting to NB date format.
            yoa: year of attainment, yob: year of birth'''
        (month, day, yoa) = doa.split('/')
        yob = str(int(yoa) - 18)
        return '/'.join([month, day, yob])

    def fix_addresses(self, row, address_fields):
        '''Inplace update row. Given, say, 7 address fields fill thus:
        put country_code (GB) in 7th
        move postcode (S10 1ST) to 6th (and blank original postcode field)
        move city (Sheffield) to 5th (and blank original city field)
        Do fields in this order to avoid city clobbering postcode in long address.
        ''' 
        field_countrycode = address_fields[-1]
        field_postcode = address_fields[-2]
        field_city = address_fields[-3]
        row[field_countrycode] = 'GB'
        for fname in address_fields[-1:0:-1]:
            v = row[fname]
            if self.ispostcode(v):
                row[fname] = ''
                row[field_postcode] = v
            elif self.iscity(v):
                row[fname] = ''
                row[field_city] = v
                
    def fix_date(self, date):
        '''electoral roll date format: 31/12/2014
        NB date format: 11-16-2009
        if date is just whitespace return empty string'''
        date = date.strip()
        if date:
            return dt.strftime(dt.strptime(date, self.date_format_electoral_roll), self.date_format_nb)
        else:
            return date            
           
    def fix_dates(self, row):
        '''Update date fields in-place'''
        for field in self.date_fields:
            row[field] = self.fix_date(row[field])

    def fix_doa(self, row, doa_fieldname):
        '''Update Date of Attainment field in-place'''
        if doa_fieldname in row and row[doa_fieldname]:
            row[doa_fieldname] = self.doa2dob(row[doa_fieldname])
    
    def fix_table(self):
        '''in-place update row'''
        for row in self.table:
            self.clean_row(row)
            self.fix_dates(row)            
            self.fix_doa(row, self.doa_field)            
            self.fix_addresses(row, self.address_fields)            
            row.update(self.tags_create(row, self.tagfields, self.tagtail)) 
        return self.table
            
    def iscity(self, city):  # is value a city
        return self.regexes['city_regex'].search(city)
        
    def iscounty (self, county) :  # is value a county
        return self.regexes['county_regex'].search(county)
    
    def ishouse(self, house)  :  # is value a house name
        return self.regexes['house_regex'].search(house)
    
    def ispostcode(self, postcode)  :  # is value a postcode
        return self.regexes['postcode_regex'].search(postcode)

    def isstreet (self, street)  :  # is value a street        
        return self.regexes['street_regex'].search(street)
 
    def tags_create(self, row, tagfields, tagtail):
        '''Assemble tag, append to @tags, create tag_list field.
        If tag field is blank then omit tag'''
        tags = []
        for tagfield in tagfields:
            value = str(row[tagfield]).strip()
            if value:
                tagfield.replace(' ', '')
#                 tag = '_'.join([value, tagfield, tagtail])
                tag = '_'.join([tagfield, value])
                tags.append(tag)
        taglist_str = ','.join(tags)
        return {'tag_list':taglist_str, }
