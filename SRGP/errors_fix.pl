#!/usr/bin/perl -p
BEGIN{
	#@ARGV=("/home/julian/Downloads/import_srgp_846.csv")
}

s/\"//g;
s/(PG::.+)/\"$1/;
s/(INSERT INTO.+)/$1\"/;
