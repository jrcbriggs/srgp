#!/bin/bash

#Concatentate registers
#Julian Briggs
#Dec 2015

set -e
set -x

datadir=~/SRGP/register/20160427
progdir=~/git/srgp/SRGP/
workdir=$datadir/work
registers_raw=(
PUB_AREA_W_BROOMH_27-04-2016.csv
PUB_AREA_W_CITY_27-04-2016.csv
PUB_AREA_W_CROOKE_27-04-2016.csv
PUB_AREA_W_ECCLES_27-04-2016.csv
PUB_AREA_W_GLEVAL_27-04-2016.csv
PUB_AREA_W_MANCAS_27-04-2016.csv
PUB_AREA_W_NETEDG_27-04-2016.csv
PUB_AREA_W_WALKLE_27-04-2016.csv
)

registers_ttw=$datadir/work/TTWRegisters2016-04-27.csv
registers_full=$registers_ttw.full

test -d ${workdir} || mkdir ${workdir}
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
