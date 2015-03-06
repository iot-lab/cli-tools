Development notice
==================

These are advices on how to maintain iotlabcli as I do right now.

Automatic multi version tests
-----------------------------

Python versions 2.6, 2.7, 3.2, 3.3 and 3.4 are unit-tested
You can run all tests with:

    tox

Running test for one specific version

    tox -e py26
    tox -e py32

Python 3.1 does not run due to external dependencies issues.


Step by step validation
-----------------------

### Test dependencies ###

Development depencencies can be installed with

    pip install -r test-requirements

For `python2.6` / `python3.2`

    pip install -r tests_utils/pylint-python-2.6_3.2.txt
    pip install -r tests_utils/test-requirements

### Manually running tests ###

    python setup.py lint
    python setup.py pep8
    flake8  # it does not work from setup.py script
    python setup.py nosetests


Coding constraints
------------------

### Python2.6 ###

 * unittest.TestCase.assertRaisesRegexp not supported
 * str.format() only used numbered/named argument


### Python3.X ###

 * Prefer '.format' when formatting strings
 * Use from `__future__ import print_function` and print('str') with parens

