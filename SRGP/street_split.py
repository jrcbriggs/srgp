#!/usr/bin/python3
#Split GH
#Julian Briggs
#4-may-2015
#~ Broom Green
#~ Broom Walk
#~ Broomspring Close
#~ Cavendish Court
#~ Conway St
#~ Egerton Close
#~ Egerton Walk
#~ Gell St
#~ Glossop Rd
#~ Headford Green
#~ Headford Grove
#~ Headford Mews
#~ Victoria St
#~ Wilkinson St
#~ Westminster Chambers

from __future__ import print_function
import fileinput
import sys
import re

regex_streets=',,,([\w\s]+),'
fn=sys.argv[1]
fn=fn.replace('.csv','')

first = 1
fh = open(fn +'_street_split.csv', 'w')

last_street=''
for line in fileinput.input():
	if first:
		print (line, end ='', file=fh)
		first =0
	else:	
		m = re.match(regex_streets, line)
		if m and m.group(0) != last_street:
			print ('', file=fh)
			last_street = m.group(0)
		print (line, end ='', file=fh)
