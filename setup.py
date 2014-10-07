#! /usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from setuptools import setup, find_packages
from iotlabcli import VERSION


# unload 'iotlabcli' module
# either it's not included in the coverage report...
try:
    del sys.modules['iotlabcli']
except KeyError:
    pass

SCRIPTS = ['auth-cli', 'experiment-cli', 'node-cli', 'profile-cli']


setup(
    name='iotlabcli',
    version=VERSION,
    description='IoT-LAB testbed command-line client',
    author='IoT-LAB Team',
    author_email='admin@iot-lab.info',
    url='http://www.iot-lab.info',
    download_url='http://github.com/iot-lab/cli-tools/',
    packages=find_packages(),
    scripts=SCRIPTS,
    classifiers=['Development Status :: 1 - Beta',
                 'Programming Language :: Python',
                 'Intended Audience :: End Users/Desktop',
                 'Environment :: Console',
                 'Topic :: Utilities', ],
    install_requires=['argparse', 'requests'],
    setup_requires=['setuptools-pep8', 'setuptools-lint',
                    'nose', 'nosexcover', 'mock'],
)
