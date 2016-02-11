#!/usr/bin/python3
'''
Created on 7 Feb 2016

@author: julian

Configurations for preparing csv files for import to Nation Builder (NB).
Each config is an OrderedDict.

'''
from collections import OrderedDict as OD
from copy import deepcopy
import os
from re import IGNORECASE, compile
from csv_fixer2 import TableFixer

# Robin Latimer (Broomhill canvassing ) Database
party_map_rl = {'AT': None, 'G': 'G', 'L': 'L', 'LD': 'D', 'NG': None, 'NI': None, 'NV': None, 'SG': 'G', 'SL': 'L', 'SLD': 'D', }
support_level_map_rl = {'AT':5, 'G':1, 'L':5, 'LD':5, 'NG':5, 'NI':3, 'NV':3, 'SG':2, 'SL':4, 'SLD':4, }
tag_map_rl = {'':'',
                         'Case': 'casework15 ',
                        'Poster': 'poster15',
                        'stdt': 'student15',
                        'Ben': 'Benefits',
                        'Crime':'Crime',
                        'Litter':'Litter',
                        'Recyc':'Recycling',
                        '20mph': '20mph',
                        'Lib':'Library',
                        'Plan':'Planning',
                        'ResPark':'ResidentsParking',
                        'StrtAhed':'StreetsAhead',
                        'Traf': 'Traffic',
                        'Post': 'Postal15',
                        'Vote14': 'Voted14',
                        'Vote12': 'Voted12',
                        }
config_rl = OD([
                # ('fieldname_new', 'fieldname_old'), # or
                # ('fieldname_new', (func, [args]{kwargs})),
                ('config_name', 'config_rl'),
                ('statefile_id', (TableFixer.merge_pd_eno, [], {'pd':'polldist', 'eno':'elect no', },)),
                ('dob', (TableFixer.doa2dob, [], {'doa': 'Date18'})),
                ('last_name', 'Surname'),
                ('first_name', 'First name'),
                ('registered_address1', (TableFixer.fix_address1, [], {
                                              'housename':'Housename',
                                              'street_number':'Number',
                                              'street_name':'Road',
                                              })),
                ('registered_address2', (TableFixer.fix_address2, [], {
                                              'block_name':'Block',
                                              })),
                ('registered_address3', None),
                ('registered_city', 'Addend'),
                ('registered_zip', 'Postcode'),
                ('email', 'E-mail'),
                ('phone_number', 'Phone'),
                ('background', (TableFixer.background_merge, [], {'notes':'Notes', 'comments':'Comments'})),
                ('party', (TableFixer.fix_party, [party_map_rl], {'party': 'Party', })),
                ('support_level', (TableFixer.fix_support_level, [support_level_map_rl], {'support_level': 'Party', })),
                ('tag_list', (TableFixer.tags_add, [tag_map_rl], {'k0': 'Demographic',
                                                                 'k1': 'national',
                                                                 'k2': 'Local',
                                                                 'k3': 'Post',
                                                                 'k4': 'Vote14',
                                                                 'k5': 'Vote12',
                                                                 }
                              )
                 ),
              ])

