#!/bin/bash

#Concatentate registers
#Julian Briggs
#Dec 2015

set -e

datadir=${DATADIR:-~/SRGP/register/2015_16}
progdir=$(cd $(dirname $0) && pwd)
workdir=$datadir/record_linking
registers=(
PUB_AREA_W_BROOMH_*.csv
PUB_AREA_W_CITY_*.csv
PUB_AREA_W_MANCAS_*.csv
PUB_AREA_W_NETEDG_*.csv
PUB_AREA_W_WALKLE_*.csv
)

registers_ttw=$workdir/${OUTPUT:-TtwAndDevWardRegisters2015-12-01.csv}

mkdir -p $workdir
cd $datadir
head -1 ${registers[0]} > $registers_ttw

for r in ${registers[*]}; do
	tail -n +2 $r >> $registers_ttw
done
wc  ${registers[*]}
wc $registers_ttw

cd $progdir
export PYTHONPATH=$progdir
$progdir/csv_fixer2.py $registers_ttw
