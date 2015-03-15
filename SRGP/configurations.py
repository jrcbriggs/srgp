#!/usr/bin/python3
'''
Created on 27 Nov 2014

@author: julian

Configurations for preparing csv files for import to Nation Builder (NB).
Each config is a dictionary.

Central GP civiCRM exports: config_members
    config_officers
    config_supporter
    config_volunteers
    config_search
Sheffield City Council Electoral Registers:
    config_register
    config_register_city2014_postal

Changes:
# Julian Briggs 11-jan-2015: do not assume ppl in SearchAll are
# supporters. Comment is_supporter extra_field
'''
from collections import OrderedDict as OD
from copy import deepcopy
import os
from re import IGNORECASE, compile
nbslug = 'srgp.nationbuilder.com'
nbtoken = os.getenv('nbtoken')

regexes = {
    'city': compile('^(Rotherham|Sheffield|Stocksbridge)$', IGNORECASE),
    'county': compile('^South Yorks$', IGNORECASE),
    'house': compile('Barn|Building|College|Cottage|Farm|Hall|House|'
                     'Lodge|Mansion|Mill|Residence', IGNORECASE),
    'postcode': compile('^S\d\d? \d\w\w$'),
    'locality': compile('(Arbourthorne|Aston|Aughton|Barnsley|Basegreen|Beauchief|Beighton|'
                        'Bents Green|Bradway|Bramley|Brampton|Brincliffe|Broom|Broomhall|'
                        'Broomhill|Burncross|Burngreave|Catcliffe|Chapeltown|Christchurch|'
                        'City Centre|Clent|Clifton|Crookes|Crookesmoor|Crooks|Crosspool|'
                        'Dalton|Darnall|Deepcar|Dinnington|Dore|East Dene|East Herringthorpe|'
                        'Ecclesall|Firshill|Firth Park|Frecheville|Fulwood|Gleadless|Greasbrough|'
                        'Greenhill|Grenoside|Hackenthorpe|Halfway|Hallam Rock|Handsworth|Hathersage|'
                        'Heeley|Herdings|Herringthorpe|Highfield|High Green|Hillsborough|'
                        'Hooton Levitt|Jordanthrope|Kimberworth|Kiveton Park|Malin Bridge|Maltby|'
                        'Meersbrook|Mexborough|Midhopestones|Millhouses|Mosborough|Nether Edge|'
                        'Nethergreen|Nether Green|Norfolk Park|Norton Lees|Nottingham|Oughtibridge|'
                        'Owlthorpe|Parkgate|Park Hill|Pitsmoor|Rawmarsh|Rivelin|Rotherham|Shalesmoor|'
                        'Sharrow|Sheffield|Shiregreen|Sothall|Stannington|Stocksbridge|Sunnyside|'
                        'Swallownest|Swinton|Thorpe Hesley|Thurcroft|Todwick|Totley|Totley Rise|'
                        'Upperthorpe|Wales Bar|Walkley|Waterthorpe|Wath upon Dearne|Wath-upon-Dearne|'
                        'Well Court|Wellgate|Wentworth|Whiston|Wickersley|Wincobank|Wingfield|'
                        'Woodhouse|Woodseats|Woodsetts|Worksop|Worrall)$', IGNORECASE),
    'street': compile(r'\b(\d+|Anglo Works|Approach|Ashgrove|Ave|Avenue|Bank|Brg|Bridge|'
                      'Brookside|Cir|Close|Common|Crossways|Court|Cres|Crescent|Croft|Ct|Dell|'
                      'Dl|Dr|Drive|Endcliffe Village|Fields|Gdns|Gardens|Gate|Glade|Glen|Gr|Green|'
                      'Grove|Hartshead|Head|Hl|Hill|Ln|Lane|Mdws|Mews|Mt|Parade|Park|Pl|Place|Rd|Rise|'
                      'Road|Row|Sq|Square|St|Street|Ter|Terrace|The Gln|Town|Turn|View|Vw|Waingate|'
                      'Walk|Way|West Bar|Wharf|'
                      'Backfields|Birkendale|Castlegate|Cracknell|'
                      'Cross Smithfield|Kelham Island|'
                      'Summerfield|Upperthorpe|Wicker|'
                      'Fairleigh|Foster|Hartshead|Millsands|Pinsent|Redgrave|The Circle|The Lawns|The Nook|'
                      'Other Electors)',
                      IGNORECASE),
}
config_members = {
    'config_name': 'config_members',
    'address_fields': OD([
        ('address1', 'Street Address',),
        ('address2', 'Supplemental Address 1',),
        ('address3', 'Supplemental Address 2',),
        ('city', 'City',),
        ('zip', 'Postal Code',),
        ('country_code', 'Country',),
    ]),
    'date_fields': ('Start Date', 'End Date', 'Member Since',),
    'date_format': '%Y-%m-%d',  # Membership date: 2014-05-17
    'doa_fields': (),
    'fieldmap': OD([
        ('Contact Name', None),
        ('Joint member name', None),
        ('Postal Greeting', None),
        ('Email Greeting', None),
        ('First Name', 'first_name'),
        ('Last Name', 'last_name'),
        ('Do not mail', 'tag_list'),
        ('Addressee', None),
        ('Contact ID', 'civicrm_id'),
        ('Membership Type', 'membership_type'),
        ('Start Date', None),
        ('End Date', 'expires_on'),
        ('Member Since', 'started_at'),
        ('Source', None),
        ('Status', 'membership_status'),
        ('Street Address', 'address_address1'),
        ('Supplemental Address 1', 'address_address2'),
        ('Supplemental Address 2', 'address_address3'),
        ('City', 'address_city'),
        ('Postal Code', 'address_zip'),
        ('Country', 'address_country_code'),
        ('Email', 'email'),
        ('Phone (primary)', 'phone_number'),
        ('Mobile', 'mobile_number'),
        ('Ward', 'precinct_name'),
        ('Local authority', None),
        ('Westminster parliament constituency', None),
        ('Local party', 'party'),  # encode to G
        ('Regional party', None),
        ('Override local party', None),
    ]),
    'skip_lines': 0,
    'fields_extra': OD([
        ('is_deceased', 'is_deceased'),
        ('is_supporter', 'is_supporter'),
        #         ('party_member', 'party_member'),
        ('party_member_true', 'party_member'),
        #         ('status', 'status'),
        ('support_level', 'support_level'),
        ('registered_state', 'registered_state'),
    ]),
    'fields_flip': (),  # Reverse Sense
}

config_officers = {
    'config_name': 'config_officers',
    'address_fields': OD([
        ('address1', 'Street Address',),
        ('address2', 'Supplemental Address 1',),
        ('address3', 'Supplemental Address 2',),
        ('city', 'City',),
        ('zip', 'Postal Code',),
    ]),
    'date_fields': (),
    'date_format': '%Y-%m-%d',  # Membershiip date: 2014-05-17
    'doa_fields': (),
    'fieldmap': OD([
        ('Relationship Type', 'tag_list'),
        ('Party', 'party'),  # encode to G
        ('Contact Name', 'name'),
        ('Street Address', 'address1'),
        ('Supplemental Address 1', 'address2'),
        ('Supplemental Address 2', 'address3'),
        ('City', 'city'),
        ('Postal Code', 'zip'),
        ('Email', 'email'),
        ('Phone (primary)', 'phone_number'),
        ('Status', 'membership_status'),
    ]),
    'skip_lines': 0,
    'fields_extra': OD([
        ('is_supporter', 'is_supporter'),
        ('support_level', 'support_level'),
    ]),
    'fields_flip': (),  # Reverse Sense
}

config_supporters = {
    'config_name': 'config_supporters',
    'address_fields': OD([
        ('address1', 'Street Address',),
        ('address2', 'Supplemental Address 1',),
        ('city', 'City',),
        ('zip', 'Postal Code',),
    ]),
    'date_fields': (),
    'date_format': '%Y-%m-%d',  # Membershiip date: 2014-05-17
    'doa_fields': (),
    'fieldmap': OD([
        ('Contact Name', 'name'),
        ('Do not mail', 'tag_list'),
        ('Contact ID', 'civicrm_id'),
        ('Email', 'email'),
        ('Street Address', 'address1'),
        ('Supplemental Address 1', 'address2'),
        ('City', 'city'),
        ('Postal Code', 'zip'),
        ('Phone (primary)', 'phone_number'),
        ('Mobile', 'mobile_number'),
        ('Ward', None),  # Consider: 'ward_name'
        ('Local party', 'party'),  # encode to G
    ]),
    'skip_lines': 0,
    'fields_extra': OD([
        ('is_supporter', 'is_supporter'),
        ('support_level', 'support_level'),
    ]),
    'fields_flip': (),  # Reverse Sense
}

config_volunteers = {
    'config_name': 'config_volunteers',
    'address_fields': {},
    'date_fields': (),
    'date_format': '%Y-%m-%d',  # Membershiip date: 2014-05-17
    'doa_fields': (),
    'fieldmap': OD([
        ('Contact Name', 'name'),
        ('Contact ID', 'civicrm_id'),
        ('Email', 'email'),
        ('Phone (primary)', 'phone_number'),
        ('Mobile', 'mobile_number'),
        #         ('Help: Doorknock', 'tag_list'),
        #         ('Help: Leaflet', 'tag_list'),
        #         ('Help: Make Phone Calls', 'tag_list'),
        #         ('Skills: List', 'tag_list'),
        #         ('Skills: Any Other', 'tag_list'),
        #         ('General Availability', 'tag_list'),
        #         ('Where Help From', 'tag_list'),
    ]),
    'skip_lines': 0,
    'fields_extra': OD([
        ('party', 'party'),
        ('is_supporter', 'is_supporter'),
        ('is_volunteer', 'is_volunteer'),
        ('support_level', 'support_level'),
    ]),
    'fields_flip': (),  # Reverse Sense
}

config_young_greens = {
    'config_name': 'config_young_greens',
    'address_fields': {},
    'date_fields': ('Start Date', 'End Date',),
    'date_format': '%Y-%m-%d',  # Membershiip date: 2014-05-17
    'doa_fields': (),
    'fieldmap': OD([
        ('First Name', 'first_name'),
        ('Last Name', 'last_name'),
        ('Contact ID', 'civicrm_id'),
        ('Start Date', 'started_at'),
        ('End Date', 'expires_on'),
        ('Status', 'membership_status'),
        ('Email', 'email'),
        ('Local party', 'party'),  # encode to G
    ]),
    'skip_lines': 0,
    'fields_extra': OD([
        ('Young Green', 'membership_name'),
    ]),
    'fields_flip': (),  # Reverse Sense
}


config_search = {
    'config_name': 'config_search',
    'address_fields': OD([
        ('address1', 'Street Address',),
        ('address2', 'Supplemental Address 1',),
        ('address3', 'Supplemental Address 2',),
        ('city', 'City',),
        ('zip', 'Postal Code',),
        ('country_code', 'Country',),
    ]),
    'date_fields': ('Birth Date',),
    'date_format': '%Y-%m-%d',  # Membership date: 2014-05-17
    'doa_fields': (),
    'fieldmap': OD([
        ('Internal Contact ID', 'civicrm_id'),
        ('Do Not Email', 'email opt in'),  # Reverse Sense
        ('Do Not Phone', 'mobile opt in'),  # Reverse Sense
        ('Do Not Mail', 'tag_list'),  # tag NoMail
        ('Do Not Sms', 'tag_list'),  # tag NoSMS
        ('First Name', 'first_name'),
        ('Middle Name', 'middle_name'),
        ('Last Name', 'last_name'),
        ('Individual Prefix', 'prefix'),
        ('Gender', 'sex'),
        ('Birth Date', 'DOB'),
        ('Is Deceased', 'is deceased'),
        ('Street Address', 'address1'),
        ('Supplemental Address 1', 'address2'),
        ('Supplemental Address 2', 'address3'),
        ('City', 'city'),
        ('Postal Code', 'zip'),
        ('Country', 'country_code'),  # encode
        ('Email', 'email'),
        ('Phone', 'phone_number'),
    ]),
    'skip_lines': 0,
    'fields_extra': OD([
        # Do not set  records support_level or is_supporter from SearchAll
    ]),
    'fields_flip': (# Reverse Sense
        'Do Not Email',
        'Do Not Phone',),
}
config_search_add = deepcopy(config_search)
config_search_add['config_name'] = 'config_search_add'
config_search_add['fields_extra'] = OD([
    ('is_supporter', 'is_supporter'),
    ('party_member_true', 'party_member'),
    ('support_level', 'support_level'),
])

config_search_mod = deepcopy(config_search_add)
config_search_mod['config_name'] = 'config_search_mod'

'''
config for Sheffield City Council electoral roll (register of electors) 2013
eg ga.xls
PD, ENO, Status, Title, First, Names, Initials, Surname, Suffix,
Date of Attainment, Franchise Flag, Address 1, Address 2, Address 3,
Address 4, Address 5, Address 6, Address 7
'''
config_register = {
    'config_name': 'config_register',
    'address_fields': OD([
        ('address1', 'Address 1',),
        ('address2', 'Address 2',),
        ('address3', 'Address 3',),
        ('address4', 'Address 4',),
#         ('city', 'Address 5',),
#         ('zip', 'Address 6',),
#         ('country_code', 'Address 7',),
        ('city', 'Address 6',),
        ('country_code', 'Address 9',),
        ('zip', 'Postcode',),
    ]),
    'date_fields': ('Date of Attainment',),
    #     'date_fields': ('Date Of Attainment',),
    'date_format': '%d/%m/%Y',  # _electoral_roll
    'doa_fields': ('Date of Attainment',),
    #     'doa_fields': ('Date Of Attainment',),
    'fieldmap': OD([
        ('PD', 'tag_list'),  # city_sub_district
        #         ('ENO', 'external_id'),
        ('ENO', 'state_file_id'),
        ('Status', 'tag_list'),
        ('Title', 'prefix'),
        ('First Names', 'first_name'),
        #         ('First Name', 'first_name'),
        ('Initials', 'middle_name'),
        ('Surname', 'last_name'),
        ('Suffix', 'suffix'),
        ('Date of Attainment', 'dob'),
        #         ('Date Of Attainment', 'dob'),
        ('Franchise Flag', 'tag_list'),
        ('Address 1', 'registered_address1'),
        ('Address 2', 'registered_address2'),
        ('Address 3', 'registered_address3'),
        # omitting this field did not make registered address visible
        # immediately
#         ('Address 4', 'registered_address4'),
#         ('Address 5', 'registered_city'),
#         ('Address 6', 'registered_zip'),
#         ('Address 7', 'registered_country_code'),
        ('Address 6', 'registered_city'),
        ('Postcode', 'registered_zip'),
        ('Address 9', 'registered_country_code'),
    ]),
    'skip_lines': 0,
    'fields_extra': OD([
        ('is_voter', 'is_voter'),
        ('ward_name', 'ward_name'),
        ('registered_state', 'registered_state'),
    ]),
    'fields_flip': (),  # Reverse Sense
}

config_register_update = deepcopy(config_register)
config_register_update['config_name'] = 'config_register_update'
config_register_update['date_fields'] = ('Date Of Attainment',)
config_register_update['doa_fields'] = ('Date Of Attainment',)
# for (k0, k1) in [('Date of Attainment', 'Date Of Attainment',), ('First Names', 'First Name',), ]:
d = {'Date of Attainment': 'Date Of Attainment', 'First Names': 'First Name', }
config_register_update['fieldmap'] = OD(
    (d[k] if k in d else k, v) for (k, v,) in config_register['fieldmap'].items())

config_register_city2014_postal = {
    'config_name': 'config_register_city2014_postal',
    'address_fields': OD([
        ('address1', 'Qualifying_Address_1',),
        ('address2', 'Qualifying_Address_2',),
        ('address3', 'Qualifying_Address_3',),
        ('address4', 'Qualifying_Address_4',),
        ('address4', 'Qualifying_Address_5',),
        ('address4', 'Qualifying_Address_6',),
        ('city', 'Qualifying_Address_7',),
        ('zip', 'Qualifying_Address_8',),
        ('country_code', 'Qualifying_Address_9',),
    ]),
    'date_fields': ('Election_Date',),
    'date_format': '%d/%m/%Y',  # _electoral_roll
    'doa_fields': (),
    'fieldnames': (
        ('Authority_Name', 'Area_Name',),
        ('PD_Letters', 'Alternate_PD',),
        ('Published_ENo', 'Supplementary',),
        ('Forename', 'Initials',),
        ('Surname', 'Proxy_Name',),
        ('Send_Address_1', 'Send_Address_2',),
        ('Send_Address_3', 'Send_Address_4',),
        ('Send_Address_5', 'Send_Postcode',),
        ('Qualifying_Address_1', 'Qualifying_Address_2',),
        ('Qualifying_Address_3', 'Qualifying_Address_4',),
        ('Qualifying_Address_5', 'Qualifying_Address_6',),
        ('Qualifying_Address_7', 'Qualifying_Address_8',),
        ('Qualifying_Address_9', 'Absent_Status',),
        ('Overseas_Address', 'Away_Address',),
        ('Election_Date', 'Election_Title_1',),
        ('Election_Title_2',),
    ),
    'fields_extra': OD([
        ('is_voter', 'is_voter'),
    ]),
    'fields_flip': (),  # Reverse Sense
    'skip_lines': 1,
    'tagfields': (
        ('PD_Letters',),
        ('Published_ENo',),
        ('Absent_Status',),
        ('Overseas_Address',),
        ('Away_Address',),
        ('Election_Date',),
        ('Election_Title_1',),
        ('Election_Title_2',),
    ),
}

canvassing = {
    'config_name': 'canvassing',
    'address_fields': OD([
        ('address1', 'Address 1',),
        ('address2', 'Address 2',),
        ('address3', 'Address 3',),
        ('address4', 'Address 4',),
        ('city', 'Address 5',),
        ('zip', 'Address 6',),
        ('country_code', 'Address 7',),
    ]),
    'date_fields': (),
    'date_format': '%d/%m/%Y',  # _electoral_roll
    'doa_fields': (),
    'fieldmap': OD([
        ('Polling district', 'city_sub_district'),  # city_sub_district
        ('Electoral roll number', 'external_id'),  # merge_pd_eno prepends pd to ern
        ('First name', 'first_name'),
        ('Surname', 'last_name'),
        ('Comments', 'notes'),
        ('Local campaigns', 'tag_list'),
        ('Postal Vote (last election)', 'tag_list'),
        ('Last local politics canvassed', 'support_level'),
        ('13/14 local politics', 'tag_list'),
        ('E-mail address', 'email'),
        ('Home/Work Phone', 'phone_number'),
        ('Mobile phone', 'mobile_number'),
        # ('TPS registered', 'mobile_opt_in'), #if we use this need to reverse sense

        ('Address 1', 'registered_address1'),
        ('Address 2', 'registered_address2'),
        ('Address 3', 'registered_address3'),
        # omitting this field did not make registered address visible
        # immediately
        ('Address 4', 'registered_address4'),
        ('Address 5', 'registered_city'),
        ('Postcode', 'registered_zip'),
        ('Address 7', 'registered_country_code'),
    ]),
    'skip_lines': 0,
    'fields_extra': OD([
        ('is_voter', 'is_voter'),
    ]),
    'fields_flip': (),  # Reverse Sense

}

config_nationbuilder = {
    'config_name': 'config_nationbuilder',
    'address_fields': OD([
        ('address_address1', 'address_address1',),
        ('address_address2', 'address_address2',),
        ('address_address3', 'address_address3',),
        ('address_city', 'address_city'),
        ('address_zip', 'address_zip'),
        ('address_country_code', 'address_country_code'),
    ]),
    'date_fields': (),
    'date_format': '%d/%m/%Y',  # _electoral_roll
    'doa_fields': (),
    'fieldmap': OD([
        ('nationbuilder_id', 'nationbuilder_id'),
        ('address_address1', 'address_address1',),
        ('address_address2', 'address_address2',),
        ('address_address3', 'address_address3',),
        ('address_city', 'address_city'),
        ('address_zip', 'address_zip'),
        ('address_country_code', 'address_country_code'),
        ('registered_address1', 'registered_address1',),
        ('registered_address2', 'registered_address2',),
        ('registered_address3', 'registered_address3',),
        ('registered_city', 'registered_city'),
        ('registered_zip', 'registered_zip'),
        ('registered_country_code', 'registered_country_code'),
    ]),
    'skip_lines': 0,
    'fields_extra': {},
    'fields_flip': (),  # Reverse Sense
}
config_nationbuilderNB = {
    'config_name': 'config_nationbuilderNB',
    'address_fields': OD([
        ('registered_address1', 'registered_address1',),
        ('registered_address2', 'registered_address2',),
        ('registered_address3', 'registered_address3',),
        ('registered_city', 'registered_city'),
        ('registered_zip', 'registered_zip'),
        ('registered_country_code', 'registered_country_code'),
    ]),
    'date_fields': (),
    'date_format': '%d/%m/%Y',  # _electoral_roll
    'doa_fields': (),
    'fieldmap': OD([
        ('nationbuilder_id', 'nationbuilder_id'),
        ('address_address1', 'address_address1',),
        ('address_address2', 'address_address2',),
        ('address_address3', 'address_address3',),
        ('address_city', 'address_city'),
        ('address_zip', 'address_zip'),
        ('address_country_code', 'address_country_code'),
        ('registered_address1', 'registered_address1',),
        ('registered_address2', 'registered_address2',),
        ('registered_address3', 'registered_address3',),
        ('registered_city', 'registered_city'),
        ('registered_zip', 'registered_zip'),
        ('registered_country_code', 'registered_country_code'),
    ]),
    'skip_lines': 0,
    'fields_extra': {},
    'fields_flip': (),  # Reverse Sense
}
