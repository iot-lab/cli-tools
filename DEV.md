Development notice
==================

These are advices on how to maintain iotlabcli as I do right now.

Code validation
---------------

No errors are allowed, some warning may be disabled but not let unresolved.

    python setup.py lint
    python setup.py pep8
    flake8  # it does not work from setup.py script
    python setup.py nosetests

Multi-versions tests
--------------------

Python versions 2.6, 2.7, 3.2, 3.3 and 3.4 are unit-tested

    tox

Python 3.1 does not run due to external dependencies issues.


Multi python versions support
-----------------------------

### Python2.6 ###

 * unittest.TestCase.assertRaisesRegexp not supported
 * str.format() only used numbered/named argument


### Python3.X ###

 * Prefer '.format' when formatting strings
 * Use from `__future__ import print_function` and print('str') with parens

