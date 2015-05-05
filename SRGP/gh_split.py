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

regex_jc=',,,(Broom|Cavendish|Conway|Egerton|Gell|Glossop|Headford|Victoria|Wilkinson|Westminster)'
fn=sys.argv[1]
fn=fn.replace('.csv','')

first = 1
fh_jillian = open(fn +'_Jillian.csv', 'w')
fh_jon    = open(fn +'_Jon.csv', 'w')

for line in fileinput.input():
	if first:
		print (line, end ='', file=fh_jillian)
		print (line, end ='', file=fh_jon)
		first =0
		
	if re.match(regex_jc, line):
		print (line, end ='', file=fh_jillian)
	else:
		print (line, end ='', file=fh_jon)
