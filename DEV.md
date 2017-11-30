Development notice
==================

These are advices on how to maintain iotlabcli as I do right now.

Automatic multi version tests
-----------------------------

Python versions 2.7, 3.4, 3.5 and 3.6 are unit-tested.
You can run all tests with:

    tox

Running test for one specific version

    tox -e py27
    tox -e py36


Step by step validation
-----------------------

### Test dependencies ###

Development depencencies can be installed with

    pip install -r tests_utils/test-requirements


### Manually running tests ###

    python setup.py lint
    python setup.py pep8
    flake8  # it does not work from setup.py script
    python setup.py nosetests


Coding constraints
------------------

### Python3.X ###

 * Prefer '.format' when formatting strings
 * Use from `__future__ import print_function` and print('str') with parens

