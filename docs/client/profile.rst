==============
Profile client
==============

You can create profiles to store you favourite sensor nodes configuration, for reusing it into your future experiments. A profile is the combination of a power supply mode and an automatic measure configuration (e.g. polling).

For each user there is a **profile store** on Senslab server and the command-line has four commands
(add, del, get, load) for managing it.

        ``$ profile-cli -h``

.. _profile-label:

-------------
Add profile
-------------

View add command options

        ``$ profile-cli add -h``

Add a profile on server with name test_consemptium, power supply method dc and power consemptium measure (current, voltage & power) with frequency
5000 milliseconds

        ``$ profile-cli add -n test_consemptium -p dc -current -voltage -power -cfreq 5000``

Add a profile on server with name test_sensor, power supply method battery and temperature sensor measure

        ``$ profile-cli add -n test_sensor -p battery -temperature``

.. note::

       You can view profile JSON representation with option -j|--json without saving it on server.  

       If you don't specify frequency for measure we use by default the frequency max in option choices. 

--------------
Delete profile
--------------

Delete profile on server with name test_profile

        ``$ profile-cli del -n test_profile``

-----------
Get profile
-----------

Get profile JSON representation with name test_profile

        ``$ profile-cli get -n test_profile``

Get profiles list JSON representation

        ``$ profile-cli get -l``

------------
Load profile
------------

Load a profile JSON representation with absolute path and save it on server

	``$ profile-cli load -f /home/user/profile.json``

Load a profile JSON representation with relative path and save it on server

	``$ profile-cli load -f profile.json``
