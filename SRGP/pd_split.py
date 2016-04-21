'''
Created on 21 Apr 2016

@author: julian
Split input csv into separate CSVs by PD
Assumes PD is first field in CSV
'''
from os.path import dirname, join
from re import findall
import sys


class Main(object):
    
    def __init__(self,pathname):
        self.fh_lookup = {}
        self.fh_in = open(pathname, 'r')
        self.dirname=dirname(pathname)
    
    def main(self):
        self.header = self.fh_in.readline()
        for line in self.fh_in:
            self.line_handler(line)
            
    def line_handler(self, line):
        pd = findall('^(\w\w)', line)[0]
        
        fh = self.fh_lookup.get(pd)
        if not fh:
            fh = self.fh_lookup.setdefault(pd, self.fh_get(pd))
            print(self.header, file=fh, end='')
        print(line, file=fh, end='')
        
    def fh_get(self, pd):
        return open(join(self.dirname,pd + '.csv'), 'w')
    
if __name__ == '__main__':
    if len(sys.argv)>1:
        pathname=sys.argv[1]
    else:      
        pathname = '/home/julian/SRGP/test/test.csv'
    m = Main(pathname)
    m.main()
