Changelog
=========

1.4.0
-----

- 1.4.1: BUG Force pylint dependency for python2.6

1.5.0
-----

### Features ###

+ 'sniffer' option in profile m3/a8
+ 'profile-cli' commands now return a json dict
+ Nicely catch rest HTTPError for Access Denied 401
+ Check credentials for auth-cli with the server

### Bugs ###

- Fix load profile
- Unicode management in python3
- Help messages
- Python3 crash without command for exp-cli

+ 1.5.1: Add 'experiment-cli get --start-time' command
- 1.5.2: BUG: Add dependency on `request >= 2.4.2` for 'json' upload parameter
+ 1.5.3: Move test dependencies to `tests_require`
- 1.5.4: Catch 'request' exception for old version and raise as RuntimeError
+ 1.5.5: Custom api url file has now priority over env variable.
         Print when using alternate api url.
+ 1.5.6: Cleanup setup.py and tests


1.6.0
-----

### Features ###

+ Add an `update-profile` command to node-cli to change monitoring profile
+ Add a `robot-cli` script to interract with the robot.
  Provides a `--status` to query the robot internal status.
+ Move experiment node selection to `parser.common`..
  May break external softwares using internal api.

### Bugs ###

- Restrict flake8 version due to pep8 incompatibility
- Correct `auth_parser` test that tried external connections

