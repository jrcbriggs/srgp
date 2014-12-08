#!/usr/bin/python3
'''
Created on 1 Nov 2014

@author: julian
'''
from collections import OrderedDict
from csv import DictReader, DictWriter
from datetime import datetime as dt
from importlib import import_module
from os import getenv, path
from re import compile, IGNORECASE
from re import search
from sys import argv
from sys import stdout
import sys

from configurations import config_members, config_register, \
    config_search, config_officers, config_supporters, \
    config_volunteers
from requests import status_codes

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
                 date_format,
                 doa_fields,
                 fieldmap,
                 fields_extra,
                 fields_flip,
                 **kwargs
                 ):
        self.fieldnames = tuple(fieldmap.keys())  # for reading csv
        self.fields_extra = fields_extra
        
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
        self.fieldmap_new.update(fields_extra)
        self.fieldmap_new.update({'tag_list':'tag_list', })
        self.fieldnames_new = tuple(self.fieldmap_new.values())
        
        # Populate params
        self.params = {
                         'address_fields':address_fields,
                         'date_fields': date_fields,
                         'date_format': date_format,
                         'doa_fields':doa_fields,
                         'fieldnames':self.fieldnames,
                         'fields_extra':self.fields_extra,
                         'fields_flip':fields_flip,
                         'tagfields':self.tagfields,
                         }

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
        if len(fieldnames) == len(fieldnames_expected):         
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

class CsvFixer(object):
    def __init__(self, csv_filename, config):
        basename = path.basename(csv_filename).replace('.csv', '')
        filehandler = FileHandler()        
        
        ch = ConfigHandler(**config)
        
        # Read csv file
        skip_lines = config.get('skip_lines', 0)
        (table, unused) = filehandler.csv_read(csv_filename, ch.fieldnames, skip_lines)

        # Fix table
        vh = TableFixer(table=table, tagtail='tagtail', **ch.params)
        table_fixed = vh.fix_table()

        # Create new table
        d2d = TableMapper(table_fixed, ch.fieldmap_new)
        table_new = d2d.data_new
                
        # Write
        self.csv_filename_new = csv_filename.replace('.csv', 'NB.csv')
        filehandler.csv_write(table_new, self.csv_filename_new, ch.fieldnames_new)
#         filehandler.csv_print(table_new, fieldnames_new)

class TableFixer(object):
    date_format_nb = '%m/%d/%Y'
    regexes = {
            'city_regex' : compile('^(Rotherham|Sheffield)$', IGNORECASE),
            'county_regex' : compile('^South Yorks$', IGNORECASE),
            'house_regex' : compile('Barn|Building|College|Cottage|Farm|Hall|House|Lodge|Mansion|Mill|Residence', IGNORECASE),
            'postcode_regex' : compile('^S\d\d? \d\w\w$'),
            'street_regex' : compile(r'Approach|Avenue|Bank|Bridge|Close|Common|Court|Crescent|Croft|Dell|'
                        'Drive|Gardens|Gate|Glen|Green|Grove|Head|Hill|Lane|Mews|Parade|Park|'
                        'Place|Rise|Road|Row|Square|Street|Terrace|Town|Turn|View|Walk|Way|Wharf|'
                        'Backfields|Birkendale|Castlegate|Cracknell|Cross Smithfield|Kelham Island|Shalesmoor|Summerfield|Upperthorpe|Wicker|'  # Localities
                        'Foster|Millsands|Pinsent|Redgrave|'  # blocks
                        'Other Electors',
                        IGNORECASE),
               }
   
    def __init__(self,
                address_fields=(),
                date_fields=(),
                date_format='',
                doa_fields='',
                fieldnames={},
                fieldmap={},
                fields_extra={},
                fields_flip=(),
                table=(),
                tagfields=None,
                tagtail=None
                 ):
        self.address_fields = address_fields
        self.date_fields = date_fields
        self.date_format = date_format
        self.doa_fields = doa_fields
        self.fieldnames = fieldnames
        self.fields_extra = fields_extra
        self.fields_flip = fields_flip
        self.table = table
        self.tagfields = tagfields
        self.tagtail = tagtail

    def extra_fields(self, row, fields_extra):
        for k, v in fields_extra.items():
            if k == 'is_deceased':
                row[k] = self.isdeceased(row)  # Set is_deceased flag
            elif k == 'is_supporter':
                row[k] = self.ismember(row) # Set is_supporter flag if a member
            elif k == 'is_volunteer':
                row[k] = True  # Set is_volunteer flag on all rows in the Volunteers csv
            elif k == 'is_voter':
                row[k] = self.isvoter(row)  # Set  flag
            elif k == 'party':
                row[k] = 'G'
            elif k == 'party_member':
                row[k] = self.ismember(row)  # Set is_member flag
            elif k == 'status':
                row[k] = 'active'  # Status must be either 'active', 'grace period', 'expired', or 'canceled'
            elif k == 'support_level':
                row[k] = 1 if self.ismember(row) else ''  # assume
            else:
                row[k] = v

  
    def flip_fields(self, row, fieldnames):
        for fn in fieldnames:
            row[fn] = not row[fn]
            
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
        
        field_countrycode = address_fields.get('country_code', None)
        if field_countrycode:
            row[field_countrycode] = 'GB'
            
        field_postcode = address_fields.get('zip', None)
        if field_postcode:
            self.fix_postcode(row, address_fields, field_postcode)
            
        field_city = address_fields.get('city', None)
        if field_city:
            self.fix_city(row, address_fields, field_city)
        
    def fix_city(self, row, address_fields, field_city):
        for fieldname in address_fields.values():
            v = row[fieldname]
            if self.iscity(v):
                row[fieldname] = ''
                row[field_city] = v
                
#     def fix_addresses_helper(self, row, ):
    def fix_date(self, date):
        '''electoral roll date format: 31/12/2014
        NB date format: 11-16-2009
        if date is just whitespace return empty string'''
        date = date.strip()
        if date:
            return dt.strftime(dt.strptime(date, self.date_format), self.date_format_nb)
        else:
            return date            
           
    def fix_dates(self, row):
        '''Update date fields in-place'''
        for field in self.date_fields:
            row[field] = self.fix_date(row[field])

    def fix_deceased(self, row):
        '''members only: append is_deceased column and populate'''
        row['is_deceased'] = self.isdeceased(row)

    def fix_doa(self, row, doa_fields):
        '''Update Date of Attainment field in-place'''
        for doa_field in doa_fields:
            row[doa_field] = self.doa2dob(row[doa_field])
    
    def fix_local_party(self, row):
        '''members only: overwrite "Sheffield & Rotherham Green Party" with "G" '''
        field = 'Local party'
        if field in row:
            row[field] = 'G'    

    def fix_postcode(self, row, address_fields, field_postcode):
        for fieldname in address_fields.values():
            v = row[fieldname]
            if self.ispostcode(v):
                row[fieldname] = ''
                row[field_postcode] = v
                
    def fix_table(self):
        '''in-place update row'''
        for row in self.table:
            self.clean_row(row)
            self.fix_dates(row)            
            self.fix_doa(row, self.doa_fields)            
            self.fix_addresses(row, self.address_fields)            
            self.fix_local_party(row)   
            self.extra_fields(row, self.fields_extra)         
            self.flip_fields(row, self.fields_flip)         
            row.update(self.tags_create(row, self.tagfields, self.tagtail)) 
        return self.table
            
    def get_status(self, row):
        statusmap={'Cancelled': 'expired', 'Current': 'active', 'Deceased': 'expired', 'Expired': 'expired', 'New': 'active'}
        status = row['Status']
        return statusmap[status]
    
    def iscity(self, city):  # is value a city
        return self.regexes['city_regex'].search(city)
        
    def iscounty (self, county) :  # is value a county
        return self.regexes['county_regex'].search(county)
    
    def isdeceased(self, row): 
        return row.get('Status', None) == 'Deceased'
    
    def ishouse(self, house)  :  # is value a house name
        return self.regexes['house_regex'].search(house)
    
    def ismember(self, row):
        return row.get('Status', None) in ('Current', 'New')
    
    def ispostcode(self, postcode)  :  # is value a postcode
        return self.regexes['postcode_regex'].search(postcode)

    def isstreet (self, street)  :  # is value a street        
        return self.regexes['street_regex'].search(street)
 
    def isvoter(self, row)  :
        return row.get('Status', None) == 'E'
    
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

class TableMapper(object):
    '''Map an old dict to a new dict: rename keys, values unchanged'''
    def __init__(self, data, fieldmap):
        self.data_new = self.mapdata(data, fieldmap)
    
    def maprow(self, row, fieldmap):
        return {key_new:row[key_old] for key_old, key_new in fieldmap.items()}
    
    def mapdata(self, data, fieldmap):
        return [self.maprow(row, fieldmap) for row in data]    
    
if __name__ == '__main__':
    config = None
    for csv_filename in argv[1:]: #skip scriptname in argv[0] 

        if search('register', csv_filename):
            config = config_register
        elif search('Members', csv_filename,):
            config = config_members
        elif search('Officers', csv_filename,):
            config = config_officers
        elif search('Supporters', csv_filename,):
            config = config_supporters
        elif search('Volunteers', csv_filename,):
            config = config_volunteers
        elif search('Search', csv_filename,):
            config = config_search
        elif search('canvass', csv_filename):
            pass  # config= config_canvass 

        CsvFixer = CsvFixer(csv_filename, config)
        print (CsvFixer.csv_filename_new)
