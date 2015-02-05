#! /usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from setuptools import setup, find_packages


def get_version():
    """ Extract module version without importing file
    Importing cause issues with coverage,
        (modules can be removed from sys.modules to prevent this)
    Importing __init__.py triggers importing rest and then requests too

    Inspired from pep8 setup.py
    """
    with open('iotlabcli/__init__.py') as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])


SCRIPTS = ['auth-cli', 'experiment-cli', 'node-cli', 'profile-cli']

TESTS_DEPS = [
    'setuptools-pep8', 'setuptools-lint', 'nose', 'nosexcover', 'mock'
]

if (2, 6) == sys.version_info[0:2]:
    TESTS_DEPS.append('pylint<1.4.0')
    TESTS_DEPS.append('astroid<1.3.0')


setup(
    name='iotlabcli',
    version=get_version(),
    description='IoT-LAB testbed command-line client',
    author='IoT-LAB Team',
    author_email='admin@iot-lab.info',
    url='http://www.iot-lab.info',
    download_url='http://github.com/iot-lab/cli-tools/',
    packages=find_packages(),
    scripts=SCRIPTS,
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 3',
                 'Intended Audience :: End Users/Desktop',
                 'Environment :: Console',
                 'Topic :: Utilities', ],
    install_requires=['argparse', 'requests>2.4.2'],
    tests_require=TESTS_DEPS,
)
