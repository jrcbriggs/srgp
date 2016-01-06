#!/bin/bash -x
#csvlink config file
#Julian Briggs
#16-dec-2015
#For linking old and new registers
#Output is single CSV: old register : linked new register
#--inner_join: Only return matches between datasets (default: False)
set -e
set -x

datadir=~/SRGP/register/2015_16/CentralConstituency
workdir=~/SRGP/register/2015_16/record_linking
registers_ttw=$workdir/TtwAndDevWardRegisters2015-12-01NB.csv

field_names='prefix first_name middle_name last_name suffix registered_zip registered_address1 registered_address2 registered_address3'

register_old=CentralConstituencyRegister2015-04-20NB.csv
#register_new=CentralConstituencyWardRegisters2015-12-01NB.csv
register_new=$registers_ttw
#register_linked=CentralConstituencyWardRegistersLinked2015-12-01.csv
register_linked=CentralConstituencyWardRegistersUNLinked2015-12-01.csv
#training_file=training.json

cd $datadir
#rm -f $training_file
perl -pi.bak -e 's/,,/,_,/g;s/,,/,_,/g; ' $register_old $register_new
csvlink --field_names $field_names --output_file $register_linked $register_old $register_new
#csvlink --field_names $field_names --output_file $register_linked --skip_training $register_old $register_new
