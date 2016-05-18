#!/bin/bash
#Concatenate files retaining single header
#Julian Briggs
#1-may-2016

head -1 -q  "${1}"
tail  -n +2 -q "${@}"
