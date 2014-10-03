# -*- coding: utf-8 -*-
""" Test the iotlabcli.helpers module """
# pylint:disable=too-many-public-methods

import unittest
try:
    # pylint: disable=import-error,no-name-in-module
    from mock import patch
except ImportError:  # pragma: no cover
    # pylint: disable=import-error,no-name-in-module
    from unittest.mock import patch

from iotlabcli import helpers
from iotlabcli.tests import my_mock


class TestHelpers(unittest.TestCase):
    """ Test the iotlabcli.helpers module """

    def test_get_current_experiment(self):
        """ Test get_current_experiment """
        api = my_mock.api_mock(ret={"items": [{"id": 234}]})
        self.assertEquals(123, helpers.get_current_experiment(api, 123))
        self.assertEquals(234, helpers.get_current_experiment(api, None))
        my_mock.api_mock_stop()

    def test__check_experiments_running(self):
        """ Test _check_experiments_running """
        # pylint:disable=protected-access
        self.assertEquals(
            123, helpers._check_experiments_running({"items": [{"id": 123}]}))
        self.assertRaises(RuntimeError, helpers._check_experiments_running,
                          {"items": []})
        self.assertRaises(RuntimeError, helpers._check_experiments_running,
                          {"items": [{"id": 123}, {"id": 124}]})

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
