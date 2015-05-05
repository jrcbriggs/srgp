#!/bin/sh
#Split csv by PD
#Julian Briggs
#3-may-2015

cd $(dirname $1)/central_ward_pds

for pd in GA GB GC GD GE GF GG GH GI; do egrep ",PD_ENO,|,$pd" $1 > CentralWard${pd}_1_2.csv; done

