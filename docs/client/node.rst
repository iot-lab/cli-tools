===========
Node client
===========

Four commands are available to interact with sensor nodes experiment. If you have only one experiment
with state Running you don't need to use id experiment option. Also if you want to launch commands for 
**all sensor nodes** experiment you don't use option -a in the command-line.

	``$ node-cli -h``


* **update** : flash firmware on sensor node(s)

	All sensor nodes of your current experiment with state Running :

        ``$ node-cli --update /home/cc1101.hex``        

        A set of experiment nodes :

	``$ node-cli -a grenoble,1-34 --update /home/cc1101.hex``

        If you have several experiments with state Running you must use experiment id option :

        ``$ node-cli -i 32 --update cc1101.hex``        

* **stop** : stop  sensor node(s)
	
	``$ nodde-cli --stop ``

* **reset** : stop and start sensor node(s)

	``$ node-cli --reset``

* **start** : start sensor node(s)

        ``$ node-cli --start`

	You can also specify the powered method with battery (dc by default) :

	``$ node-cli --start -b``


