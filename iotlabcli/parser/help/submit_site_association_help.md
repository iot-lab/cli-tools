Site associations
=================

Site associations describe site specific configurations.
The argument can be specified multiple times.

    --site-association <site><,site>,<assocname=assocvalue><,assoc=val>

Currently supported associations is 'script'.


Examples
--------

Same script and for two sites

    --site-association grenoble,lille,script=experient.sh
