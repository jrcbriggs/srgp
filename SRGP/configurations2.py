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
tag_map_robin_latimer = {'':'',
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
                        'Post': 'Postal14',
                        'Vote14': 'Vote14',
                        'Vote12': 'Vote12',
                        }

party_map = {
            'AT': None,
            'G': 'G',
            'L': 'L',
            'LD': 'D',
            'NG': None,
            'NI': None,
            'NV': None,
            'SG': 'G',
            'SL': 'L',
            'SLD': 'D',
}
support_level_map = {
            'AT':5,
            'G':1,
            'L':5,
            'LD':5,
            'NG':5,
            'NI':3,
            'NV':3,
            'SG':2,
            'SL':4,
            'SLD':4,
}
config_robin_latimer = OD([
                            # ('fieldname_new', 'fieldname_old'), # or
                            # ('fieldname_new', (func, {kwargs})),
                            ('config_name', 'config_robin_latimer'),
                            ('statefile_id', (tf.merge_pd_eno, {'key_pd':'polldist', 'key_eno':'elect no', },)),
                            ('dob', (tf.doa2dob, {'key_doa': 'Date18'})),
                            ('last_name', 'Surname'),
                            ('first_name', 'First name'),
                            ('registered_address1', (tf.fix_address1, {
                                                          'key_housename':'Housename',
                                                          'key_street_number':'Number',
                                                          'key_street_name':'Road',
                                                          })),
                            ('registered_address2', (tf.fix_address2, {
                                                          'key_block_name':'Block',
                                                          })),
                            ('registered_address3', None),
                            ('registered_city', 'Addend'),
                            ('registered_zip', 'Postcode'),
                            ('email', 'E-mail'),
                            ('phone_number', 'Phone'),
                            ('background', (tf.background_merge, {'key_notes':'Notes',
                                                              'key_comments':'Comments'})),
                            ('party', (tf.fix_party, {'key_party': 'Party', 'party_map':party_map, })),
                            ('support_level', (tf.fix_support_level, {'key_support_level': 'Party', 'support_level_map':support_level_map, })),
                            ('tag_list', (tf.tags_add, {'fieldnames': ('Demographic',
                                                                                  'national',
                                                                                  'Local',
                                                                                  'Post',
                                                                                  'Vote14',
                                                                                  'Vote12',
                                                                                  ),
                                                                    'tag_map': tag_map_robin_latimer, })),
                          ])
