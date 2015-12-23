#!/bin/bash

#Concatentate registers
#Julian Briggs
#Dec 2015

set -e

datadir=~/SRGP/register/2015_16
progdir=~/git/srgp/SRGP/
workdir=$datadir/record_linking
registers=(
PUB_AREA_W_BROOMH_01-12-2015.csv
PUB_AREA_W_CENTRA_01-12-2015.csv
#~ PUB_AREA_W_CROOKE_01-12-2015.csv
#~ PUB_AREA_W_ECCLES_01-12-2015.csv
#~ PUB_AREA_W_GLEVAL_01-12-2015.csv
PUB_AREA_W_MANCAS_01-12-2015.csv
PUB_AREA_W_NETEDG_01-12-2015.csv
PUB_AREA_W_WALKLE_01-12-2015.csv
)

#~ registers_ttw=$workdir/TtwAndDevWardRegisters2015-12-01.csv
registers_ttw=$workdir/CentralConstituencyWardsRegister2015-12-01.csv

cd $datadir
head -1 ${registers[0]} > $registers_ttw

for r in ${registers[*]}; do
	tail -n +2 $r >> $registers_ttw
done
wc  ${registers[*]}
wc $registers_ttw

cd $progdir
export PYTHONPATH=$progdir
$progdir/csv_fixer.py $registers_ttw
