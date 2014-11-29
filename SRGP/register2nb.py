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
from configurations import config_members, config_register
from register_handler import FileHandler, RegisterFixer, Dict2Dict, ConfigHandler


class Main(object):
    def __init__(self, csv_filename, config):
        basename = path.basename(csv_filename).replace('.csv', '')
        filehandler = FileHandler()        
        
        ch = ConfigHandler(**config)
        
        # Read csv file
        skip_lines = config.get('skip_lines', 0)
        tagtail = argv[3] if len(argv) > 3 else basename
        (table, unused) = filehandler.csv_read(csv_filename, ch.fieldnames, skip_lines)

        # Fix table
        vh = RegisterFixer(regexes=regexes, table=table, tagtail=tagtail, **ch.config_new)
        table_fixed = vh.fix_table()

        # Create new table
        d2d = Dict2Dict(table_fixed, ch.fieldmap_new)
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
        csv_filename = SRGP + 'electoralregister-apr2014head.csv'
    else:
        csv_filename = argv[1]
    
    # Config 
    if search('register', csv_filename):
        config = config_register
    elif search('embers', csv_filename,):
        config = config_members
    elif search('canvass', csv_filename):
        pass
#         config= config_canvass
        
    main = Main(csv_filename, config)
    
