Welcome to Senslab command-line client documentation !
================================================

=====
About
=====

.. include:: ../README.rst

============
Installation
============

In order to achieve module installation, two primary pieces of software are needed :

* the python module `argparse <http://docs.python.org/dev/library/argparse.html>`_;

* the python module `requests <http://docs.python-requests.org/en/latest/index.html>`_;

Ubuntu desktop :

	``$ sudo apt-get install python-argparse python-pip``
        
	``$ sudo pip install requests``

Fedora desktop :

    	``$ yum install python-argparse python-pip``

	``$ pip-python install requests``


**Download and unpack** the client archive and run this command : 

	``tar -xzvf senslabcli-1.x.tar.gz & cd senlabcli-1.x``

Ubuntu desktop :

	``$ sudo python setup.py install`` 

Fedora desktop :

	``$ python setup.py install``



============
General Note
============

--------------
Error handling
--------------
API Rest errors are returned using standard HTTP error code syntax. Each error message is included into response body. 

----------------------------
Rest resource representation 
----------------------------
The supported format for API requests and responses is JSON representation. 

--------------
Authentication
--------------
We use basic http authentication (login and password) over SSL communication with your account credentials. 


============
Command-line 
============

.. toctree::
   :maxdepth: 2
   :glob:

   client/*


