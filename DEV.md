Development notice
==================

These are advices on how to maintain iotlabcli as I do right now.

Automatic multi version tests
-----------------------------

Python versions 3.7+ are unit-tested.
You can run all tests with:

    tox

Running test for one specific version

    tox -e py313


Step by step validation
-----------------------

### Test dependencies ###

Development depencencies can be installed with

    pip install -r tests_utils/test-requirements
