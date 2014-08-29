#! /usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand
from iotlabcli import VERSION

SCRIPTS = ['auth-cli', 'experiment-cli', 'node-cli', 'profile-cli']


setup(name='iotlabcli',
      version=VERSION,
      description='IoT-LAB testbed command-line client',
      author='IoT-LAB Team',
      author_email='admin@iot-lab.info',
      url='http://www.iot-lab.info',
      download_url='http://github.com/iot-lab/cli-tools/',
      packages=['iotlabcli'],
      scripts=SCRIPTS,
      classifiers=['Development Status :: 1 - Beta',
                   'Programming Language :: Python',
                   'Intended Audience :: End Users/Desktop',
                   'Environment :: Console',
                   'Topic :: Utilities', ],
      install_requires=['argparse', 'requests<=1.2.3'],
      test_suite='nose.collector',
      tests_require=['nose'],
      setup_requires=['setuptools-pep8', 'setuptools-lint'],
      )
