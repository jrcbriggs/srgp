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

from csv_fixer2 import TableFixer as tf


# from csv_fixer2.TableFixer import merge_pd_eno, fix_address1, fix_address2, background_merge, tags_add
tag_map_robin_latimer = {'Case': 'casework15 ',
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
                    'Post': 'Postal14',
                    'Vote14': 'Vote14',
                    'Vote12': 'Vote12',
                    }
'''                        ('fieldname_new', 'fieldname_old'), # or
                           ('fieldname_new', (func, {kwargs})),
'''
config_robin_latimer = OD([
                            ('statefile_id', (tf.merge_pd_eno, {'pd':'polldist', 'eno':'elect no', },)),
                            ('dob', 'Date18'),
                            ('last_name', 'Surname'),
                            ('first_name', 'First name'),
                            ('registered_address1', (tf.fix_address1, {
                                                          'housename':'Housename',
                                                          'street_number':'Number',
                                                          'street_name':'Road',
                                                          })),
                            ('registered_address2', (tf.fix_address2, {
                                                          'block_name':'Block',
                                                          })),
                            ('registered_address3', None),
                            ('registered_city', 'Addend'),
                            ('registered_zip', 'Postcode'),
#                             ('', 'HholdNo'),
#                             ('', 'F'),
#                             ('', 'SelHhold'),
#                             ('', 'HouseFilt'),
                            ('background', (tf.background_merge, {'notes':'Notes',
                                                              'comments':'Comments'})),
                            ('tag_list', (tf.tags_add, {'fieldnames': ('Demographic',
                                                                                  'national',
                                                                                  'Local',
                                                                                  'Post',
                                                                                  'Vote14',
                                                                                  'Vote12',
                                                                                  ),
                                                                    'tag_map': tag_map_robin_latimer, })),
                            ('phone_number', 'Phone'),
                            ('email', 'E-mail'),
#                             ('', 'Date'),
                            ('', 'OnReg'),
                            ('', 'Lastvote'),
                          ])
