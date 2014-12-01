#!/usr/bin/python3
'''
Created on 27 Nov 2014

@author: julian
'''
from collections import OrderedDict

config_members = {
         'address_fields' : (
            'Street Address',
            'Supplemental Address 1',
            'Supplemental Address 2',
            'City',
            'Postal Code',
            'Country',
            ),
        'date_fields' : ('Start Date', 'End Date', 'Member Since',),
        'date_format' : '%Y-%m-%d',  # Membershiip date: 2014-05-17
        'doa_field' : None,
          'fieldmap':OrderedDict([
            ('Contact Name', None),
            ('Joint member name', None),
            ('Postal Greeting', None),
            ('Email Greeting', None),
            ('First Name', 'first_name'),
            ('Last Name', 'last_name'),
            ('Do not mail', 'do_not_contact'),
            ('Addressee', None),
            ('Contact ID', 'civiCRM_ID'),
            ('Membership Type', None),  # consider 'tag_list' encode 
            ('Start Date', None),
            ('End Date', 'expires_on'),
            ('Member Since', 'started_at'),
            ('Source', None),  # eg: Online Contribution: Individual Unwaged Membership
            ('Status', 'membership_name'),  # Membership status: Cancelled, Current, Deceased, Expired, New
            ('Street Address', 'address1'),
            ('Supplemental Address 1', 'address2'),
            ('Supplemental Address 2', 'address3'),
            ('City', 'city'),
            ('Postal Code', 'zip'),
            ('Country', 'country_code'),  # encode
            ('Email', 'email'),
            ('Phone (primary)', 'phone_number'),
            ('Mobile', 'mobile_number'),
            ('Ward', None),  # Consider: 'ward_name'
            ('Local authority', None),
            ('Westminster parliament constituency', None),
            ('Local party', 'party'),  # encode to G
            ('Regional party', None),
            ('Override local party', None),
#             (1, 'party_member'),  # extra
#             (1, 'support level'),  # extra
          ]),
        'skip_lines':0,
        'fields_extra':OrderedDict([
            ('is_deceased', 'is_deceased'),
            ('party_member', 'party_member'),
            ]),
        'fields_flip':(),                       #Reverse Sense
}
'''
Relationship Type    Membership    name
Party    Membership    party
Contact Name    Signup    name
Street Address    Address    address1
Supplemental Address 1    Address    address2
Supplemental Address 2    Address    address3
City    Address    city
Postal Code    Address    zip
Email    Signup    email
Phone (primary)    Signup    phone_number
Status    Signup    taglist
'''
config_officers = {
         'address_fields' : (
            'Street Address',
            'Supplemental Address 1',
            'City',
            'Postal Code',
            ),
        'date_fields' : (),
        'date_format' : '%Y-%m-%d',  # Membershiip date: 2014-05-17
        'doa_field' : None,
          'fieldmap':OrderedDict([
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
            ('Status', 'membership_name'),
          ]),
        'skip_lines':0,
        'fields_extra':OrderedDict([
            ]),
        'fields_flip':(),                       #Reverse Sense
}
'''
Contact Name    Signup    name
Do not mail    Signup    do_not_contact
Contact ID    Signup    CiviCRM_ID
Email    Signup    email
Street Address    Address    address1
Supplemental Address 1    Address    address2
City    Address    city
Postal Code    Address    zip
Phone (primary)    Signup    phone_number
Mobile    Signup    mobile_number
Ward    Precinct    ward_name
Local party    Signup    party
'''
config_supporters = {
         'address_fields' : (
            'Street Address',
            'Supplemental Address 1',
            'City',
            'Postal Code',
            ),
        'date_fields' : (),
        'date_format' : '%Y-%m-%d',  # Membershiip date: 2014-05-17
        'doa_field' : None,
          'fieldmap':OrderedDict([
            ('Contact Name', 'name'),
            ('Do not mail', 'do_not_contact'),
            ('Contact ID', 'civiCRM_ID'),
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
        'skip_lines':0,
        'fields_extra':OrderedDict([
            ]),
        'fields_flip':(),                       #Reverse Sense
}
'''
Contact Name    Signup    name
Contact ID    Signup    CiviCRM_ID
Email    Signup    email
Phone (primary)    Signup    phone_number
Mobile    Signup    mobile_number
Ward    Precinct    ward_name
Local party    Signup    party
Action: Display a Poster    Signup    taglist
Help: Doorknock    Signup    taglist
Help: Leaflet    Signup    taglist
Help: Make Phone Calls    Signup    taglist
Skills: List    Signup    taglist
Skills: Any Other    Signup    taglist
General Availability    Signup    taglist
Where Help From    Signup    taglist
'''
config_volunteers = {
         'address_fields' : (
            ),
        'date_fields' : (),
        'date_format' : '%Y-%m-%d',  # Membershiip date: 2014-05-17
        'doa_field' : None,
          'fieldmap':OrderedDict([
            ('Contact Name', 'name'),
            ('Contact ID', 'civiCRM_ID'),
            ('Email', 'email'),
            ('Phone (primary)', 'phone_number'),
            ('Mobile', 'mobile_number'),
            ('Help: Doorknock', 'taglist'),  
            ('Help: Leaflet', 'taglist'),  
            ('Help: Make Phone Calls', 'taglist'),  
            ('Skills: List', 'taglist'),  
            ('Skills: Any Other', 'taglist'),  
            ('General Availability', 'taglist'),  
            ('Where Help From', 'taglist'),  
          ]),
        'skip_lines':0,
        'fields_extra':OrderedDict([
            ]),
        'fields_flip':(),                       #Reverse Sense
}

'''
config for Sheffield City Council electoral roll (register of electors) 2013 
eg ga.xls

PD, ENO, Status, Title, First, Names, Initials, Surname, Suffix, Date of Attainment, Franchise Flag, Address 1, Address 2, Address 3, Address 4, Address 5, Address 6, Address 7

'''
config_register = {
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
        'date_format' : '%d/%m/%Y',  # _electoral_roll
        'doa_field' : 'Date of Attainment',
        'fieldmap':OrderedDict([
                ('PD', 'tag_list'),  # city_sub_district
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
                ('Address 4', 'registered_address4'),  # omitting this field did not make registered address visible immediately
                ('Address 5', 'registered_city'),
                ('Address 6', 'registered_zip'),
                ('Address 7', 'registered_country_code'),
                ]),
        'skip_lines':1,
        'fields_extra':OrderedDict([
            ('is_voter', 'is_voter'),
            ]),
        'fields_flip':(),                       #Reverse Sense
    }

config_civi_search_all={
         'address_fields' : (
            'Street Address',
            'Supplemental Address 1',
            'Supplemental Address 2',
            'City',
            'Postal Code',
            'Country',
            ),
        'date_fields' : ('Birth Date',),
        'date_format' : '%Y-%m-%d',  # Membership date: 2014-05-17
        'doa_field' : None,
          'fieldmap':OrderedDict([
            ('Internal Contact ID', 'civiCRM_ID'),
            ('Do Not Email', 'email opt in'), #Reverse Sense
            ('Do Not Phone', 'mobile opt in'), #Reverse Sense
            ('Do Not Mail', 'do_not_contact'), #tag NoMail
            ('Do Not Sms', 'tag_list'), #tag NoSMS
            ('First Name', 'first_name'),
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
        'skip_lines':0,
        'fields_extra':OrderedDict([
#             ('party', 'party'),#Undefined in civi search all
#             ('party_member', 'party_member'), #Undefined in civi search all
#             ('support level', 'support level'),#Undefined in civi search all
            ]),
        'fields_flip':(                       #Reverse Sense
                      'Do Not Mail',
                      'Do Not Phone',),
}
