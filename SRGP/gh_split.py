#!/usr/bin/python3
# Split GH
# Julian Briggs
# 4-may-2015
# ~ Broom Green
# ~ Broom Walk
# ~ Broomspring Close
# ~ Cavendish Court
# ~ Conway St
# ~ Egerton Close
# ~ Egerton Walk
# ~ Gell St
# ~ Glossop Rd
# ~ Headford Green
# ~ Headford Grove
# ~ Headford Mews
# ~ Victoria St
# ~ Wilkinson St
# ~ Westminster Chambers

from __future__ import print_function

import fileinput
import re
import sys


regex_jc = ',,,(Broom|Cavendish|Conway|Egerton|Gell|Glossop|Headford|Victoria|Westminster|Wilkinson)'
fn = sys.argv[1]
fn = fn.replace('.csv', '')

fh_jillian = open(fn + '_Jillian.csv', 'w')
fh_jon = open(fn + '_Jon.csv', 'w')

lines = fileinput.input()

# Print header
line1 = next(lines)
print (line1, end='', file=fh_jillian)
print (line1, end='', file=fh_jon)

for line in lines:
    if re.match(regex_jc, line):
        print (line, end='', file=fh_jillian)
    else:
        print (line, end='', file=fh_jon)
