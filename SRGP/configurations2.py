#!/usr/bin/python3
'''
Created on 7 Feb 2016

@author: julian

Configurations for preparing csv files for import to Nation Builder (NB).
Each config is an OrderedDict.
'''

from collections import OrderedDict as OD

from csv_fixer2 import AddressHandler as AD, Canvass as CN, Generic as GN, Member as MB, Register as RG, Voter as VT


# Robin Latimer (Broomhill canvassing ) Database
party_map_rl = {'':None, 'AT': None, 'G': 'G', 'L': 'L', 'LD': 'D', 'NG': None, 'NI': None, 'NV': None, 'SG': 'G', 'SL': 'L', 'SLD': 'D', }
support_level_map_rl = {'':None, 'AT':5, 'G':1, 'L':5, 'LD':5, 'NG':4, 'NI':5, 'NV':4, 'SG':2, 'SL':3, 'SLD':3, }
tag_map_rl = {
    '':'',
    'Case': 'casework15 ',
    'Poster': 'poster15',
    'Stdt': 'student15',
    'stdt': 'student15',
    'Ben': 'Benefits',
    'Crime':'Crime',
    'Litter':'Litter',
    'Recyc':'Recycling',
    '20mph': '20mph',
    'Lib':'Library',
    'Plan':'Planning',
    'Planning':'Planning',
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
    ('statefile_id', (VT.merge_pd_eno, [], {'pd':'polldist', 'eno':'elect no', },)),
    ('dob', (GN.doa2dob, [], {'doa': 'Date18'})),
    ('last_name', 'Surname'),
    ('first_name', 'First name'),
    ('registered_address1', (CN.fix_address1, [], {
                                  'housename':'Housename',
                                  'street_number':'Number',
                                  'street_name':'Road',
                                  })),
    ('registered_address2', (CN.fix_address2, [], {
                                  'block_name':'Block',
                                  })),
    ('registered_address3', None),
    ('registered_city', 'Addend'),
    ('registered_zip', 'Postcode'),
    ('email', 'E-mail'),
    ('phone_number', 'Phone'),
    ('background', 'Comments'),
    ('party', (VT.fix_party, [party_map_rl], {'party': 'Party', })),
    ('support_level', (VT.fix_support_level, [support_level_map_rl], {'support_level': 'Party', })),
    ('tag_list', (GN.tags_add, [tag_map_rl], {'k0': 'Demographic',
                                             'k1': 'national',
                                             'k2': 'Local',
                                             'k3': 'Post',
                                             'k4': 'Vote14',
                                             'k5': 'Vote12',
                                             'basename':'basename' ,                                                                       
                                             }
                  )
     ),
  ])

tag_map_voter = {'A':'Added', 'D':'Deleted', 'M':'Modified', 'K':'K',
                 'E':'European', 'F':'UK EU', 'G':'Local Scots', 'K':'Local Scots EU', 'L':'Local', }
address_register = {'add{}'.format(n):'Address {}'.format(n) for n in range(1, 8)}
ward_lookup = {'E': 'Broomhill',
                'G': 'Central',
                'H': 'Crookes',
                'L': 'Ecclesall',
                'O': 'Gleadless Valley',
                'R': 'Manor Castle',
                'T': 'Nether Edge',
                'Z': 'Walkley',
                }
config_register = OD([
    ('config_name', 'config_register'),
    ('statefile_id', (VT.merge_pd_eno, [], {'pd':'PD', 'eno':'ENO', },)),
    ('prefix', 'Title'),
    ('first_name', 'First Name'),
    ('middle_name', 'Initials'),
    ('last_name', 'Surname'),
    ('suffix', 'Suffix'),
    ('dob', (GN.doa2dob, [], {'doa': 'Date Of Attainment'})),
    ('registered_address1', (AD.address_get, ['address1'], address_register)),
    ('registered_address2', (AD.address_get, ['address2'], address_register)),
    ('registered_address3', (AD.address_get, ['address3'], address_register)),
    ('registered_city', (AD.address_get, ['city'], address_register)),
    ('registered_zip', (AD.address_get, ['postcode'], address_register)),
    ('registered_state', (GN.state_get, [], {})),
    ('ward', (RG.ward_get, [ward_lookup], {'pd':'PD', })),
    ('tag_list', (RG.tags_add_voter, [tag_map_voter], {'PD': 'PD',
                                                        'status': 'Status',
                                                        'franchise': 'Franchise Flag',
                                                        'basename':'basename' ,                                                                       
                                                        })),
    ])

#########################################################################################
address_member = {'k0':'Street Address', 'k1':'Supplemental Address 1', 'k2':'Supplemental Address 2','k3':'City','k4':'Postal Code'}
config_member = OD([
    ('config_name', 'config_member'),
    ('first_name', 'First Name'),
    ('last_name', 'Last Name'),
    ('civicrm_id', 'Contact ID'),
    ('membership_type', 'Membership Type'),
    ('expires_on', (MB.fix_date, [], {'date':'End Date', })),
    ('started_at', (MB.fix_date, [], {'date':'Member Since', })),
    ('membership_status', (MB.get_status, [], {'status':'Status', })),
    ('address_address1', (AD.address_get, ['address1'], address_member)),
    ('address_address2', (AD.address_get, ['address2'], address_member)),
    ('address_address3', (AD.address_get, ['address3'], address_member)),
    ('address_city', (AD.address_get, ['city'], address_member)),
    ('address_zip', (AD.address_get, ['postcode'], address_member)),
    ('address_country_code', (RG.country_code_get, [], {})),  # Always GB
    ('email', 'Email'),
    ('phone_number', 'Phone (primary)'),
    ('mobile_number', 'Mobile'),
    ('precinct_name', 'Ward'),
    ('party', (MB.get_party, [], {})),
    ('is_deceased', (MB.is_deceased, [], {'status':'Status', })),
    ('party_member', (MB.get_party_member, [], {'status':'Status',})),
    ('support_level', (MB.get_support_level, [], {'status':'Status', })),
    ('registered_state', (GN.state_get, [], {})),
#                     ('ward', 'Ward'),
#                     ('constituency', 'Westminster parliament constituency'),
    ('tag_list', (GN.tags_add, [{}], {'basename':'basename'})),
    ])

#########################################################################################
address_supporter = {'k0':'Street Address', 'k1':'Supplemental Address 1', 'k3':'City','k4':'Postal Code'}
config_supporter = OD([
    ('config_name', 'config_supporter'),
    ('name', 'Contact Name'),
    ('civicrm_id', 'Contact ID'),
    ('address_address1', (AD.address_get, ['address1'], address_supporter)),
    ('address_address2', (AD.address_get, ['address2'], address_supporter)),
    ('address_address3', (AD.address_get, ['address3'], address_supporter)),
    ('address_city', (AD.address_get, ['city'], address_supporter)),
    ('address_zip', (AD.address_get, ['postcode'], address_supporter)),
    ('address_country_code', (RG.country_code_get, [], {})),  # Always GB
    ('email', 'Email'),
    ('phone_number', 'Phone (primary)'),
    ('mobile_number', 'Mobile'),
    ('precinct_name', 'Ward'),
    ('party', (MB.get_party, [], {})),
    ('registered_state', (GN.state_get, [], {})),
#                     ('ward', 'Ward'),
#                     ('constituency', 'Westminster parliament constituency'),
    ('tag_list', (GN.tags_add, [{}], {'basename':'basename'})),
    ])

tag_map_volunteer={}
config_volunteers = OD([
    ('config_name', 'config_supporter'),
    ('name', 'Contact Name'),
    ('civicrm_id', 'Contact ID'),
    ('email', 'Email'),
    ('phone_number', 'Phone (primary)'),
    ('mobile_number', 'Mobile'),
    ('precinct_name', 'Ward'),
    ('party', (MB.get_party, [], {})),
    ('registered_state', (GN.state_get, [], {})),
#                     ('ward', 'Ward'),
#                     ('constituency', 'Westminster parliament constituency'),
    ('tag_list', (GN.tags_add, [{}], {
                                    'basename':'basename',
#                                       'volunteer_status':'Status',
#                                       'volunteer_availability':'Availability',
#                                       'volunteer_can_help_from':'I can help from',
#                                       'volunteer_actions':'Actions',
#                                       'volunteer_skills':'Skills',
#                                       'volunteer_skills_other':'Skills: Other',
                                      })),
    ])

#########################################################################################
config_young_greens = OD([
    ('config_name', 'config_supporter'),
    ('first_name', 'First Name'),
    ('last_name', 'Last Name'),
    ('civicrm_id', 'Contact ID'),
    ('started_at', (MB.fix_date, [], {'date':'Start Date', })),
    ('expires_on', (MB.fix_date, [], {'date':'End Date', })),
    ('membership_status', (MB.get_status, [], {'status':'Status', })),
    ('email', 'Email'),
    ('party', (MB.get_party, [], {})),
    ('registered_state', (GN.state_get, [], {})),
    ('is_deceased', (MB.is_deceased, [], {'status':'Status', })),
    ('party_member', (MB.get_party_member, [], {'status':'Status',})),
    ('support_level', (MB.get_support_level, [], {'status':'Status', })),
    ('tag_list', (GN.tags_add, [{}], {'basename':'basename',
                                      })),
    ])

config_lookup = [
     ('BroomhillCanvassData', config_rl),
     ('CentralConstituencyRegister', config_register),
     ('CentralConstituencyWardRegisters', config_register),
     ('SRGP_MembersAll', config_member),
     ('SRGP_SupportersAll', config_supporter),
     ('SRGP_VolunteersAll', config_volunteers),
     ('SRGP_YoungGreens', config_young_greens),
     ]
