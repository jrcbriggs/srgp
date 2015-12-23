#!/bin/bash -x
#csvlink config file
#Julian Briggs
#16-dec-2015
#For linking old and new registers
#Output is single CSV: old register : linked new register
#--inner_join: Only return matches between datasets (default: False)
set -x

datadir=~/SRGP/register/2015_16/CentralConstituency
field_names='prefix first_name middle_name last_name suffix registered_zip registered_address1 registered_address2 registered_address3'

register_old=CentralConstituencyRegister2015-04-20NB.csv
register_new=CentralConstituencyWardsRegister2015-12-01NB.csv
register_linked=CentralConstituencyWardsRegisterLinked2015-12-01.csv
training_file=training_file.json

cd $datadir
#rm -f $training_file
perl -pi.bak -e 's/,,/,_,/g;' $register_old $register_new
perl -pi.bak -e 's/,,/,_,/g;' $register_old $register_new #do twice to replace overlapping ,,,
csvlink --inner_join --field_names $field_names --output_file $register_linked $register_old $register_new
