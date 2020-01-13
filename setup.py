#! /usr/bin/env python
# -*- coding:utf-8 -*-

# This file is a part of IoT-LAB cli-tools
# Copyright (C) 2015 INRIA (Contact: admin@iot-lab.info)
# Contributor(s) : see AUTHORS file
#
# This software is governed by the CeCILL license under French law
# and abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# http://www.cecill.info.
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

import os
from setuptools import setup, find_packages

PACKAGE = 'iotlabcli'
# GPL compatible http://www.gnu.org/licenses/license-list.html#CeCILL
LICENSE = 'CeCILL v2.1'


def cat(files, join_str=''):
    """Concatenate `files` content with `join_str` between them."""
    files_content = (open(f).read() for f in files)
    return join_str.join(files_content)


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


SCRIPTS = ['iotlab-auth', 'iotlab-experiment', 'iotlab-node', 'iotlab-profile',
           'iotlab-robot', 'iotlab-status', 'iotlab']

LONG_DESCRIPTION_FILES = ['README.rst', 'CHANGELOG.rst']


setup(
    name=PACKAGE,
    version=get_version(PACKAGE),
    description='IoT-LAB testbed command-line client',
    long_description=cat(LONG_DESCRIPTION_FILES, u'\n\n'),
    author='IoT-LAB Team',
    author_email='admin@iot-lab.info',
    url='http://www.iot-lab.info',
    license=LICENSE,
    download_url='http://github.com/iot-lab/cli-tools/',
    packages=find_packages(),
    package_data={'integration/firmwares': ['integration/firmwares/*']},
    include_package_data=True,
    scripts=SCRIPTS,
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Intended Audience :: End Users/Desktop',
                 'Environment :: Console',
                 'Topic :: Utilities', ],
    extras_require={
        # https://urllib3.readthedocs.org/en/latest/\
        #     security.html#openssl-pyopenssl
        'secure': ['pyOpenSSL', 'ndg-httpsclient', 'pyasn1'],
    },
    install_requires=['requests>2.4.2', 'jmespath'],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
)
