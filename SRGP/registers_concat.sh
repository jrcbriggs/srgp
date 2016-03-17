#!/bin/bash

#Concatentate registers
#Julian Briggs
#Dec 2015

set -e

datadir=~/SRGP/register/20160301
progdir=~/git/srgp/SRGP/
workdir=$datadir/work
registers_raw=(
PUB_AREA_W_BROOMH_01-03-2016.csv
PUB_AREA_W_CITY_01-03-2016.csv
PUB_AREA_W_CROOKE_01-03-2016.csv
PUB_AREA_W_ECCLES_01-03-2016.csv
PUB_AREA_W_GLEVAL_01-03-2016.csv
PUB_AREA_W_MANCAS_01-03-2016.csv
PUB_AREA_W_NETEDG_01-03-2016.csv
PUB_AREA_W_WALKLE_01-03-2016.csv
)

registers_ttw=$datadir/work/TTWRegisters2016-03-01.csv
registers_full=$registers_ttw.full

cd $datadir/raw
head -1 ${registers_raw[0]} > $registers_full

for r in ${registers_raw[*]}; do
	tail -n +2 $r >> $registers_full
done

#Omit Crookes (H) and 2 Manor PDs (RC, RG)
egrep -v '^"(H|RC|RG)' $registers_full > $registers_ttw

wc  ${registers_raw[*]}
wc $registers_full
wc $registers_ttw

cd $progdir
export PYTHONPATH=$progdir
#$progdir/csv_fixer.py $registers_ttw


#~ datadir=${DATADIR:-~/SRGP/register/2015_16}
#~ progdir=$(cd $(dirname $0) && pwd)
#~ workdir=$datadir/record_linking
#~ registers=(
#~ PUB_AREA_W_BROOMH_*.csv
#~ PUB_AREA_W_CITY_*.csv
#~ PUB_AREA_W_MANCAS_*.csv
#~ PUB_AREA_W_NETEDG_*.csv
#~ PUB_AREA_W_WALKLE_*.csv
#~ )

#~ registers_ttw=$workdir/${OUTPUT:-TtwAndDevWardRegisters2015-12-01.csv}

#~ mkdir -p $workdir
#~ cd $datadir
#~ head -1 ${registers[0]} > $registers_ttw
