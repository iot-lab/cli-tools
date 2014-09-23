# -*- coding:utf-8 -*-
""" Test the iotlabcli.rest module """

# pylint: disable=too-many-public-methods,missing-docstring

import unittest
try:
    # pylint: disable=import-error,no-name-in-module
    from mock import patch
except ImportError:  # pragma: no cover
    # pylint: disable=import-error,no-name-in-module
    from unittest.mock import patch
from iotlabcli import rest


class TestRest(unittest.TestCase):

    @patch('iotlabcli.helpers.read_file')
    def test_read_custom_api_url(self, read_file_mock):
        read_file_mock.side_effect = IOError()

        self.assertIsNone(rest.read_custom_api_url())

        read_file_mock.side_effect = None
        read_file_mock.return_value = 'API_URL_CUSTOM'
        self.assertEquals('API_URL_CUSTOM', rest.read_custom_api_url())

        with patch('os.getenv', return_value='API_URL_2'):
            self.assertEquals('API_URL_2', rest.read_custom_api_url())
