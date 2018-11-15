# -*- coding: utf-8 -*-

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

""" Test the iotlabcli.helpers module """
# pylint:disable=too-many-public-methods,redefined-outer-name

import unittest
import sys
import warnings

import pytest

from iotlabcli import helpers
from iotlabcli.tests import my_mock

from .c23 import patch


class TestHelpers(unittest.TestCase):
    """ Test the iotlabcli.helpers module """

    def test_exp_by_states(self):
        """ Run the 'exp_by_states' function """
        api = my_mock.api_mock({"items": [{'state': 'Waiting', 'id': 10134},
                                          {'state': 'Waiting', 'id': 10135},
                                          {'state': 'Running', 'id': 10130}]})
        states_d = helpers.exps_by_states_dict(api, helpers.ACTIVE_STATES)
        self.assertEqual(
            {'Waiting': [10134, 10135], 'Running': [10130]}, states_d)
        my_mock.api_mock_stop()

    def test_get_current_experiment(self):
        """ Test get_current_experiment """
        api = None
        with patch('iotlabcli.helpers.exps_by_states_dict') as exps_m:
            exps_m.return_value = {'Running': [234]}

            self.assertEqual(123, helpers.get_current_experiment(api, 123))
            self.assertEqual(234, helpers.get_current_experiment(api, None))

            # also return 'active' experiments
            exps_m.return_value = {'Waiting': [234]}
            self.assertEqual(234, helpers.get_current_experiment(
                api, None, running_only=False))

    @patch('sys.stderr', sys.stdout)
    @patch('iotlabcli.helpers.read_file')
    def test_read_custom_api_url(self, read_file_mock):
        """ Test API URL reading """

        # No config
        with patch('os.getenv', return_value=None):
            read_file_mock.side_effect = IOError()
            self.assertTrue(helpers.read_custom_api_url() is None)

        # Only File
        with patch('os.getenv', return_value=None):
            read_file_mock.side_effect = None
            read_file_mock.return_value = 'API_URL_CUSTOM'
            self.assertEqual('API_URL_CUSTOM', helpers.read_custom_api_url())

        # Only env variable
        with patch('os.getenv', return_value='API_URL_2'):
            read_file_mock.side_effect = IOError()
            self.assertEqual('API_URL_2', helpers.read_custom_api_url())

        # File priority over env variable
        with patch('os.getenv', return_value='API_URL_2'):
            read_file_mock.side_effect = None
            read_file_mock.return_value = 'API_URL_CUSTOM'
            self.assertEqual('API_URL_CUSTOM', helpers.read_custom_api_url())

    def test_deprecate_command(self):
        """Test command deprecation."""
        with warnings.catch_warnings(record=True) as warn:
            helpers.deprecate_cmd(lambda: None, "old", "new")

        self.assertEqual(len(warn), 1)
        self.assertTrue(issubclass(warn[-1].category, DeprecationWarning))
        self.assertTrue(helpers.DEPRECATION_MESSAGE.format(old_cmd="old",
                                                           new_cmd="new")
                        in str(warn[-1].message))


# Test FilesDict class

@pytest.fixture(scope='function')
def file_dict():
    """fixture to provide an empty FilesDict"""
    return helpers.FilesDict()


def test_none_input(file_dict):
    """FilesDict.add_file(None) should do nothin"""
    assert file_dict.add_file(None) is None
    assert file_dict == {}


def test_can_overwrite(file_dict):
    """we can overwrite a value inside the FileDict if same value"""
    file_dict['test'] = 'value'
    file_dict['test'] = 'value'

    assert file_dict['test'] == 'value'


def test_dict_eq(file_dict):
    """a FileDict should be equatable to a dict"""
    file_dict['test'] = 'value'
    file_dict['test2'] = 'value'
    file_dict['test3'] = 'value3'

    assert file_dict == {'test': 'value', 'test3': 'value3', 'test2': 'value'}


def test_no_overwrite(file_dict):
    """Test FilesDict values overriding."""
    file_dict['a'] = 1
    # Can re-add same value
    file_dict['a'] = 1

    # Cannot add a different valu
    file_dict['b'] = 2

    with pytest.raises(ValueError):
        file_dict['b'] = 3

    # Check dict
    assert file_dict == {'a': 1, 'b': 2}


@patch('iotlabcli.helpers.read_file')
def test_same_basename_files(read_file, file_dict):
    """Test FilesDict add_file methods
    when given two files with same basename."""

    files = {
        'a/1.elf': b'ELF32_1',
        '~/iot-lab/b/1.elf': b'ELF32_2',
        '/tmp/c/1.elf': b'ELF32_3',
    }

    keys = [
        '1.elf',
        '56d50b0f4f3216dd962e8911ec91c062_1.elf',
        'c7b7412e59348fb71ca8ec6619284f3f_1.elf'
    ]

    def _read_file(name, *_):
        """Read file mock."""

        return files[name]

    read_file.side_effect = _read_file

    # Add some files
    input_files_dict = {'firmware': 'a/1.elf'}
    inserted = file_dict.add_files_from_dict(('firmware',), input_files_dict)
    assert inserted['firmware'] == keys[0]
    assert file_dict == {keys[0]: b'ELF32_1'}

    # Add some other files
    input_files_dict = {'firmware': '~/iot-lab/b/1.elf'}
    inserted = file_dict.add_files_from_dict(('firmware',), input_files_dict)

    assert inserted['firmware'] == keys[1]
    assert file_dict == {keys[0]: b'ELF32_1',
                         keys[1]: b'ELF32_2'}

    input_files_dict = {'firmware': '/tmp/c/1.elf'}
    inserted = file_dict.add_files_from_dict(('firmware',), input_files_dict)

    assert inserted['firmware'] == keys[2]
    assert file_dict == {keys[0]: b'ELF32_1',
                         keys[1]: b'ELF32_2',
                         keys[2]: b'ELF32_3'}


@patch('iotlabcli.helpers.read_file')
def test_add_file_method(read_file, file_dict):
    """Test FilesDict add_file methods."""
    def _read_file(name, *_):
        """Read file mock."""
        files = {
            '1.elf': b'ELF32_1',
            '2.elf': b'ELF32_2',
            'prof.json': b'{}',
        }
        return files[name]
    read_file.side_effect = _read_file

    # Add some files
    input_files_dict = {'firmware': '1.elf', 'profile': 'prof.json'}
    file_dict.add_files_from_dict(['firmware', 'profile', 'script'],
                                  input_files_dict)
    assert file_dict == {'1.elf': b'ELF32_1', 'prof.json': b'{}'}

    # Add some other files
    input_files_dict = {'firmware': '2.elf', 'scriptconfig': 'otherfile'}
    file_dict.add_files_from_dict(['firmware', 'profile', 'script'],
                                  input_files_dict)
    assert file_dict == {'1.elf': b'ELF32_1', '2.elf': b'ELF32_2',
                         'prof.json': b'{}', }
