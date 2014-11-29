#!/usr/bin/python
'''
Created on 1 Nov 2014

@author: julian

config for Sheffield City Council electoral roll (register of electors) 2013 
eg ga.xls
'''


config = {
         'address_fields' : (
            'Qualifying_Address_1',
            'Qualifying_Address_2',
            'Qualifying_Address_3',
            'Qualifying_Address_4',
            'Qualifying_Address_5',
            'Qualifying_Address_6',
            'Qualifying_Address_7',
            'Qualifying_Address_8',
            'Qualifying_Address_9',
            ),
        'address_fields2' : ( 'Street', 'City', 'Postcode', 'CountryCode', 'tag_list'),
        'date_fields' : ('Election_Date',),
        'fieldnames' : (
            'Authority_Name', 'Area_Name',
            'PD_Letters', 'Alternate_PD',
            'Published_ENo', 'Supplementary',
            'Forename', 'Initials',
            'Surname', 'Proxy_Name',
            'Send_Address_1', 'Send_Address_2',
            'Send_Address_3', 'Send_Address_4',
            'Send_Address_5', 'Send_Postcode',
            'Qualifying_Address_1', 'Qualifying_Address_2',
            'Qualifying_Address_3', 'Qualifying_Address_4',
            'Qualifying_Address_5', 'Qualifying_Address_6',
            'Qualifying_Address_7', 'Qualifying_Address_8',
            'Qualifying_Address_9', 'Absent_Status',
            'Overseas_Address', 'Away_Address',
            'Election_Date', 'Election_Title_1',
            'Election_Title_2',
        ),
        'tagfields' : (
            'PD_Letters'      ,
            'Published_ENo'   ,
            'Absent_Status'   ,
            'Overseas_Address',
            'Away_Address'    ,
            'Election_Date'   ,
            'Election_Title_1',
            'Election_Title_2',
        ),
    }
