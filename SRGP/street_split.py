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


regex_streets = ',,,([\w\s]+),'
fn = sys.argv[1]
fn = fn.replace('.csv', '_street_split.csv')

fh = open(fn, 'w')

lines = fileinput.input()

# Print header
line1 = next(lines)
print (line1, end='', file=fh)

last_street = ''
for line in lines:
    m = re.match(regex_streets, line)
    if m and m.group(0) != last_street:
        print ('', file=fh)
        last_street = m.group(0)
    print (line, end='', file=fh)
