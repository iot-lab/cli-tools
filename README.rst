IoT-Lab cli-tools
=================

|PyPI| |Travis| |Codecov|

IoT-LAB cli-tools provide a basic set of operations for managing IoT-LAB
experiments from the command-line.

License
-------

IoT-LAB cli-tools, including all examples, code snippets and attached
documentation is covered by the CeCILL v2.1 free software licence.

Commands
--------

IoT-LAB cli-tools are available through a shared entrypoint, ``iotlab``,
Many subcommands are available:

+------------------------------+----------------------------------------------------------------------------------------+
| Command                      | Functions                                                                              |
+==============================+========================================================================================+
| ``iotlab auth``              | configure account credentials                                                          |
+------------------------------+----------------------------------------------------------------------------------------+
| ``iotlab experiment``        | start, stop, query experiments                                                         |
+------------------------------+----------------------------------------------------------------------------------------+
| ``iotlab node``              | start, stop, reset nodes, update firmwares                                             |
+------------------------------+----------------------------------------------------------------------------------------+
| ``iotlab profile``           | manage nodes configurations                                                            |
+------------------------------+----------------------------------------------------------------------------------------+
| ``iotlab robot``             | manage robot nodes                                                                     |
+------------------------------+----------------------------------------------------------------------------------------+
| ``iotlab status``            | manage informations about testbed sites, nodes and running experiments                 | 
+------------------------------+----------------------------------------------------------------------------------------+

Optional commands:
------------------

When `IoT-Lab SSH CLI Tools <https://github.com/iot-lab/ssh-cli-tools>`_ is installed:

+------------------------------+----------------------------------------------------------------------------------------+
| ``iotlab ssh``               | run commands on A8 open nodes through SSH                                              |
+------------------------------+----------------------------------------------------------------------------------------+

When `IoT-Lab OML plot Tools <https://github.com/iot-lab/oml-plot-tools>`_ is installed:

+------------------------------+----------------------------------------------------------------------------------------+
| ``iotlab plot traj``         | plot robot trajectory                                                                  |
+------------------------------+----------------------------------------------------------------------------------------+
| ``iotlab plot consum``       | plot node consumption                                                                  |
+------------------------------+----------------------------------------------------------------------------------------+
| ``iotlab plot radio``        | plot node sniffer results                                                              |
+------------------------------+----------------------------------------------------------------------------------------+

When `IoT-Lab Aggregation Tools <https://github.com/iot-lab/aggregation-tools>`_ is installed:

+------------------------------+----------------------------------------------------------------------------------------+
| ``iotlab serial``            | aggregate node serial link                                                             |
+------------------------------+----------------------------------------------------------------------------------------+
| ``iotlab sniffer``           | aggregate node sniffer link                                                            |
+------------------------------+----------------------------------------------------------------------------------------+


Commands are self-documented, and usually have sub-commands which are
also self-documented. Use e.g:

::

    iotlab-node --help
    iotlab-profile add --help

Description
-----------

The cli-tools leverage the IoT-LAB ``REST API`` and simply wrap calls to
module ``iotlabcli``, which is a Python client for the API.

The cli-tools come as an installable Python package and require that
module ``setuptools`` be installed before tools installation can happen.
Please grab the relevant python-setuptools package for your
distribution.

To install cli-tools from Pypi, use ``pip install iotlabcli``.

To install cli-tools from source, use ``pip install --user .`` or ``python setup.py install``

Installing cli-tools automatically fetches additional dependencies as
needed.

Further documentation: https://github.com/iot-lab/iot-lab/wiki/CLI-Tools

.. |PyPI| image:: https://badge.fury.io/py/iotlabcli.svg
   :target: https://badge.fury.io/py/iotlabcli
   :alt: PyPI package status

.. |Travis| image:: https://travis-ci.org/iot-lab/cli-tools.svg?branch=master
   :target: https://travis-ci.org/iot-lab/cli-tools
   :alt: Travis build status

.. |Codecov| image:: https://codecov.io/gh/iot-lab/cli-tools/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/iot-lab/cli-tools/branch/master
   :alt: Codecov coverage status
