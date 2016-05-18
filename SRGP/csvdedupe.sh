#!/bin/bash -x
#csvdedupe config file
#Julian Briggs
#20-feb-2015
#For deduping nationbuilder export of ALL signups
#Output is single CSV with dupe clusters in top rows

#input_file=$1
input_file=/home/julian/SRGP/nationbuilder/dedupe/nationbuilder-people-export-446-447-2016-04-30.csv
outfile=${input_file/.csv/_deduped.csv/}

set -- first_name middle_name last_name phone_number mobile_number email primary_zip primary_address1 primary_address2 primary_address3
output_file=dedupe_out.csv
training_file=training.json
csvdedupe $input_file --field_names  "$@"  --output_file  $output_file   --training_file $training_file
