=================
Experiment client
=================

The client provides the following five commands :  submit, stop, get, load, info

	``$ experiment-cli -h``


-----------------
Submit experiment
-----------------

View submit command options

        ``$ experiment-cli submit -h``

The submission is a request to the scheduler of the testbed, which allows resources (sensor nodes) reservation
for experimentation with a duration. If your submission is accepted by the scheduler, the response is
**id submission experiment**.

There is two types of submission :

* **physical** : based on physical sensor nodes reservation with id.
* **alias** : based on sensor nodes properties (**architecture, site, mobile**) and the number of nodes expected.

Submit a physical experiment type on Grenoble site with name test_cc1101, duration of 30 minutes and
five nodes : 

	``$ experiment-cli submit -n test_cc1101 -d 30 -a grenoble,1-4+5``

Submit the same experiment with alias type :

        ``$ experiment-cli  submit -n test_cc1101 -d 30 -a 5,archi=wsn430:cc1101+site=grenoble``

Submit a physical experiment type with two sites Grenoble and Rennes :

	``$ experiment-cli submit -d 30 -a grenoble,1-6+12+20 -a rennes,1-50``

Submit the same experiment with alias type :

        ``$ experiment-cli  submit -d 30 -a 8,archi=wsn430:cc1101+site=grenoble -a 
        50,archi=wsn430:cc2420+site=rennes``

You can specify the associations between profiles, firmwares and sensor nodes for experiment deployment
configuration.

Submit experiment with associations :

* Profile name profile_cc2420 (already saved into the user profile store, See :ref:`profile-label`) and firmware absolute path file

	``$ experiment-cli submit -d 30 -a grenoble,1-3+4,profile_cc2420,/home/user/tp.hex``

* Only firmware relative path file

        ``$ experiment-cli submit -d 30 -a grenoble,1-3+4,,tp.ihex``

* Only profile name profile_cc2420

        ``$ experiment-cli submit -d 30 -a grenoble,1-3+4,profile_cc2420``


.. note::

  By default if you don't specify associations on sensor nodes :

  * without profile nodes are configured with a power supply method dc and no polling measure configuration
  * without firmware the sensor nodes are programmed with the firmware "idle".

  You can view experiment JSON representation with option -j|--json without saving it on the server.


You can also schedule your experiment with -r option. For this we use Linux epoch timestamp.

Submit experiment with a schedule date (e.g. 20 Sep 2012 14:00:00) :

    	``$ experiment-cli submit -n schedule_experiment -d 20 -a grenoble,1-100  -r $(date +%s -d "20 Sep 2012 14:00:00 UTC")``

.. note::
 
  The linux command ``date +%s`` gives you the current Linux epoch timestamp (seconds since 1970-01-01 00:00:00 UTC)

---------------
Stop experiment
---------------

Stop an experiment :
	
	``$ experiment-cli stop``

.. note::

  If you have only one experiment with state Running you don't need to use id experiment option.

--------------
Get experiment
--------------

Get experiment submission JSON representation :

        ``$ experiment-cli get -j``

Get experiment archive (tar.gz) containing submission JSON representation and firmware(s) :

        ``$ experiment-cli get -a``

Get experiment resources list JSON representation (e.g. sensor nodes) :

	``$ experiment-cli get -r``

Get experiment state JSON representation :

	``$ experiment-cli get -s``

.. note::

  If you have only one experiment with state Running you don't need to use id experiment option.


------------------
Load an experiment
------------------

Load an experiment JSON representation with absolute path and submit on server.

	``$ experiment-cli load -f /home/user/experiment.json``

Load an experiment JSON representation with relative path and submit on server.

	``$ experiment-cli load -f experiment.json``

If you have a firmware association in your experiment JSON representation, we open
by default firmware file with relative path. If you want to use firmware file with
absolute path you can use -l option to refer to the firmware(s) list in the JSON representation.


	``$ experiment-cli load -f experiment.json -l /home/user/tp.hex,/home/user/firm.ihex``


---------------------------------------------
Testbed information for experiment submission
---------------------------------------------


Get testbed sites list JSON representation

	``$ experiment-cli info -s``

Get testbed resources list JSON representation

	``$ experiment-cli info -r``

Get testbed resources state list JSON representation (e.g. command-line NODE_LIST format : 1-5+7)

        ``$ experiment-cli info -rs``

Get total number of upcoming, running and past user's experiments JSON representation

	``$ experiment-cli info -t``

Get user's experiment list JSON representation 

	``$ experiment-cli info -e``

You can filter your search with attribute state, limit (number of experiments) and offset (start index of number experiments).

	``$ experiment-cli info -e --state Running,Terminated --offset 10 --limit 20``

