#!/bin/bash

f0=20150202/nationbuilder-people-export-members-25-2015-02-03.csv
f1=20150205/nationbuilder-people-export-members-28-2015-02-04.csv

(head -1 $f0; ((tail -n +2 $f0; tail -n +2 $f1) | sort | uniq -u))

