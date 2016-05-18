#!/usr/bin/perl -p
#Abbreviate address
#Surround target with word break to avoid replacing embedded address parts
#So we don't change Adam Courtney to Adam Ctney
#Julian Briggs
#3-may-2016

BEGIN(){
	%abbrevs=(
	 'Alley'=>	'Aly',
	 'Arcade'=>	'Arc',
	 'Avenue'=>	'Ave',
	 'Boulevard'=>	'Blvd',
	 'Branch'=>	'Br',
	 'Bypass'=>	'Byp',
	 'Causeway'=>	'Cswy',
	 'Center'=>	'Ctr',
	 'Circle'=>	'Cir',
	 'Court'=>	'Ct',
	 'Crescent'=>	'Cres',
	 'Drive'=>	'Dr',
	 'Expressway'=>	'Expy',
	 'Extension'=>	'Ext',
	 'Freeway'=>	'Fwy',
	 'Gardens'=>	'Gdns',
	 'Grove'=>	'Grv',
	 'Heights'=>	'Hts',
	 'Highway'=>	'Hwy',
	 'Lane'=>	'Ln',
	 'Manor'=>	'Mnr',
	 'Place'=>	'Pl',
	 'Plaza'=>	'Plz',
	 'Point'=>	'Pt',
	 'Road'=>	'Rd',
	 'Route'=>	'Rte',
	 'Rural'=>	'R',
	 'Square'=>	'Sq',
	 'Street'=>	'St',
	 'Terrace'=>	'Ter',
	 'Trail'=>	'Trl',
	 'Turnpike'=>	'Tpke',
	 'Viaduct'=>	'Via',
	 'Vista'=>	'Vis',
	);
	$target = join('|', keys %abbrevs);
}

s/\b($target)\b/$abbrevs{$1}/eg;

