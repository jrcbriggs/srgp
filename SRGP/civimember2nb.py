'''
Created on 1 Nov 2014

@author: julian
'''
from csv import DictReader, DictWriter
from datetime import datetime as dt
from os.path import join

DOWNLOADS_DIR = '/home/julian/Downloads'
BASENAME_MEMBERS = 'SRGP_AllMembers_20141101-1139'
EXT = '.csv'
UPDATED = '_NB'

class MembersHandler(object):

    def __init__(self, pathname=None, table=None, FIELDNAMES=None):
        # Dates
        self.date_fields = ('Start Date', 'End Date', 'Member Since')
        self.date_civi = '%Y-%m-%d'
        self.date_nb = '%m/%d/%Y'
        
        #New Columns
        self.columns_new={'StatusNB':'active', 'Membership Type':'Current'}        
            
        #Initialise table either read file or from argument
        if pathname:
            self.csv_read(pathname)
        elif table:
            self.table=table
            self.fieldnames=FIELDNAMES
        else:
            raise Exception('must pass either csv filename or populated table ')
            
    def append_fields(self, row):
        '''NB: Status must be either 'active', 'grace period', 'expired', or 'canceled' 
           Append column values in place in row'''
        for k, v in self.columns_new.items():
            row[k] = v

    def csv_read(self, pathname):
        with open(pathname, 'r') as csvfile:
            dr = DictReader(csvfile)
            self.table = [row for row in dr]
            self.fieldnames = dr.fieldnames
        self.fieldnames2 = dr.fieldnames[:] + self.columns_new.keys()

    def csv_write(self, pathname):
        with open(pathname, 'w') as csvfile:
            dw = DictWriter(csvfile, self.fieldnames2)   
            dw.writeheader()
            dw.writerows(self.table)
        
    def fix_table(self):
        for row in self.table:
            self.append_fields(row)
            self.fix_dates(row)
            
    def fix_date(self, date):
        '''civi date format: 2009-11-16
        NB date format: 11-16-2009
        if date is just whitespace return empty string'''
        date = date.strip()
        if date:
            return dt.strftime(dt.strptime(date, self.date_civi), self.date_nb)
        else:
            return date            
           
    def fix_dates(self, row):
        '''Update date fields inplace'''
        for field in self.date_fields:
            row[field] = self.fix_date(row[field])
                    

if __name__ == '__main__':
    
    # Read
    pathname = join(DOWNLOADS_DIR, BASENAME_MEMBERS + EXT)
    print pathname
    vh = MembersHandler(pathname=pathname)
    members = vh.table
 
    # Reformat dates
    vh.fix_table()
    
    # Write
    pathname = join(DOWNLOADS_DIR, BASENAME_MEMBERS + UPDATED + EXT)
    vh.csv_write(pathname)
    print 'Done'
    
