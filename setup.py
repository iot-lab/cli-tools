#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os
from setuptools import setup, find_packages

PACKAGE = 'iotlabcli'


def get_version(package):
    """ Extract package version without importing file
    Importing cause issues with coverage,
        (modules can be removed from sys.modules to prevent this)
    Importing __init__.py triggers importing rest and then requests too

    Inspired from pep8 setup.py
    """
    with open(os.path.join(package, '__init__.py')) as init_fd:
        for line in init_fd:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])  # pylint:disable=eval-used


SCRIPTS = ['auth-cli', 'experiment-cli', 'node-cli', 'profile-cli']


setup(
    name=PACKAGE,
    version=get_version(PACKAGE),
    description='IoT-LAB testbed command-line client',
    author='IoT-LAB Team',
    author_email='admin@iot-lab.info',
    url='http://www.iot-lab.info',
    download_url='http://github.com/iot-lab/cli-tools/',
    packages=find_packages(),
    package_data={'integration/firmwares': ['integration/firmwares/*']},
    scripts=SCRIPTS,
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 3',
                 'Intended Audience :: End Users/Desktop',
                 'Environment :: Console',
                 'Topic :: Utilities', ],
    install_requires=['argparse', 'requests>2.4.2']
)
