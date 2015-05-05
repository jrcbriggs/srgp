#!/bin/sh
#Split GH
#Julian Briggs
#4-may-2015
#~ Broom Green
#~ Broom Walk
#~ Broomspring Close
#~ Cavendish Court
#~ Conway St
#~ Egerton Close
#~ Egerton Walk
#~ Gell St
#~ Glossop Rd
#~ Headford Green
#~ Headford Grove
#~ Headford Mews
#~ Victoria St
#~ Wilkinson St
#~ Westminster Chambers

regex_jc=',,,(Broom|Cavendish|Conway|Egerton|Gell|Glossop|Headford|Victoria|Wilkinson|Westminster)'
fn=$(basename $1 .csv)
dn=$(dirname $1)

(head -1 $1; egrep $regex_jc $1) > $dn/${fn}_Jillian.csv
egrep -v $regex_jc $1 > $dn/${fn}_Jon.csv
