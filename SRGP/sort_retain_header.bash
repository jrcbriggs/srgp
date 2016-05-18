#!/bin/bash
#sort csv retaining header
#Julian Briggs
#22-apr-2016

(head -n 1 ${1} && tail -n +2 ${1} | sort) > ${1/.csv/sorted.csv}
