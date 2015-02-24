'''
Created on 24 Feb 2015

@author: ph1jb
'''
from copy import deepcopy
class UpdateRegister(object):

    def __init__(self, ld0, ld1, k0, k1):
        self.d0 = self.ld2dd(ld0, k0, k1)
        self.d1 = self.ld2dd(ld1, k0, k1)

    def ld2dd(self, l0, k0, k1):
        '''Create a dict of rows from a table of rows.
        {(row[k0], row[k1]):row, ...}
        '''
        return {(row[k0], row[k1]): row for row in l0}

    def update(self, d0, d1, status):
        '''Update table d0 with table d1.
        d0 and d1 list of rows where a row is a dictionary {colname:value, ...}
        d1 contains rows with Status='D'. Delete these rows from d0. 
        '''
        d3 = deepcopy(d0)
        d3.update(d1)
        #Delete records with Status='D'
        return {k:v for (k,v) in d3.items() if v[status]!='D'}

if __name__ == '__main__':
    pass
