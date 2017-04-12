IoT-Lab cli-tools
=================

IoT-LAB cli-tools provide a basic set of operations for managing IoT-LAB
experiments from the command-line.

License
-------

IoT-LAB cli-tools, including all examples, code snippets and attached
documentation is covered by the CeCILL v2.1 free software licence.

Commands
--------

The following commands are available:

+------------------------------+---------------------------------------------+
| Command                      | Functions                                   |
+==============================+=============================================+
| ``auth-cli``                 | configure account credentials               |
+------------------------------+---------------------------------------------+
| ``experiment-cli``           | start, stop, query experiments              |
+------------------------------+---------------------------------------------+
| ``node-cli``                 | start, stop, reset nodes, update firmwares  |
+------------------------------+---------------------------------------------+
| ``profile-cli``              | manage nodes configurations                 |
+------------------------------+---------------------------------------------+
| ``robot-cli``                | manage robot nodes                          |
+------------------------------+---------------------------------------------+

Commands are self-documented, and usually have sub-commands which are
also self-documented. Use e.g:

::

    node-cli --help
    profile-cli add --help

Description
-----------

The cli-tools leverage the IoT-LAB ``REST API`` and simply wrap calls to
module ``iotlabcli``, which is a Python (2.6 or higher) client for the
API.

The cli-tools come as an installable Python package and require that
module ``setuptools`` be installed before tools installation can happen.
Please grab the relevant python-setuptools package for your
distribution.

To proceede to install cli-tools, use ``sudo python setup.py install``.

Installing cli-tools automatically fetches additional dependencies as
needed.

Further documentation: https://github.com/iot-lab/iot-lab/wiki/CLI-Tools
