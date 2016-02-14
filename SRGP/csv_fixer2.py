#!/usr/bin/python3
'''
Created on 1 Nov 2014

@author: julian
'''
from csv import DictReader, DictWriter
from re import compile, IGNORECASE, search
from sys import argv

regexes = {
    'city': compile('^(Rotherham|Sheffield|Stocksbridge)$', IGNORECASE),
    'county': compile('^South Yorks$', IGNORECASE),
    'house': compile('Barn|Building|College|Cottage|Farm|Hall|House|'
                     'Lodge|Mansion|Mill|Residence', IGNORECASE),
    'postcode': compile('^S\d\d? \d\w\w$'),
    'locality': compile(r'^(Arbourthorne|Aston|Aughton|Barnsley|Basegreen|Beauchief|Beighton|'
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
                        'Owlthorpe|Parkgate|Park Hill|Pitsmoor|Rawmarsh|Rivelin|Shalesmoor|'
                        'Sharrow|Shiregreen|Sothall|Stannington|Sunnyside|'
                        'Swallownest|Swinton|Thorpe Hesley|Thurcroft|Todwick|Totley|Totley Rise|'
                        'Upperthorpe|Wales Bar|Walkley|Waterthorpe|Wath upon Dearne|Wath-upon-Dearne|'
                        'Well Court|Wellgate|Wentworth|Whiston|Wickersley|Wincobank|Wingfield|'
                        'Woodhouse|Woodseats|Woodsetts|Worksop|Worrall)$', IGNORECASE),
    'street': compile(r'\b(Anglo Works|Approach|Ashgrove|Ave|Avenue|Bakers Yard|Bank|Brg|Bridge|'
                      'Brookside|Cir|Close|Common|Common Side|Crossways|Court|Cres|Crescent|Croft|Ct|Dell|'
                      'Dl|Dr|Drive|Edward Street Flats|Endcliffe Village|Fields|Gdns|Gardens|Gate|Glade|Glen|Gr|Green|'
                      'Grove|Hartshead|Head|Hl|Hill|Ln|Lane|Mdws|Mews|Moorfields Flats|Mt|Parade|Park|Park Centre|Pl|Place|Rd|Rise|'
                      'Road|Road North|Road South|Row|Sq|Square|St|Street|Street South|Ter|Terrace|The Gln|Town|Turn|View|Vw|Victoria Villas|Waingate|'
                      'Walk|Way|West Bar|Wharf|'
                      'Backfields|Birkendale|Castlegate|Cracknell|'
                      'Cross Smithfield|Kelham Island|'
                      'Summerfield|Upperthorpe|Wicker|Woodcliffe|The Lawns|The Nook|'
                      'Fairleigh|Foster|Hartshead|Millsands|Pinsent|Redgrave|The Circle|'  # blocks
                      'Other Electors)$', IGNORECASE),
     'block': compile(r'^()$', IGNORECASE),  # Fairleigh|Foster|Hartshead|Pinsent|Redgrave|The Circle
    'street_number': compile(r'^(Above|Back|Back Of|Bk|First Floor|Flat Above|Flat Over|Ground Floor|Over|Rear|Rear Of)?[\s\d/-]+\w?$'),
}

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

class CsvFixer(object):

    '''The top level class.
    Read csv data file into a table
    Fix the data in table
    Create new table: with NB table column headings
    Write the table to a new csv file for import to NB.
    '''
    def fix_csv(self, pathname, config, filereader, filewriter):

        # Read csv data file into a table
        table0 = filereader(pathname)

        # Fix the data in table
        table1 = TableFixer(config=config).fix_table(table0)

        # Write the table to a new csv file for import to NB.
        pathname_new = pathname.replace('.csv', 'NB.csv')
        fieldnames = config.keys()
        filewriter(table1, pathname_new, fieldnames)
        return pathname_new

class TableFixer(object):

    def __init__(self, config=None):
        self.config = config

    def fix_table(self, table0):
        '''Returns new table given old table
        '''
        try:
            return [self.fix_row(row0) for row0 in table0]
        except (IndexError, KeyError, TypeError) as e:
            e.args += ('config:', self.config,)
            raise

    def fix_row(self, row0):
        '''Creates new row from old row
        '''
        try:
            return {fieldname1: self.fix_field(row0, arg0)
                        for (fieldname1, arg0) in self.config.items()}
        except (IndexError, KeyError, TypeError) as e:
            e.args += ('row0:', row0)
            raise

    def fix_field(self, row0, arg0):
        '''Creates new field from old field(s)
        '''
        try:
            if arg0 == None:
                return None
            elif isinstance(arg0, str):
                return row0.get(arg0).strip()
            elif isinstance(arg0, tuple):
                (func, args, kwargs0) = arg0
                if callable(func):
                    kwargs = {k: row0[v].strip() for (k, v) in kwargs0.items()}
                    return func(*args, **kwargs)
            raise TypeError('TableFixer.fix_field: expected str or (func, kwargs). Got:{}'.format(arg0))
        except (AttributeError, IndexError, KeyError, TypeError) as e:
            e.args += ('fix_field', 'row0:', row0, 'arg0:', arg0,)
            raise

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
        try:
            tag_lists0 = kwargs.values()
            tag_lists1 = [cls.tags_split(tag_map, tag_str0) for tag_str0 in tag_lists0]
            tag_str1 = ','.join(sorted([tag for tag_list in tag_lists1 for tag in tag_list if tag != '']))
            return tag_str1
        except (KeyError) as e:
            e.args += ('tags_add', 'tag_map:', tag_map, 'kwargs:', kwargs,)
            raise

    @classmethod
    def tags_split(cls, tag_map, tag_str0):
        '''For a single tag_str0:
              Split into tag0 elements in tag_list0
              Strip (leading and trailing) white space from tag0
              Convert tag0 to tag1 elements in tag_list1
           Return tag_list as string, eg: 'ResidentsParking,StreetsAhead'
        '''
        try:
            tag_list0 = tag_str0.split(',')  # 'stdt,ResPark' -> ['stdt','ResPark']
            tag_list1 = [tag_map[tag0.strip()] for tag0 in tag_list0]  # ['Student','ResidentsParking']
            return tag_list1
        except (KeyError) as e:
            e.args += ('tags_split', 'tag_map:', tag_map, 'tag_str0:', tag_str0,)
            raise

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

class Canvass(Generic):
    @classmethod
    def background_merge(cls, notes='', comments=''):
        return ' '.join([notes, comments])

    @classmethod
    def fix_address1(cls, housename='', street_number='', street_name=''):
        return ' '.join([housename, street_number, street_name]).strip()

    @classmethod
    def fix_address2(cls, block_name=''):
        return block_name

class Register(object):

    @classmethod
    def tags_add_voter(cls, tag_map_voter, **kwargs):
        '''Eg kwargs = {'PD':'ED', 'status':'K', 'franchise':'E'
        '''
        pd = kwargs['PD']
        tag_map_voter.update({pd:pd, })
        return ','.join(sorted(['{}={}'.format(k, tag_map_voter[v]) for (k, v) in kwargs.items() if v]))

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

class AddressHandler():
    
#     @classmethod
#     def is_block(cls, v):
#         return regexes['block'].search(v)
    
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
    def address_split(cls, **kwargs):
        address = {}
#         block_needed=True
        street_needed = True
        street_number_needed = True

        # Scan each kwarg value, from last (eg postcode) to first (eg Flat 1) in turn for NB address fields
        for k in sorted(kwargs.keys(), reverse=True):
            v = kwargs[k].strip()
            # Skip null values
            if not v:
                continue
            # Skip postcode, city, locality
            if cls.is_postcode(v) or cls.is_city(v) or cls.is_locality(v):
                continue
#             if cls.is_block(v) and block_needed:
#                 block_needed=False
#                 address['address3'] = v
            if cls.is_street(v) and street_needed:
                street_needed = False
                address['address1'] = v
            elif cls.is_street_number(v) and street_number_needed:
                street_number_needed = False
                address['address1'] = (v + ' ' + address.get('address1', '')).strip()
            else:
                address['address2'] = (v + ' ' + address.get('address2', '')).strip()
                
        # Return
        return address

    @classmethod
    def address1_get(cls, **kwargs):
        '''Get street address1 (NB sorts canvassing sheets on this)'''
        return cls.address_split(**kwargs).get('address1')     
        
    @classmethod
    def address2_get(cls, **kwargs):
        '''Get street address2. Eg Flat 1'''
        return cls.address_split(**kwargs).get('address2')     
        
    @classmethod
    def address3_get(cls, **kwargs):
        '''Get street address3. Block, eg Mill Cracknell'''
        return cls.address_split(**kwargs).get('address3')     

    @classmethod
    def city_get(cls, **kwargs):
        for v in kwargs.values():
            if cls.is_city(v):
                return v
        return None     

    @classmethod
    def postcode_get(cls, **kwargs):
        for v in kwargs.values():
            if cls.is_postcode(v):
                return v
        return None     

class Main():

    def __init__(self, config_lookup=None, filereader=None, filewriter=None):
        '''Create filereader and fielwriter unless given in kwargs
        '''
        self.fh = FileHandler()
        self.filereader = filereader or self.fh.csv_read
        self.filewriter = filereader or self.fh.csv_write
        self.config_lookup = config_lookup or [
                         ('BroomhillCanvassData', config_rl),
                         ('CentralConstituencyRegister', config_register),
                         ('CentralConstituencyWardRegisters', config_register),
                         ]
        self.csv_fixer = CsvFixer()

    def main(self, filenames):
        '''Fix one or more files for input to NB
        Lookup config using part of filename in order
        '''
        for filename in filenames:  # skip scriptname in argv[0]
            # Find config varname to match csv filename
            for (name , config) in self.config_lookup:
                if search(name, filename):
                    print('Using config: {}'.format(config.get('config_name')))
                    del config['config_name']
                    self.fix_csv(filename, config)
                    break
            else:
                raise AttributeError('config not found for filename:{}'.format(filename))

    def fix_csv(self, filename, config):
        filename_new = self.csv_fixer.fix_csv(filename, config, filereader=self.filereader, filewriter=self.filewriter)
        print(filename_new)

if __name__ == '__main__':
    from configurations2 import config_rl, config_register
#     argv.append('/home/julian/SRGP/canvassing/2014_15/broomhill/csv/BroomhillCanvassData2015-03EA-H.csv')
#     argv.append('/home/julian/SRGP/register/2015_16/CentralConstituency/CentralConstituencyRegisterUpdate2016-02-01.csv')
    argv.append('/home/julian/SRGP/register/2015_16/CentralConstituency/CentralConstituencyWardRegisters2015-12-01.csv')
    Main().main(argv[1:])
    
