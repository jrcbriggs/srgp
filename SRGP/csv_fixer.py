#!/usr/bin/python3
'''
Created on 1 Nov 2014

@author: julian
'''
from collections import OrderedDict as OD
from csv import DictReader, DictWriter
from datetime import datetime as dt
import datetime
from importlib import import_module
from io import StringIO
import mmap
import os
from os.path import basename, splitext
from re import compile, IGNORECASE, sub
from re import search
from sys import argv
from sys import stdout
import xlrd

from configurations import config_members, config_register, \
    config_search, config_officers, config_supporters, \
    config_volunteers, canvassing, config_young_greens, config_search_add, config_search_mod, \
    config_nationbuilder, config_nationbuilderNB, regexes, \
    config_register_update, config_register_postal, config_textable, \
    config_support1_2


class ConfigHandler(object):

    '''Parse the config dict to extract input params to table fixer and csv fixer:
    fieldmap: ordered dict maps old to new fieldnames
    fieldnames: for reading original csv
    fieldnames_new: fieldnames for writing new csv
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
        # for writing csv (append new fields later)
        self.fieldmap_new = OD()
#         self.fieldmap_new.update(fields_extra)
        for k, v in fieldmap.items():
            if v == 'tag_list':
                self.tagfields += (k,)  # Put original fieldname on taglist
            elif(v is None):
                pass
            else:
                self.fieldmap_new[k] = v

        # Update properties
        self.fieldmap_new.update(fields_extra)
        self.fieldmap_new.update({'tag_list': 'tag_list', })
        self.fieldnames_new = tuple(self.fieldmap_new.values())

        # Populate params
        self.params = {
            'address_fields': address_fields,
            'date_fields': date_fields,
            'date_format': date_format,
            'doa_fields': doa_fields,
            'fieldnames': self.fieldnames,
            'fields_extra': self.fields_extra,
            'fields_flip': fields_flip,
            'tagfields': self.tagfields,
        }


class FileHandler(object):

    '''Handle reading and writing files, including the config file which is loaded as a Python module.
    '''

    def config_load(self, modulename):
        mods = import_module(modulename)
        return mods.config

    def csv_read(self, pathname, fieldnames_expected, skip_lines=0):
        '''Read csv file (excluding 1st row) into self.table.
        Populate self.fieldnames with fields from 1st row in order'''
        with open(pathname, 'r', encoding='utf-8', errors='ignore') as fh:
            return self.csv_read_fh(fh, fieldnames_expected, skip_lines)

    def csv_read_fh(self, fh, fieldnames_expected, skip_lines=0):
        '''Read csv file (excluding 1st row) into self.table.
        Populate self.fieldnames with fields from 1st row in order'''
        for unused in range(skip_lines):
            next(fh)
        dr = DictReader(fh)
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
                                 + '\nmismatch:' + ','.join(sorted(fields_odd)))
        return (table, fieldnames)

    def find_mismatch(self, set0, set1):
        '''return difference of 2 iterables (lists, sets, tuples)
        as sorted list'''
        return sorted(list(set(set0).difference(set(set1))))

    def csv_print(self, table, fieldnames2):
        self.csv_write_fh(table, stdout, fieldnames2)

    def csv_write(self, table, pathname, fieldnames2):
        with open(pathname, 'w') as fh:
            self. csv_write_fh(table, fh, fieldnames2)

    def csv_write_fh(self, table, fh, fieldnames2):
        dw = DictWriter(fh, fieldnames2)
        dw.writeheader()
        dw.writerows(table)

    def xlsx_read(self, pathname, fieldnames_expected, skip_lines=0, sheet_index=1):
        with open(pathname, 'r') as fh:

            data = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
            book = xlrd.open_workbook(file_contents=data)
            sheet = book.sheet_by_index(sheet_index)

            def cell_value(i, j):
                '''Convert xls date from days since ~1900 to '31/12/2014' '''
                cell = sheet.cell(i, j)
                value = cell.value
                if cell.ctype == 3 and value:  # XL_CELL_DATE
                    return datetime.datetime(*xlrd.xldate_as_tuple(value, book.datemode)).strftime('%d/%m/%Y')
                else:
                    return str(value).replace(',', '')

            csv = (','.join([cell_value(i, j) for j in range(sheet.ncols)])
                   for i in range(sheet.nrows))
            return self.csv_read_fh(csv, fieldnames_expected, skip_lines)


class CsvWardUpdate(object):

    '''The top level class.
    Read csv data file into a table
    Fix the data in table
    Create new table: with NB table column headings
    Write the table to a new csv file for import to NB.
    '''

    def __init__(self, csv_register, config, filereader):
        ch = ConfigHandler(**config)

        # Read csv data file into a table
        skip_lines = config.get('skip_lines', 0)
        (table, unused) = filereader(
            csv_register, ch.fieldnames, skip_lines)

        # Fix the data in table
        (csv_basename, _) = splitext(basename(csv_register))
        vh = TableWardUpdate(table=table, csv_basename=csv_basename, **ch.params)
        table_fixed = None
        if 'nationbuilder' in csv_basename:
            table_fixed = vh.fix_table_street_address()
        else:
            table_fixed = vh.fix_table()

        # Create new table: with NB table column headings
        d2d = TableMapper(table_fixed, ch.fieldmap_new)
        table_new = d2d.data_new

        # Write the table to a new csv file for import to NB.
        self.csv_filename_new = csv_register.replace(
            '.csv', 'NB.csv').replace('.xlsx', 'NB.csv')
        filehandler.csv_write(
            table_new, self.csv_filename_new, ch.fieldnames_new)
#         filehandler.csv_print(table_new, fieldnames_new)


class TableWardUpdate(object):

    '''
    Fix the data in the table, top level method is: fix_table
    clean_rows (trim leading and training white space
    fix_dates: from dd/mm/yyyy etc. to mm/dd/yyyy
    fix_doa: change date of attainment (18yo can vote) to DoB
    fix_addresses_city_postcode_countrycode: move city, postcode and country to names fields
    fix_local_party: change 'Sheffield & Rotherham Green Party' to G
    extra_fields: append and populate extra fields
    flip_fields: reverse the (boolean) sense of field, eg do_not_email to email_opt_in
    row.update: append tags column
    skip_list: skip matching rows (eg Organisation row in civi Search csv)
    '''
    date_format_nb = '%m/%d/%Y'

    # Skip Rows where (civi) contact type is Organization (not Individual)
    skip_dict = {'Contact Type': 'Organization'}

    @staticmethod
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
                 csv_basename=None
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
        self.csv_basename = csv_basename

    def extra_fields(self, row, fields_extra):
        for k, v in fields_extra.items():
            if k == 'is_deceased':
                row[k] = self.isdeceased(row)  # Set is_deceased flag
            elif k == 'is_supporter':
                # Set is_supporter extra field exists (change from if a member.
                # Julian 23-jan-2015)
                row[k] = True  # self.is_party_member(row)
            elif k == 'is_volunteer':
                # Set is_volunteer flag on all rows in the Volunteers csv
                row[k] = True
            elif k == 'is_voter':
                row[k] = self.isvoter(row)  # Set  flag
            # volunteers have extra field party, set it to G
            elif k == 'party':
                row[k] = 'G'
            elif k == 'party_member':
                row[k] = self.is_party_member(row)  # Set is_member flag
            elif k == 'party_member_true':
                row[k] = True  # Set is_member flag
            elif k == 'support_level':
                # assume strong support from all civi:
                # (members, officers, supporters, volunteers but not search
                row[k] = 1
            elif k == 'Young Green':
                row[k] = k
            elif k == 'knockedUp':
                row[k] = ''
            elif k == 'phoned':
                row[k] = ''
            elif k == 'voted':
                row[k] = ''
            elif k == 'street_name':
                row[k] = sub('^[\d-]+\w?\s+', '', row['registered_address1'])  # split()[1:]
            else:
                row[k] = v

    def flip_fields(self, row, fieldnames):
        for fn in fieldnames:
            if row[fn] in (0, '0', '', 'False', False):
                row[fn] = False
            row[fn] = not row[fn]

    def clean_value(self, value):
        return value.replace(',', ';').strip()

    def clean_row(self, row):
        '''Clean all the values (but not the keys) in a row'''
        for k, v in row.items():
            row[k] = self.clean_value(v)

    def doa2dob(self, doa):
        '''Convert date of attainment (ie reach 18years old) to DoB.
            Use after converting to NB date format.
            yoa: year of attainment, yob: year of birth'''
        if doa:
            (month, day, yoa) = doa.split('/')
            yob = str(int(yoa) - 18)
            return '/'.join([month, day, yob])
        else:
            return doa

    def fix_addresses_city_postcode_countrycode(self, row, address_fields):
        '''Update row inplace. Given, say, 7 address fields fill thus:
        put country_code (GB) in country_code field
        move postcode (S10 1ST) to postcode field
        move city (Sheffield) to city field
        Do in this order to avoid city clobbering postcode in long address.
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

#     def fix_address_street0(self, row, address_fields):
#         '''Merge fields address1-4 into  address1'''
#         if self.csv_basename.startswith('CentralConstituencyRegister'):
# af = list(address_fields.values())[0:5]  # address1-4
#             row[af[0]] = ' '.join([row[af[0]], row[af[1]], row[af[2]], row[af[3]]])
#             for i in range(1, 4):
#                 row[af[i]] = ''

    def fix_address_street(self, row, address_fields):
        '''Move street address to address1:
        1. Copy address values from row into a list.
        2. Find street address.
        3. Pop it (ie remove from list)
        4. Prepend it to the list
        5. Copy array elements back into address fields in row.
        '''
        afns = list(address_fields.values())[
            :-3]  # omit rightmost 3 fields (city, zip, country)
        if afns:
            alist = [row[afn] for afn in afns]
            for i in range(len(alist) - 1, -1, -1):
                if self.isstreet(alist[i]) and not self.islocality(alist[i]):
                    v = alist.pop(i)
                    alist.insert(0, v)
                    break
            else:
                if alist[0]:
                    print('Street not found {}'.format(alist))
            for i in range(len(alist)):
                row[afns[i]] = alist[i]

    def fix_address_street0(self, row, address_fields):
        '''Merge and shift address fields:
        Address2,3,4 => address1
        Address1 => address2
        Address5 => address3'''
        if self.csv_basename.startswith('CentralConstituencyRegister2015') or (self.csv_basename.find('WardRegister2015') > -1):
            (row['Address 1'], row['Address 2'], row['Address 3'],) = (row[
                'Address 2'] + ' ' + row['Address 3'] + ' ' + row['Address 4'], row['Address 1'], row['Address 5'])

    def fix_address_street1(self, row, address_fields):
        '''Move Street address to Corres Addr 5 (which maps to NB address1)
        See config fieldmap: Corres Addr 1 maps to address2 etc.'''
        if self.csv_basename.startswith('CentralConstituencyRegisterPV2015'):
            field_address1 = address_fields.get('address1', None)
            for fn in ['Corres Address Line 5', 'Corres Address Line 4', 'Corres Address Line 3', 'Corres Address Line 2', 'Corres Address Line 1', ]:
                if self.isstreet(row[fn]):
                    tmp = row[fn]
                    row[fn] = ''
                    row[field_address1] = tmp
                    break

    def fix_address_street_postal(self, row, address_fields):
        '''Move Street address to Qualifying_Address_5 (which maps to NB address1)
        See config fieldmap: Qualifying_Address_1 maps to address2 etc.'''
        if self.csv_basename.startswith('Crookes_Ecclesall_Postal'):
#             print('fix_address_street_postal')
            field_address1 = address_fields.get('registered_address1', None)
            field_address2 = address_fields.get('registered_address2', None)
            field_address3 = address_fields.get('registered_address3', None)
            row[field_address1] = row['Qualifying_Address_1'] + ' ' + row['Qualifying_Address_2'] + ' ' + row['Qualifying_Address_3']
            row[field_address2] = ''
            row[field_address3] = ''


    def fix_city(self, row, address_fields, field_city):
        for fieldname in address_fields.values():
            v = row[fieldname]
            if self.iscity(v):
                row[fieldname] = ''
                row[field_city] = v

    def fix_contact_name(self, row):
        '''civi Contact name is 'last_name, first name'
        change this to 'first_name last_name'
        used by: Officers, Supporters, Volunteers
        Members have: 'Contact Name' and: 'First Name', 'Middle Name', 'Last Name'
        '''
        if 'Contact Name' in row:
            contact_name = row['Contact Name']
            names = contact_name.split()
            names.reverse()
            row['Contact Name'] = ' '.join(names)

    def fix_date(self, date):
        '''electoral roll date format: 31/12/2014
        NB date format: 11-16-2009
        if date is just whitespace return empty string'''
        date = date.strip()
        if date:
            return dt.strftime(dt.strptime(date, self.date_format),
                               self.date_format_nb)
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
        '''
        Members: set civi field: Local party=G
        Officers: set civi field: Party=G
        Supporters: set civi field: Local party=G
        Volunteers: not set here: extra_fields sets NB: party=G
        canvassing: not set here: no Party or Local Party field
        register: not set here: no Party or Local Party field
        '''
        for field in ('Local party', 'Party'):
            if field in row:
                row[field] = 'G'

    def fix_postcode(self, row, address_fields, field_postcode):
        for fieldname in address_fields.values():
            v = row[fieldname]
            if self.ispostcode(v):
                row[fieldname] = ''
                row[field_postcode] = v

    def fix_state(self, row):
        if 'registered_state' in row:
            row['registered_state'] = 'Sheffield'

    def fix_status(self, row):
        if 'Status' in row:
            statusmap = {'Cancelled': 'canceled', 'Current': 'active',
                         'Deceased': 'expired', 'Expired': 'expired',
                         'New': 'active', 'Grace': 'grace period'}
            # needed to avoid updating Status in electoral register
            if row['Status'] in statusmap:
                row['Status'] = statusmap[row['Status']]

    def fix_table(self):
        '''in-place update row'''
        skip_list = []
        for row in self.table:
            self.clean_row(row)
            self.fix_contact_name(row)
            self.fix_dates(row)
            self.fix_doa(row, self.doa_fields)
            self.fix_addresses_city_postcode_countrycode(row, self.address_fields)
#             if self.csv_basename.startswith('CentralConstituencyRegister'):
#                 self.fix_address_street0(row, self.address_fields)
#             else:
#             self.fix_address_street(row, self.address_fields)
            self.fix_address_street0(row, self.address_fields)
            self.fix_address_street1(row, self.address_fields)
            self.fix_address_street_postal(row, self.address_fields)
            self.fix_local_party(row)
            # Must call before fix_status to identify is_deceased
            self.extra_fields(row, self.fields_extra)
            # Must call after extra_fields so extra_fields can identify
            # is_deceased
            self.fix_state(row)
            self.fix_status(row)
            self.flip_fields(row, self.fields_flip)
            self.merge_pd_eno(row)
            self.set_ward(row)
            tags = self.tags_create(row, self.tagfields, self.csv_basename)
            row.update(tags)
            skip_list += self.is_matching_row(row, self.skip_dict)
        for row in skip_list:
            self.table.remove(row)  # Remove list element by value
        return self.table

    def fix_table_street_address(self):
        '''Just fix the street address.
        in-place update row'''
        for row in self.table:
            self.fix_address_street(row, self.address_fields)
        return self.table

    def iscity(self, city):  # is value a city
        return regexes['city'].search(city)

    def iscounty(self, county):  # is value a county
        return regexes['county'].search(county)

    def isdeceased(self, row):
        return row.get('Status', None) == 'Deceased'

    def ishouse(self, value):  # is value a house name
        return regexes['house'].search(value)

    def islocality(self, value):  # is value a locality (eg Broomhall
        return regexes['locality'].match(value)

    def is_matching_row(self, row, skip_dict):
        return [row for (k, v) in skip_dict.items() if row.get(k, None) == v]

    def is_party_member(self, row):
        return row.get('Status', None) in ('Current', 'New', 'Grace', 'active')

    def ispostcode(self, postcode):  # is value a postcode
        return regexes['postcode'].search(postcode)

    def isstreet(self, value):  # is value a street
        return regexes['street'].search(value)

    def isvoter(self, row):
        return (row.get('Status', 'None') in 'AEM'  # register
                or
                'Electoral roll number' in row  # Canvassing
                )

    def merge_pd_eno(self, row):
        if ('PD_Letters' in row) and ('Published_ENo' in row):
            row['Published_ENo'] = row[
                'PD_Letters'] + str(row['Published_ENo'])
        if ('PD' in row) and ('ENO' in row):
            row['ENO'] = row['PD'] + str(row['ENO'])
        if 'Polling district' in row and 'Electoral roll number' in row:
            row['Electoral roll number'] = row[
                'Polling district'] + str(row['Electoral roll number'])
        if 'PD/ENO' in row:
            row['PD/ENO'] = row['PD/ENO'].replace('/', '')

    def set_ward(self, row):
        if 'PD' in row:
            pd = row['PD']
            ward = TableWardUpdate.pd2ward(pd)
            row['ward_name'] = ward
        if 'PD_Letters' in row:
            pd = row['PD_Letters']
            ward = TableWardUpdate.pd2ward(pd)
            row['ward_name'] = ward

    def tags_create(self, row, tagfields, csv_basename):
        '''Assemble tag, append to @tags, create tag_list field.
        If tag field is blank then omit tag'''
        tagdict = {
            'Postal Vote (last election)': 'PV',
            # strip field name so tag is just value (Postal or Proxy)
            'AV Type': '',
            '': '',
        }
        tags = []
        # Handle civi Vounteers actions
        if csv_basename.startswith('SRGP_Volunteers'):
            if 'Actions' in row:
                tags = [
                    'Volunteer_' + action for action in row['Actions'].split(';')]
                row['Actions'] = ''
        for tagfield in tagfields:
            value = str(row[tagfield]).strip()
            if value:
                tagfield.replace(' ', '')
                tagfield = tagdict.get(tagfield, tagfield)
                if tagfield:
                    tag = '{}={}'.format(tagfield, value)
                else:
                    tag = value
                tags.append(tag)
#         tags.append(csv_basename)
        taglist_str = ','.join(tags)[:255]  # truncate tags list to 255 chars
        return {'tag_list': taglist_str, }


class TableMapper(object):

    '''Map original table (row of dicts) to new table (row of dicts).
    Read original table and field mapper. Write new table with new field names.
    Values unchanged'''

    def __init__(self, data, fieldmap):
        self.data_new = self.mapdata(data, fieldmap)

    def maprow(self, row, fieldmap):
        return {key_new: row[key_old] for key_old, key_new in fieldmap.items()}

    def mapdata(self, data, fieldmap):
        return [self.maprow(row, fieldmap) for row in data]

if __name__ == '__main__':
    config = None
    for csv_filename in argv[1:]:  # skip scriptname in argv[0]
        # Find config varname to match csv filename
        if search('registerUpdate', csv_filename, IGNORECASE):
            config = config_register_update
        elif search('RegisterPV', csv_filename, IGNORECASE):
            config = config_register_postal
        elif search('CentralConsituencyPostal', csv_filename, IGNORECASE):
            config = config_register_postal
        elif search('CentralWardPostal', csv_filename, IGNORECASE):
            config = config_register_postal
        elif search('Crookes_Ecclesall_Postal', csv_filename, IGNORECASE):
            config = config_register_postal
        elif search('register', csv_filename, IGNORECASE):
            config = config_register
        elif search('SearchAdd', csv_filename, IGNORECASE):
            config = config_search_add
        elif search('SearchMod', csv_filename, IGNORECASE):
            config = config_search_mod
        elif search('textable', csv_filename, IGNORECASE):
            config = config_textable
        elif search('support1_2', csv_filename, IGNORECASE):
            config = config_support1_2
#         elif search('MembersNew', csv_filename,):
#             config = config_members_new
        elif search('Members', csv_filename, IGNORECASE):
            config = config_members
        elif search('Officers', csv_filename, IGNORECASE):
            config = config_officers
        elif search('Supporters', csv_filename, IGNORECASE):
            config = config_supporters
        elif search('Volunteers', csv_filename, IGNORECASE):
            config = config_volunteers
        elif search('YoungGreens', csv_filename, IGNORECASE):
            config = config_young_greens
        elif search('Search', csv_filename, IGNORECASE):
            config = config_search
        elif search('canvass', csv_filename, IGNORECASE):
            config = canvassing
        elif search('nationbuilder.+NB', csv_filename):
            config = config_nationbuilderNB
        elif search('nationbuilder', csv_filename):
            config = config_nationbuilder
        else:
            raise Exception(
                'Cannot find config for csv {}'.format(csv_filename))

        filehandler = FileHandler()
        reader = None
        if csv_filename.endswith('.csv'):
            reader = filehandler.csv_read
        elif csv_filename.endswith('.xls'):
            reader = filehandler.xlsx_read
        elif csv_filename.endswith('.xlsx'):
            reader = filehandler.xlsx_read
        xls_pw = os.getenv('XLS_PASSWORD')

        print('config_name: ', config['config_name'])
        csvfixer = CsvWardUpdate(csv_filename, config, reader)
        print(csvfixer.csv_filename_new)
