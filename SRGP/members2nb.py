#!/usr/bin/python
'''
Created on 1 Nov 2014

@author: julian
'''
from os import getenv, path
from re import search
from sys import argv
import sys

from address_regexes import regexes
from register_handler import FileHandler, TableFixer, TableMapper, ConfigHandler


class Main(object):
    def __init__(self, csv_filename, modulename):
        basename = path.basename(csv_filename).replace('.csv', '')
        filehandler = FileHandler()        
        
        # Load config
        config = filehandler.config_load(modulename)
        ch = ConfigHandler(**config)
        
        # Read csv file
        skip_lines = config.get('skip_lines', 0)
        tagtail = argv[3] if len(argv) > 3 else basename
        (table, unused) = filehandler.csv_read(csv_filename, ch.fieldnames, skip_lines)

        # Fix table
        vh = TableFixer(regexes=regexes, table=table, tagtail=tagtail, **ch.config_new)
        table_fixed = vh.fix_table()

        # Create new table
        d2d = TableMapper(table_fixed, ch.fieldmap_new)
        table_new = d2d.data_new
                
        # Write
        csv_filename_new = csv_filename.replace('.csv', 'NB.csv')
        filehandler.csv_write(table_new, csv_filename_new, ch.fieldnames_new)
#         filehandler.csv_print(table_new, fieldnames_new)

        # Print output csv_filename
        print csv_filename_new
    
if __name__ == '__main__':
    
    SRGP = getenv("HOME") + '/Desktop/SRGP/'

    # CSV Filename
    csv_filename = None
    if len(argv) == 1:
        csv_filename = SRGP + 'members/SRGP_MembersAll_20141119-2321head.csv'
    else:
        csv_filename = argv[1]
    
    # Config module
    modulename = None
    if len(argv) == 2:
        modulename = argv[2]
    elif search('register', csv_filename):
        modulename = 'config_electoral_register2014'
    elif search('Members', csv_filename):
        modulename = 'config_members'
    elif search('canvass', csv_filename):
        modulename = 'config_canvassing_sheets'
        
    main = Main(csv_filename, modulename)
    
