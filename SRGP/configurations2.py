#!/usr/bin/python3
'''
Created on 7 Feb 2016

@author: julian

Configurations for preparing csv files for import to Nation Builder (NB).
Each class has an config (List of tuples) with supporting (mappings) dicts 

config =[
    ('col1a', 'col0a'), # or
    ('col1b', 'col0b'), # or
    ('col1c', (func0c, [args0c]{kwargs0c})),
    ('col1d', (func0d, [args0d]{kwargs0d})),
    ...
    ]
    
Where:
  col1a, col1b etc are the column names for the new csv in order.
  col0a, col0b etc are the column names for the old csv, where we can simply copy column values from old to new column
  func0c, func0d etc are the function called with given args and kwargs which returns the value for the new column
    the kwarg keys are named kwargs in the function, the kwarg values name columns in the old csv.
    The function is called with the given args and given kwargs with kwarg values set to the values in the named columns in the old csv
    See the csv_fixer2.py module for function definitions
Most classes have maps which provide a lookup from old value to new value.
 

'''
from collections import OrderedDict
from copy import deepcopy

from csv_fixer2 import AddressHandler as AD, Canvass as CN, Generic as GN, Member as MB, Register as RG, Volunteer as VL, Voter as VT


class Member(object):
    address_headers = {'k0':'Street Address', 'k1':'Supplemental Address 1', 'k2':'Supplemental Address 2', 'k3':'City', 'k4':'Postal Code'}
    party_map = {'Current':'G', 'Cancelled':None, 'Deceased':None, 'Expired':None, 'Grace':'G', 'New':'G', 'Pending':'G', }
    party_member_map = {'Current':True, 'Cancelled':False, 'Deceased':False, 'Expired':False, 'Grace':True, 'New':True, 'Pending':True, }
    party_status_map = {'Current':'active', 'Cancelled':'canceled', 'Deceased':'expired', 'Expired':'expired', 'Grace':'grace period', 'New':'active', 'Pending':'grace period', }
    support_level_map = {'Current':1, 'Cancelled':4, 'Deceased':None, 'Expired':2, 'Grace':1, 'New':1, 'Pending':1, }
    config = OrderedDict([
        ('first_name', 'First Name'),
        ('last_name', 'Last Name'),
        ('civicrm_id', 'Contact ID'),
        ('membership_type', 'Membership Type'),
        ('expires_on', (MB.fix_date, [party_status_map], {'date':'End Date', 'status':'Status', })),
        ('started_at', (MB.fix_date, [], {'date':'Member Since', })),
        ('membership_status', (MB.get_status, [party_status_map], {'end_date':'End Date', 'status':'Status', })),
        ('address_address1', (AD.address_get, ['address1'], address_headers)),
        ('address_address2', (AD.address_get, ['address2'], address_headers)),
        ('address_address3', (AD.address_get, ['address3'], address_headers)),
        ('address_city', (AD.address_get, ['city'], address_headers)),
        ('address_zip', (AD.address_get, ['postcode'], address_headers)),
        ('address_country_code', (RG.country_code_get, [], {})),  # Always GB
        ('email', 'Email'),
        ('phone_number', 'Phone (primary)'),
        ('mobile_number', 'Mobile'),
        ('precinct_name', 'Ward'),
        ('party', (MB.get_party, [party_map], {'status':'Status', })),
        ('is_deceased', (MB.is_deceased, [], {'status':'Status', })),
        ('party_member', (MB.get_party_member, [party_member_map], {'status':'Status', })),
        ('support_level', (MB.get_support_level, [support_level_map], {'status':'Status', })),
        ('registered_state', (GN.state_get, [], {})),
        ])
    
class Postal(object): 
    '''AV Type,PD/ENO,Elector Surname,Elector Forename,Elector Initials,Elector Suffix,Elector Title,
    Corres Address Line 1,Corres Address Line 2,Corres Address Line 3,Corres Address Line 4,Corres Address Line 5,
    Corres Address Postcode,Corres Address Country,Proxy Name,Send Address Line 1,Send Address Line 2,Send Address Line 3,
    Send Address Line 4,Send Address Line 5,Send Address Postcode  
    '''  
    address_headers = {'add{}'.format(n):'Corres Address Line {}'.format(n) for n in range(1, 6)}
    ward_map = {'E': 'Broomhill',
                'G': 'City',
                'H': 'Crookes & Crosspool',
                'L': 'Ecclesall',
                'O': 'Gleadless Valley',
                'R': 'Manor Castle',
                'T': 'Nether Edge & Sharrow',
                'Z': 'Walkley',
                    }
    av_map = {'Postal':'Postal16', 'Postal Proxy':'Postal16,Proxy16', 'Proxy':'Proxy16', }
    config = OrderedDict([
        ('state_file_id', (VT.merge_pd_slash_eno, [], {'pd_slash_eno':'PD/ENO', },)),
        ('prefix', 'Elector Title'),
        ('first_name', 'Elector Forename'),
        ('middle_name', 'Elector Initials'),
        ('last_name', 'Elector Surname'),
        ('suffix', 'Elector Suffix'),
        ('registered_address1', (AD.address_get, ['address1'], address_headers)),
        ('registered_address2', (AD.address_get, ['address2'], address_headers)),
        ('registered_address3', (AD.address_get, ['address3'], address_headers)),
        ('registered_city', (AD.address_get, ['city'], address_headers)),
        ('registered_zip', 'Corres Address Postcode'),
        ('registered_state', (GN.state_get, [], {})),
        ('registered_country', 'Corres Address Country'),
        ('ward', (RG.ward_get_slash_eno, [ward_map], {'pd_slash_eno':'PD/ENO', })),
        ('tag_list', (VT.tags_add_postal, [av_map], {'av_type':'AV Type', 'pd_slash_eno': 'PD/ENO', })),
        ])
    
class Register(object):   
    tag_map = {'':'', 'A':'Added', 'D':'Deleted', 'M':'Modified', 'K':'K',
                     'E':'European', 'F':'UK EU', 'G':'Local Scots', 'K':'Local Scots EU', 'L':'Local', }
    address_headers = {'add{}'.format(n):'Address {}'.format(n) for n in range(1, 8)}
    ward_map = {'E': 'Broomhill',
                'G': 'City',
                'H': 'Crookes & Crosspool',
                'L': 'Ecclesall',
                'O': 'Gleadless Valley',
                'R': 'Manor Castle',
                'T': 'Nether Edge & Sharrow',
                'Z': 'Walkley',
                    }
    config = OrderedDict([
        ('state_file_id', (VT.merge_pd_eno, [], {'pd':'PD', 'eno':'ENO', },)),
        ('prefix', 'Title'),
        ('first_name', 'First Name'),
        ('middle_name', 'Initials'),
        ('last_name', 'Surname'),
        ('suffix', 'Suffix'),
        ('dob', (GN.doa2dob, [], {'doa': 'Date Of Attainment'})),
        ('registered_address1', (AD.address_get, ['address1'], address_headers)),
        ('registered_address2', (AD.address_get, ['address2'], address_headers)),
        ('registered_address3', (AD.address_get, ['address3'], address_headers)),
        ('registered_city', (AD.address_get, ['city'], address_headers)),
        ('registered_zip', 'Postcode'),
        ('registered_state', (GN.state_get, [], {})),
        ('ward', (RG.ward_get, [ward_map], {'pd':'PD', })),
        ('tag_list', (VT.tags_add_voter, [tag_map], {'PD': 'PD',
                                                    'Status': 'Status',
                                                    'Franchise': 'Franchise Flag',
                                                    })),
        ])

class RegisterCentralConstituency20160401(Register):
    tag_map = Register.tag_map 
    address_headers = deepcopy(Register.address_headers) 
    ward_map = Register.ward_map 
    config = deepcopy(Register.config)
    config['registered_zip'] = (AD.address_get, ['postcode'], address_headers)
    config['state_file_id'] = (VT.merge_pd_eno, [], {'pd':'PD', 'eno':'ENO', },)

class Register2015(Register):   
    tag_map = {'':'', 'A':'Added', 'D':'Deleted', 'M':'Modified', 'K':'K',
                     'E':'European', 'F':'UK EU', 'G':'Local Scots', 'K':'Local Scots EU', 'L':'Local', }
    address_headers = {'add{}'.format(n):'Address {}'.format(n) for n in range(1, 8)}
#     ward_map = {'E': 'Broomhill',
#                 'G': 'Central',
#                 'H': 'Crookes',
#                 'L': 'Ecclesall',
#                 'O': 'Gleadless Valley',
#                 'R': 'Manor Castle',
#                 'T': 'Nether Edge',
#                 'Z': 'Walkley',
#                     }
    ward_map = {'E': 'Broomhill',
                'G': 'City',
                'H': 'Crookes & Crosspool',
                'L': 'Ecclesall',
                'O': 'Gleadless Valley',
                'R': 'Manor Castle',
                'T': 'Nether Edge & Sharrow',
                'Z': 'Walkley',
                    }
    config = OrderedDict([
        ('state_file_id', (VT.merge_pd_eno, [], {'pd':'PD', 'eno':'ENO', },)),
        ('prefix', 'Title'),
        ('first_name', 'First Names'),
        ('middle_name', 'Initials'),
        ('last_name', 'Surname'),
        ('suffix', 'Suffix'),
        ('dob', (GN.doa2dob, [], {'doa': 'Date of Attainment'})),
        ('registered_address1', (AD.address_get, ['address1'], address_headers)),
        ('registered_address2', (AD.address_get, ['address2'], address_headers)),
        ('registered_address3', (AD.address_get, ['address3'], address_headers)),
        ('registered_city', (AD.address_get, ['city'], address_headers)),
        ('registered_zip', 'Postcode'),
        ('registered_state', (GN.state_get, [], {})),
        ('ward', (RG.ward_get, [ward_map], {'pd':'PD', })),
        ('tag_list', (VT.tags_add_voter, [tag_map], {'PD': 'PD',
                                                    'Status': 'Status',
                                                    'Franchise': 'Franchise Flag',
                                                    })),
        ])

    
class RobinLatimer(object):
    ''' Robin Latimer (Broomhill canvassing ) Database'''
    party_map = {'':None, 'AT': None, 'G': 'G', 'L': 'L', 'LD': 'D', 'NG': None, 'NI': None, 'NV': None, 'SG': 'G', 'SL': 'L', 'SLD': 'D', }
    support_level_map = {'':None, 'AT':5, 'G':1, 'L':5, 'LD':5, 'NG':4, 'NI':5, 'NV':4, 'SG':2, 'SL':3, 'SLD':3, }
    tag_map = {
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
    config = OrderedDict([
        ('state_file_id', (VT.merge_pd_eno, [], {'pd':'polldist', 'eno':'elect no', },)),
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
        ('party', (VT.fix_party, [party_map], {'party': 'Party', })),
        ('support_level', (VT.fix_support_level, [support_level_map], {'support_level': 'Party', })),
        ('tag_list', (GN.tags_add, [tag_map], {'k0': 'Demographic',
                                                 'k1': 'national',
                                                 'k2': 'Local',
                                                 'k3': 'Post',
                                                 'k4': 'Vote14',
                                                 'k5': 'Vote12',
                                                 }
                      )
         ),
      ])

class Supporter(object):
    address_headers = {'k0':'Street Address', 'k1':'Supplemental Address 1', 'k3':'City', 'k4':'Postal Code'}
    party_map = {'Current':'G', 'Cancelled':None, 'Deceased':None, 'Expired':None, 'Grace':'G', 'New':'G', }
    config = OrderedDict([
        ('name', 'Contact Name'),
        ('civicrm_id', 'Contact ID'),
        ('address_address1', (AD.address_get, ['address1'], address_headers)),
        ('address_address2', (AD.address_get, ['address2'], address_headers)),
        ('address_address3', (AD.address_get, ['address3'], address_headers)),
        ('address_city', (AD.address_get, ['city'], address_headers)),
        ('address_zip', (AD.address_get, ['postcode'], address_headers)),
        ('address_country_code', (RG.country_code_get, [], {})),  # Always GB
        ('email', 'Email'),
        ('phone_number', 'Phone (primary)'),
        ('mobile_number', 'Mobile'),
        ('precinct_name', 'Ward'),
        ('party', (MB.get_party_green, [], {})),
        ('registered_state', (GN.state_get, [], {})),
        ])

class Volunteer(object):
    status_map = {"I've not been contacted":"volunteer_not_contacted", "I've been contacted but not yet helping":"volunteer_contacted", "I'm already helping":"volunteer_helping", }
    availability_map = {'Anytime':'volunteer_anytime', 'Election Time':'volunteer_election_time', 'Evenings':'volunteer_evenings', 'Weekdays':'volunteer_weekdays', 'Weekends':'volunteer_weekends', }
    action_map = {'Attend an Action Day':'',
                'Canvassing':'volunteer_canvass',
                'Donate':'donor',
                'Election Day Telling':'canvass_electionday',
                'Leafletting':'canvass_leaflet',
                'Envelope Stuffing':'envelope',  # TODO
                'Phone Canvassing':'canvass_phone',
                'Postal Vote':'',
                'Poster Display':'Poster16',
                'Run a Stall':'canvass_stall',
                'Vote Green':'',
                }
    skill_map = {'Admin':'volunteer_skill',
                'Any Other':'volunteer_skill',
                'Campaigning':'volunteer_skill',
                'Designer':'volunteer_skill',
                'Driver':'volunteer_skill',
                'Events':'volunteer_skill',
                'Film Making':'volunteer_skill',
                'Food':'volunteer_skill',
                'HR':'volunteer_skill',
                'Fundraising':'volunteer_skill',
                'NGO and Government':'volunteer_skill',
                'Poster Board':'volunteer_skill',
                'PR and Media':'volunteer_skill',
                'Press':'volunteer_skill',
                'Social Media':'volunteer_skill',
                'Web Development':'volunteer_skill',
                'Writing':'volunteer_skill', }
    tag_map = {'':''}
    tag_map.update(status_map)
    tag_map.update(availability_map)
    tag_map.update(action_map)
    tag_map.update(skill_map)
    config = OrderedDict([
        ('name', 'Contact Name'),
        ('civicrm_id', 'Contact ID'),
        ('email', 'Email'),
        ('phone_number', 'Phone (primary)'),
        ('mobile_number', 'Mobile'),
        ('precinct_name', 'Ward'),
        ('party', (MB.get_party_green, [], {})),
        ('registered_state', (GN.state_get, [], {})),
        ('tag_list', (GN.tags_add, [tag_map], {
                                        'volunteer_status':'Status',
                                        'volunteer_at':'Availability',
    #                                       'volunteer_can_help_from':'I can help from',
                                        'volunteer_actions':'Actions',
                                        'volunteer_skills':'Skills',
    #                                       'volunteer_skills_other':'Skills: Other',
                                          })),
        ])
    
class YoungGreens(object):
    party_status_map = {'Current':'active', 'Cancelled':'canceled', 'Deceased':'expired', 'Expired':'expired', 'Grace':'grace period', 'New':'active', 'Pending':'grace period', }
    config = OrderedDict([
        ('first_name', 'First Name'),
        ('last_name', 'Last Name'),
        ('civicrm_id', 'Contact ID'),
        ('started_at', (MB.fix_date, [], {'date':'Start Date', })),
        ('expires_on', (MB.fix_date, [party_status_map], {'date':'End Date', 'status':'Status', })),
        ('membership_status', (MB.get_status, [party_status_map], {'end_date':'End Date', 'status':'Status', })),
        ('membership_type', (GN.value_get, ['YoungGreen'], {})),
        ])
    
class NB(object):
    fields = ('nationbuilder_id',
              'state_file_id',
                'prefix',
                'first_name',
                'middle_name',
                'last_name',
                'suffix',
                'registered_address1',
                'registered_address2',
                'registered_address3',
                'registered_city',
                'registered_zip',
                'registered_state',
                'precinct_name',
                'tag_list',
            )
    config = OrderedDict([(f, f) for f in fields])


config_lookup = [
     ('BroomhillCanvassData', RobinLatimer.config, 'RobinLatimer.config',),
     ('CentralConstituencyRegister', Register.config, 'Register.config',),
     ('CentralConstituencyWardRegisters', Register.config, 'Register.config',),
     ('TTWRegisters', Register.config, 'Register.config',),
     ('RegisterCentralConstituency20160401', RegisterCentralConstituency20160401.config, 'RegisterCentralConstituency20160401.config',),
     ('Register2015', Register2015.config, 'Register2015.config',),
     ('RegisterPostal', Postal.config, 'Postal.config',),
     ('Register', Register.config, 'Register.config',),
     ('nationbuilder-people-export', NB.config, 'NB.config',),
     ('SRGP_MembersAll', Member.config, 'Member.config',),
     ('SRGP_SupportersAll', Supporter.config, 'Supporter.config',),
     ('SRGP_VolunteersAll', Volunteer.config, 'Volunteer.config',),
     ('SRGP_YoungGreens', YoungGreens.config, 'YoungGreens.config',),
     ('nationbuilder-people-export', NB.config, 'NB.config',),
     ]
