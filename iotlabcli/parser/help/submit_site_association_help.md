Site associations
=================

Site associations describe site specific configurations.
The argument can be specified multiple times.

    --site-association <site><,site>,<assocname=assocvalue><,assoc=val>

Currently supported associations are 'script' and 'scriptconfig'.


Examples
--------

Same script and for two sites

    iotlab-experiment submit ... \
        --site-association grenoble,lille,script=experient.sh


Same script but a different config for each site

    iotlab-experiment submit ... \
        --site-association grenoble,lille,script=experiment
        --site-association grenoble,scriptconfig=grenoble.conf
        --site-association lille,scriptconfig=lille.conf
