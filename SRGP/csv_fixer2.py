#!/usr/bin/python3
'''
Created on 1 Nov 2014

@author: julian
'''
from csv import DictReader, DictWriter
from os import path
from re import compile, IGNORECASE, search
from sys import argv
from logging import warning

regexes = {
    'block': compile(r'^()$', IGNORECASE),  # Fairleigh|Foster|Hartshead|Pinsent|Redgrave|The Circle
    'city': compile('^(Barnsley|Hathersage|Mexborough|Rotherham|Sheffield|Stocksbridge|Worksop)$', IGNORECASE),
    'county': compile('^South Yorks$', IGNORECASE),
    'house': compile('Barn|Building|College|Cottage|Farm|Hall|House|'
                     'Lodge|Mansion|Mill|Residence', IGNORECASE),
    'locality': compile(r'^(Abbeydale|Arbourthorne|Aston|Aughton|Barnsley|Basegreen|Bate Green|Beauchief|Beighton|'
                        'Bents Green|Bingley Seat|Birley|Bradway|Bramley|Brampton|Brincliffe|Brinsworth|Broom|Broomhall|'
                        'Broomhill|Burncross|Burngreave|Carterknowle|Catcliffe|Chapeltown|Christchurch|'
                        'City Centre|Clent|Clifton|Crookes|Crookesmoor|Crooks|Crosspool|'
                        'Dalton|Darnall|Deepcar|Dinnington|Dore|East Dene|East Herringthorpe|'
                        'Ecclesall|Ecclesfield|Firshill|Firth Park|Frecheville|Fulwood|Gleadless|Greasbrough|'
                        'Greenhill|Grenoside|Hackenthorpe|Halfway|Hallam Rock|Handsworth|Hathersage|'
                        'Heeley|Hellaby|Herdings|Herringthorpe|Highfield|High Green|Hillsborough|'
                        'Hooton Levitt|Hunters Bar|Intake|Jordanthrope|Kimberworth|Kiveton Park|Loxley|Malin Bridge|Maltby|'
                        'Meersbrook|Mexborough|Midhopestones|Millhouses|Mosborough|Nether Edge|Netheredge|'
                        'Nethergreen|Nether Green|Norfolk Park|Norton|Norton Lees|Nottingham|Oughtibridge|'
                        'Owlthorpe|Parkgate|Park Hill|Pitsmoor|Ranmoor|Rawmarsh|Rivelin|Shalesmoor|'
                        'Sharrow|Shiregreen|Sothall|Stannington|Stocksbridge|Storrs|Sunnyside|'
                        'Swallownest|Swinton|Thorpe Hesley|Thurcroft|Todwick|Totley|Totley Rise|'
                        'Upperthorpe|Wales Bar|Walkley|Waterthorpe|Wath upon Dearne|Wath-upon-Dearne|'
                        'Well Court|Wellgate|Wentworth|West Melton|Whiston|Wickersley|Wincobank|Wingfield|'
                        'Woodend|Woodhouse|Woodseats|Woodsetts|Worksop|Worrall)$', IGNORECASE),
    'postcode': compile('^S\d\d? ?\d\w\w$', IGNORECASE),
    'street': compile(r'\b(Anglo Works|Approach|Ashgrove|Ave|Avenue|Bakers Yard|Bank|Brg|Bridge|'
                      'Brookside|Cir|Close|Common|Common Side|Crookes|Crossways|Court|Cres|Crescent|Croft|Ct|Dell|'
                      'Dl|Dr|Drive|Edward Street Flats|Endcliffe Village|Fields|Gdns|Gardens|Gate|Glade|Glen|Gr|Green|'
                      'Grove|Hartshead|Head|Hl|Hill|Ln|Lane|Mdws|Mews|Moorfields Flats|Mt|Parade|Park|Park Centre|Pl|Place|Rd|Rise|'
                      'Road|Road North|Road South|Row|Sq|Square|St|Street|Street South|Ter|Terrace|The Gln|Town|Turn|View|Vw|Victoria Villas|Waingate|'
                      'Walk|Way|West Bar|Wharf|'
                      'Backfields|Birkendale|Castlegate|Cracknell|'
                      'Cross Smithfield|Kelham Island|'
                      'Summerfield|Upperthorpe|Wicker|Woodcliffe|The Lawns|The Nook|'
                      'Fairleigh|Foster|Hartshead|Millsands|Pinsent|Redgrave|The Circle|'  # blocks
                      'Midhopecourt|'
                      'Other Electors)$', IGNORECASE),
    'street_number': compile(r'^(Above|Back|Back Of|Bk|First Floor|Flat Above|Flat Over|Ground Floor|Over|Rear|Rear Of)?[\s\d/-]+\w?$', IGNORECASE),
}

class AddressHandler():
    
    address = None
    
    @classmethod
    def is_city(cls, v):  # is v a city
        return regexes['city'].search(v)

    @classmethod
    def is_locality(cls, v):  # is v a locality (eg Broomhall)
        return regexes['locality'].search(v)

    @classmethod
    def is_postcode(cls, v):  # is v a postcode
        return regexes['postcode'].search(v)

    @classmethod
    def is_street(cls, v):  # is v a street
        return regexes['street'].search(v)
    
    @classmethod
    def is_street_number(cls, v):  # is v a street
        return regexes['street_number'].search(v)
    
   
    @classmethod
    def address_get(cls, key, **kwargs):
        '''Get address1, address2, address3,
        Caches address (all parts) for use by subsequent calls for address parts
        Must call once for each row and in that order
        '''
        if key == 'address1':
            cls.address = cls.address_get_helper(**kwargs)
        return cls.address.get(key)
        
    @classmethod
    def address_get_helper(cls, **kwargs):
        address = {}
        street_number = ''

        # Scan each kwarg value, from last (eg postcode) to first (eg Flat 1) in turn for NB address fields
        for k in sorted(kwargs.keys(), reverse=True):
            v = kwargs[k].strip()
            # Skip null values
            if not v:
                continue
            elif cls.is_postcode(v) and not address.get('postcode'):
                address['postcode'] = v.upper()
            elif cls.is_city(v) and not address.get('city'):
                address['city'] = v
            elif cls.is_locality(v) and not address.get('address3'):
                address['address3'] = v
            elif cls.is_street(v) and not address.get('address1'):
                address['address1'] = v
            elif cls.is_street_number(v) and not street_number:
                street_number = v
            else:
                address['address2'] = (v + ' ' + address.get('address2', '')).strip()
                
        address['address1'] = ' '.join([street_number, address.get('address1', '')]).strip()
        address['city'] = address.get('city', '').capitalize()
        
        return address  

class Canvass():
    @classmethod
    def background_merge(cls, notes='', comments=''):
        return ' '.join([notes, comments])

    @classmethod
    def fix_address1(cls, housename='', street_number='', street_name=''):
        return ' '.join([housename, street_number, street_name]).strip()

    @classmethod
    def fix_address2(cls, block_name=''):
        return block_name

class CsvFixer(object):

    '''The top level class.
    Read csv data file into a table
    Fix the data in table
    Create new table: with NB table column headings
    Write the table to a new csv file for import to NB.
    '''
    def fix_csv(self, pathname, config, config_name, filereader, filewriter):
        
        # Get the basename
        basename = path.basename(pathname).replace('.csv', '').replace('-','_') #NB complains about - in tags sometimes

        # Read csv data file into a table
        table0 = filereader(pathname)

        # Fix the data in table
        table1 = TableFixer(config=config, config_name=config_name).fix_table(table0)
        
        # Append basename to tags
        for row1 in table1:
            # Replace - by _ in basename: NB throws error if tag list contains just a single tag containing a minus sign -
            basename.replace('-', '_') 
            tag_list = row1.get('tag_list')
            row1['tag_list'] = tag_list + ',' + basename if tag_list else basename

        # Write the table to a new csv file for import to NB.
        pathname_new = pathname.replace('.csv', 'NB.csv')
        fieldnames = [k for (k,unused) in config]
        # Enusre tag_list is in keys
        if not 'tag_list' in fieldnames:
            fieldnames.append('tag_list')
        
        filewriter(table1, pathname_new, fieldnames)
        return pathname_new

class FileHandler(object):

    '''Handle reading and writing files, including the config file which is loaded as a Python module.
    '''

    def csv_read(self, pathname):
        '''Read csv file (excluding 1st row) into self.table.
        Populate self.fieldnames with fields from 1st row in order'''
        with open(pathname, 'r', encoding='utf-8', errors='ignore') as fh:
            return self.csv_read_fh(fh)

    def csv_read_fh(self, fh):
        '''Read csv file (excluding 1st row) into self.table.
        Populate self.fieldnames with fields from 1st row in order'''
        dr = DictReader(fh)
        return [row for row in dr]

    def csv_write(self, table1, pathname, fieldnames1):
        with open(pathname, 'w') as fh:
            self. csv_write_fh(table1, fh, fieldnames1)

    def csv_write_fh(self, table1, fh, fieldnames1):
        dw = DictWriter(fh, fieldnames1)
        dw.writeheader()
        dw.writerows(table1)

class Generic(object):
    
    @classmethod
    def doa2dob(cls, doa=None):
        '''Convert date of attainment (ie reach 18years old) to DoB in US format: mm/dd/yyyy.
            Use after converting to NB date format.
            yoa: year of attainment, yob: year of birth'''
        if doa:
            (day, month, yoa) = doa.split('/')
            yob = str(int(yoa) - 18)
            return '/'.join([month, day, yob])
        else:
            return doa

    @classmethod
    def fix_date(cls, date=None):
        '''Convert date from UK format (dd/mm/yyyy) to US format: mm/dd/yyyy.
        '''
        if date:
            (day, month, year) = date.split('/')
            return '/'.join([month, day, year])
        else:
            return date

    @classmethod
    def state_get(cls):
        return 'Sheffield'
 
    @classmethod
    def tags_add(cls, tag_map, **kwargs):
        '''For tag_str0 in tag_lists0 (values in kwargs), eg: 'ResidentsParking,StreetsAhead','Ben, Bins', '','', 'Vote14', 'Vote12'}
            Split into tag0 elements in tag_list0:
              Strip (leading and trailing) white space from tag0
              Convert tag0 tag1 elements in tag_list1
              Merge into tag_list1 removing empty tags ('')
              Sort
              Convert to string tag_str1
            Return tags_str1
        '''
        tag_lists0 = kwargs.values()
        tag_lists1 = [cls.tags_split(tag_map, tag_str0) for tag_str0 in tag_lists0]
        tag_str1 = ','.join(sorted(set([tag for tag_list in tag_lists1 for tag in tag_list if tag != '']))) #set to remove duplicates
        return tag_str1


    @classmethod
    def tags_split(cls, tag_map, tag_str0):
        '''For a single tag_str0:
              Split into tag0 elements in tag_list0
              Strip (leading and trailing) white space from tag0
              Convert tag0 to tag1 elements in tag_list1
           Return tag_list as string, eg: 'ResidentsParking,StreetsAhead'
        '''
        tag_list0 = tag_str0.split(',')  # 'stdt,ResPark' -> ['stdt','ResPark']
        tag_list1 = []
        for tag0 in tag_list0:
            try:
                tag_list1.append(tag_map[tag0.strip()])
            except:
                warning('key {} not found in tagmap {}'.format(tag0, tag_map)) 
        return tag_list1

    @classmethod
    def value_get(cls, value):
        return value
 
class Member():
    
    @classmethod
    def fix_date(cls, date=None):
        '''Convert date from UK format (dd/mm/yyyy) to US format: mm/dd/yyyy.
        '''
        if date:
            (year, month, day) = date.split('-')
            return '/'.join([month, day, year])
        else:
            return date

    @classmethod
    def get_party(cls, party_map, status=None):
        return party_map[status]
     
    @classmethod
    def get_party_green(cls,):
        '''Return 'G'. Used for supporters and volunteers (civi has no status for them)'''
        return 'G'
     
    @classmethod
    def get_party_member(cls, party_member_map, status=None):
        '''Party member flag for is currently a member: 
        False for: Cancelled, Deceased, Expired 
        True for: Current, Grace, New
        (Alternatively one could argue that a cancelled member is still a member, so True.)
        '''
        return party_member_map[status]
    
    @classmethod
    def get_status(cls, party_status_map, status=None):
        '''NB: active, canceled, expired, grace period
        '''
        return party_status_map[status]
    @classmethod
    def get_support_level(cls, support_level_map, status=None):
        '''Support level: Cancelled, Deceased, Expired
        Unclear what level to set for: cancelled, expired 
        TODO uncomment after matching to original csv
        '''
        return support_level_map[status]
    
   
    @classmethod
    def is_deceased(cls, status=None):
        return status == 'Deceased'
     
class Register(object):

    @classmethod
    def city_get(cls):
        '''Naive method, just returns Sheffield. 
        OK for Register and Canvassing.
         AddressHandler.city_get OK for members etc and Postal
        '''
        return 'Sheffield'
    
    @classmethod
    def country_code_get(cls):
        return 'GB'
    
    @classmethod
    def ward_get(cls, ward_lookup, pd=None):
        return ward_lookup[pd[0]]

class TableFixer(object):
    
    def __init__(self, config=None, config_name=None):
        self.config = config
        self.config_name = config_name

    def fix_table(self, table0):
        '''Returns new table given old table
        '''
        return [self.fix_row(row0) for row0 in table0]

    def fix_row(self, row0):
        '''Creates new row from old row
        '''
        return {fieldname1: self.fix_field(row0, arg0)
                    for (fieldname1, arg0) in self.config}

    def fix_field(self, row0, arg0):
        '''Creates new field from old field(s)
        row0 ={k0:v0,...}
        row1 ={k1:v1,...}
        field1 is in row1
        Replaced list comp by for loop to allow exception handling
        was: kwargs = {k: row0[v].strip() for (k, v) in kwargs0.items()}
        '''
        try:
            if arg0 == None:
                return None
            elif isinstance(arg0, str):
                return row0.get(arg0).strip()
            elif isinstance(arg0, tuple):
                (func, args, kwargs0) = arg0
                if callable(func):
                    kwargs = {}
                    for (k1, k0) in kwargs0.items():
                        try:
                            kwargs[k1] = row0[k0].strip() 
                        except(KeyError):
                            warning('In {} in config file, check config row {}, header {} not in row0:{}'.format(self.config_name, k1, k0, row0))
                    return func(*args, **kwargs)
            raise TypeError('TableFixer.fix_field: expected str or (func, kwargs). Got:{}'.format(arg0))
        except (AttributeError, IndexError, KeyError, TypeError) as e:
            e.args += ('fix_field', 'row0:', row0, 'arg0:', arg0,)
            raise

class Volunteer():
    
    @classmethod
    def tag_add_volunteer(cls, stem, tags_map, **kwargs):
#         kwargs['volunteer_at'] = kwargs['volunteer_at'].replace('  ', ',')
#         return Generic.tags_add(tags_map, **kwargs)
        return ','.join([stem+ v for v in Generic.tags_add(tags_map, **kwargs).split(',')])
    
class Voter(object):
    '''Common to register and canvassing
    '''
    @classmethod
    def merge_pd_eno(cls, pd=None, eno=None):
        '''Merged PD & zero padded eno,
        takes: pd old and eno old.eg:
        {'pd':'polldist', 'eno':'elect no',} -> {'statefile_id':EA0012',}
        '''
        eno_padded = None
        try:
            pd = pd.lstrip('!')
            eno_padded = cls.eno_pad(eno)
            return pd + eno_padded
        except (TypeError) as e:
            e.args += ('pd:{} eno:{} eno_padded:{}'.format(pd, eno, eno_padded),)
            raise

    @classmethod
    def eno_pad(cls, eno):
        return '%04d' % (int(eno),)

    @classmethod
    def fix_party(cls, party_map, party=None):
        return party_map[party]

    @classmethod
    def fix_support_level(cls, support_level_map, support_level=None):
        return support_level_map[support_level]

    @classmethod
    def tags_add_voter(cls, tag_map_voter, **kwargs):
        '''Eg kwargs = {'PD':'ED', 'status':'K', 'franchise':'E'
        '''
        pd = kwargs['PD']
        tag_map_voter.update({pd:pd, })
        return ','.join(sorted(['{}={}'.format(k, tag_map_voter[v]) for (k, v) in kwargs.items() if v]))

class Main():

    def __init__(self, config_lookup=None, filereader=None, filewriter=None):
        '''Create filereader and fielwriter unless given in kwargs
        '''
        self.config_lookup = config_lookup
        self.fh = FileHandler()
        self.filereader = filereader or self.fh.csv_read
        self.filewriter = filereader or self.fh.csv_write
        self.csv_fixer = CsvFixer()

    def main(self, filenames):
        '''Fix one or more files for input to NB
        Lookup config using part of filename in order
        '''
        for filename in filenames:  # skip scriptname in argv[0]
            # Find config varname to match csv filename
            for (name, config, config_name) in self.config_lookup:
                if search(name, filename):
                    print('Using: {}'.format(config_name))
                    self.fix_csv(filename, config, config_name)
                    break
            else:
                raise AttributeError('config not found for filename:{}'.format(filename))

    def fix_csv(self, filename, config, config_name):
        filename_new = self.csv_fixer.fix_csv(filename, config, config_name, filereader=self.filereader, filewriter=self.filewriter)
        print(filename_new)

if __name__ == '__main__':
    from configurations2 import config_lookup
    argv += [
#             '/home/julian/SRGP/canvassing/2014_15/broomhill/csv/BroomhillCanvassData2015-03EA-H.csv',
#             '/home/julian/SRGP/register/2015_16/CentralConstituency/CentralConstituencyRegisterUpdate2016-02-01.csv',
#             '/home/julian/SRGP/register/2015_16/CentralConstituency/CentralConstituencyWardRegisters2015-12-01.csv',
#             '/home/julian/SRGP/civi/20160217/SRGP_MembersAll_20160217-1738.csv',
#             '/home/julian/SRGP/civi/20160217/SRGP_SupportersAll_20160217-2031.csv',
#             '/home/julian/SRGP/civi/20160217/SRGP_VolunteersAll_20160217-2039.csv',
#             '/home/julian/SRGP/civi/20160217/SRGP_YoungGreens_20160217-2055.csv',
            ]
    Main(config_lookup=config_lookup).main(argv[1:])
    print('Done')
      
