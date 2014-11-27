'''
Created on 22 Nov 2014

@author: julian
'''
from re import compile, IGNORECASE


regexes = {
        'city_regex' : compile('^Sheffield$', IGNORECASE),
        'county_regex' : compile('^South Yorks$', IGNORECASE),
        'house_regex' : compile('Barn|Building|College|Cottage|Farm|Hall|House|Lodge|Mansion|Mill|Residence', IGNORECASE),
        'postcode_regex' : compile('^S\d\d? \d\w\w$'),
        'street_regex' : compile(r'Approach|Avenue|Bank|Bridge|Close|Common|Court|Crescent|Croft|Dell|'
                    'Drive|Gardens|Gate|Glen|Green|Grove|Head|Hill|Lane|Mews|Parade|Park|'
                    'Place|Rise|Road|Row|Square|Street|Terrace|Town|Turn|View|Walk|Way|Wharf|'
                    'Backfields|Birkendale|Castlegate|Cracknell|Cross Smithfield|Kelham Island|Shalesmoor|Summerfield|Upperthorpe|Wicker|'  # Localities
                    'Foster|Millsands|Pinsent|Redgrave|'  # blocks
                    'Other Electors',
                    IGNORECASE),
}

