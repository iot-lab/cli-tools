Changelog
=========

1.5.2: BUG: Add dependency on `request >= 2.4.2` for 'json' upload parameter
1.5.1: Add 'experiment-cli get --start-time' command

1.5.0
-----

+ Features

 * 'sniffer' option in profile m3/a8
 * 'profile-cli' commands now return a json dict
 * Nicely catch rest HTTPError for Access Denied 401
 * Check credentials for auth-cli with the server

 + Bugs
    * Fix load profile
    * Unicode management in python3
    * Help messages
    * Python3 crash without command for exp-cli

1.4.1: BUG Force pylint dependency for python2.6
