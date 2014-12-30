# -*- coding: utf-8 -*-
""" Test the iotlabcli.helpers module """
# pylint:disable=too-many-public-methods

import unittest
from iotlabcli.tests import patch
from iotlabcli import helpers
from iotlabcli.tests import my_mock


class TestHelpers(unittest.TestCase):
    """ Test the iotlabcli.helpers module """

    def test_exp_by_states(self):
        """ Run the 'exp_by_states' function """
        api = my_mock.api_mock({"items": [{'state': 'Waiting', 'id': 10134},
                                          {'state': 'Waiting', 'id': 10135},
                                          {'state': 'Running', 'id': 10130}]})
        states_d = helpers.exps_by_states_dict(api, helpers.ACTIVE_STATES)
        self.assertEquals(
            {'Waiting': [10134, 10135], 'Running': [10130]}, states_d)
        my_mock.api_mock_stop()

    def test_get_current_experiment(self):
        """ Test get_current_experiment """
        api = None
        with patch('iotlabcli.helpers.exps_by_states_dict') as exps_m:
            exps_m.return_value = {'Running': [234]}

            self.assertEquals(123, helpers.get_current_experiment(api, 123))
            self.assertEquals(234, helpers.get_current_experiment(api, None))

            # also return 'active' experiments
            exps_m.return_value = {'Waiting': [234]}
            self.assertEquals(234, helpers.get_current_experiment(
                api, None, running_only=False))

    @patch('iotlabcli.helpers.read_file')
    def test_read_custom_api_url(self, read_file_mock):
        """ Test API URL reading """

        with patch('os.getenv', return_value=None):
            read_file_mock.side_effect = IOError()
            self.assertTrue(helpers.read_custom_api_url() is None)

        with patch('os.getenv', return_value=None):
            read_file_mock.side_effect = None
            read_file_mock.return_value = 'API_URL_CUSTOM'
            self.assertEquals('API_URL_CUSTOM', helpers.read_custom_api_url())

        with patch('os.getenv', return_value='API_URL_2'):
            self.assertEquals('API_URL_2', helpers.read_custom_api_url())
