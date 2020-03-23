Changelog
=========

3.1.1
-----

- fix URL used with update-profile command

3.1.0
-----

- Add --cancel-on-timeout flag with experiment wait subcommand

3.0.0
-----

- Migrate the new IoT-LAB REST API (https://api.iot-lab.info)
- Add iotlab-status command
- Add support for flashing firmware in raw format with .bin extension
- Remove the iotlab-admin command

2.6.0
-----

- Manage duplicated firmware name at experiment submission
- Add iotlab subcommands (experiment, node, profile, ...)
- Add autocompletion script

2.5.4
-----

- Replace remaining occurences of *-cli with iotlab-* in commands help
- Use new command names in integration tests

2.5.3
-----

- Replace remaining occurences of *-cli with iotlab-*

2.5.2
-----

- Revert 2.5.1

2.5.1
-----

-  Fixing python 3 required version in setup.py

2.5.0
-----

-  Drop python 2.6 support
-  Fixing issues raised by pylint 1.8
-  Deprecate *-cli commands and add new iotlab-* commands

2.4.2
-----

Bugs
~~~~

-  Fix load experiment with mobilities or profiles associations.

2.4.1
-----

Features
~~~~~~~~

-  Remove ``archi`` names validation in AliasNodes association

Internal
~~~~~~~~

-  Fixing pylint

2.4.0
-----

Features
~~~~~~~~

-  Add ``script`` execution management at submit and during experiment
-  Add node ``update-idle`` command to update firmware with an idle
   firmware.
-  Add node ``profile-load`` command to update profile from a JSON.
-  Add node ``profile-reset`` command to update profile with the default
   one.
-  Allow restricting output by archi and state in
   ``experiment-cli info``
-  Allow restricting by archi for ``profile-cli get``
-  Allow providing ``-l`` multiples times for ``experiment-cli load``
-  Remove parser ``archi`` names validation, prepare for adding new
   ones.
-  Add dedicated help commands for ``--list`` and ``--site-association``
   options
-  Update for Pypi

   -  README and CHANGELOG to ``reStructuredText``
   -  Set ``long_description`` in ``setup.py``

Internal
~~~~~~~~

-  Refactoring ``associations`` management
-  Reduce maximum McCabe complexity to 4

2.3.0.post1
-----------

Same as 2.3.0 but rebased on master branch.

2.3.0
-----

Features
~~~~~~~~

-  Add a 'get --experiments' command to get a summary of active
   experiments ids.
-  Add support to ``reload`` experiment by 'id' (as on the website)
-  Add an ``admin-cli`` script with a command to wait for any user
   experiment

   -  Required for ``runscript``: allows waiting for an user experiment
      without ``auth-cli`` having been run on the server.

Internal
~~~~~~~~

-  Fixing docstrings
-  Refactoring internal code and tests

2.0.0
-----

Backward incompatible changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  robot-cli: ``--status`` command replaced by ``status``
-  profile-cli: remove support for mobility in profiles (remove from the
   api)

Features
~~~~~~~~

-  New architectures: add support for 'custom' and 'des' nodes
-  experiment-cli submit: add named arguments and associations support:

::

    --list grenoble,m3,1,tutorial.elf,consumption
    # equivalent to --list
    grenoble,m3,1,profile=consumption,firmware=tutorial.elf

    # Specifying robot mobility to 'Jhall'
    --list grenoble,m3,381,mobility=Jhall

-  robot-cli: add new commands

   status: get robot status get --list: list user mobilities get --name
   NAME,SITE: get given mobility JSON update NAME,SITE: update robots
   with given mobility

-  rest: add commands to download map and configuration (for
   oml-plot-tools)
-  2.1.0: Add a context manager for missing auth-cli
-  2.2.0: Add 'custom' nodes profile creation in profile-cli
-  2.2.1: Officially support python3.5, fix broken test and cleanup
   tox.ini

1.8.0
-----

Features
~~~~~~~~

-  Add ``--jmespath`` and ``--format`` options to handle json output
-  1.8.1: Fix pylint 1.5.0 new warnings

1.7.0
-----

Features
~~~~~~~~

-  Add 'debug-start' and 'debug-stop' commands

Bugs
~~~~

-  Fix how home directory is found.
-  Force 'mock' version to stay compatible with python2.6
-  Fix integration 'tox' command to have a correct coverage output.
-  1.7.1: Add dependency on 'urllib3[secure]' to fix ssl connections
   security
-  1.7.2: Catch BrokenPipe errors when printing results

1.6.0
-----

Setting the license to CeCILL v2.1

Features
~~~~~~~~

-  Add an ``update-profile`` command to node-cli to change monitoring
   profile
-  Add a ``robot-cli`` script to interract with the robot. Provides a
   ``--status`` to query the robot internal status.
-  Move experiment node selection to ``parser.common``.. May break
   external softwares using internal api.

Bugs
~~~~

-  Restrict flake8 version due to pep8 incompatibility
-  Correct ``auth_parser`` test that tried external connections

1.5.0
-----

Features
~~~~~~~~

-  'sniffer' option in profile m3/a8
-  'profile-cli' commands now return a json dict
-  Nicely catch rest HTTPError for Access Denied 401
-  Check credentials for auth-cli with the server

Bugs
~~~~

-  Fix load profile
-  Unicode management in python3
-  Help messages
-  Python3 crash without command for exp-cli
-  1.5.1: Add 'experiment-cli get --start-time' command
-  1.5.2: BUG: Add dependency on ``request >= 2.4.2`` for 'json' upload
   parameter
-  1.5.3: Move test dependencies to ``tests_require``
-  1.5.4: Catch 'request' exception for old version and raise as
   RuntimeError
-  1.5.5: Custom api url file has now priority over env variable. Print
   when using alternate api url.
-  1.5.6: Cleanup setup.py and tests

1.4.0
-----

-  1.4.1: BUG Force pylint dependency for python2.6

