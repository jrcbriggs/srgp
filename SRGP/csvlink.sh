#!/bin/bash -x
#csvlink config file
#Julian Briggs
#15-mar-2016
#
#For linking old and new registers
#Output is single CSV: old register : linked new register
#--inner_join: Only return matches between datasets (default: False)
#csvlink --field_names $field_names --output_file $register_linked --skip_training $register_old $register_new

set -e
set -x

datadir=${DATADIR:-~/SRGP/register/20160427/link}
field_names='first_name middle_name last_name registered_zip registered_address1 registered_address2 registered_address3'

register_old=backup-nationbuilder-people-export-437-438-2016-04-29NB.csv
register_new=TTWRegisters2016-04-27NBlinkedRegOnlyAbbrev.csv
register_linked=TTWRegisters2016-04-27NBlinkedRegOnlyAbbrevLinked2.csv
training_file=training.json

cd $datadir
#rm -f $training_file
#Replace empty fields by _
perl -pi.bak -e 's/,,/,_,/g;s/,,/,_,/g;' $register_old $register_new

#Remove embedded commas from address: 
perl -pi.bak -e 's/"([^",]+),([^",]+)"/"$1$2"/g' $register_old $register_new

csvlink --field_names $field_names --output_file $register_linked $register_old $register_new
perl -pi.bak -e 's/,_/,/g;' $register_linked