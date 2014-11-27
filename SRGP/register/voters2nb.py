#!/usr/bin/python
'''
Created on 1 Nov 2014

@author: julian
'''
from os import path
from sys import argv
import sys

from address_regexes import regexes
from voter_handler import FileHandler, RegisterFixer, Dict2Dict, ConfigHandler


class Main(object):
    def __init__(self, argv):
        csv_filename = argv[1]
        basename = path.basename(csv_filename).replace('.csv', '')
        filehandler = FileHandler()        
        
        # Load config
        config_filename = argv[2]
        config = filehandler.config_load(config_filename)
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

        # Print output filename
        print csv_filename_new
    
if __name__ == '__main__':
    # Set argv for testing
#     SRGP = '/home/ph1jb/SRGP/'
#     SRGP = '/home/julian/Desktop/SRGP/'
#     argv += [SRGP + 'electoralregister-apr2014head.csv']
#     argv += ['config_electoral_register2014.py']
    main = Main(argv)
    
