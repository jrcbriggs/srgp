#!/usr/bin/python
'''
Created on 1 Nov 2014

@author: julian

config for Sheffield City Council electoral roll (register of electors) 2013 
eg ga.xls

PD, ENO, Status, Title, First, Names, Initials, Surname, Suffix, Date of Attainment, Franchise Flag, Address 1, Address 2, Address 3, Address 4, Address 5, Address 6, Address 7

'''
from collections import OrderedDict


config = {
         'address_fields' : (
            'Address 1',
            'Address 2',
            'Address 3',
            'Address 4',
            'Address 5',
            'Address 6',
            'Address 7',
            ),
        'date_fields' : ('Date of Attainment',),
        'date_format' : '%d/%m/%Y', #_electoral_roll
        'doa_field' : 'Date of Attainment',
        'fieldmap':OrderedDict([
                ('PD', 'tag_list'), #city_sub_district
                ('ENO', 'external_id'),
                ('Status', 'tag_list'),
                ('Title', 'prefix'),
                ('First Names', 'first_name'),
                ('Initials', 'middle_name'),
                ('Surname', 'last_name'),
                ('Suffix', 'suffix'),
                ('Date of Attainment', 'dob'),
                ('Franchise Flag', 'tag_list'),
                ('Address 1', 'registered_address1'),
                ('Address 2', 'registered_address2'),
                ('Address 3', 'registered_address3'),
                ('Address 4', 'registered_address4'), #omitting this field did not make registered address visible immediately
                ('Address 5', 'registered_city'),
                ('Address 6', 'registered_zip'),
                ('Address 7', 'registered_country_code'),
                ]),
        'skip_lines':1,
    }
