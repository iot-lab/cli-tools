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
# pylint:disable=too-many-public-methods

import unittest
import sys

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
