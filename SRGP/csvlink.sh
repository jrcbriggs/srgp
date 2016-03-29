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

datadir=${DATADIR:-~/SRGP/register/20160301/work}
field_names='prefix first_name middle_name last_name suffix registered_zip registered_address1 registered_address2 registered_address3'

register_old=TTWRegisters2016-03-01NB.csv
register_new=nationbuilder-people-export2016-03-15NB.csv
register_linked=TTWRegisters2016-03-01NBlinked.csv
training_file=training.json

cd $datadir
#rm -f $training_file
perl -pi.bak -e 's/,,/,_,/g;s/, ,/,_,/g;' $register_old $register_new
csvlink --field_names $field_names --output_file $register_linked --skip_training $register_old $register_new
perl -pi.bak -e 's/,_/,/g;' $register_linked