# -*- coding: utf-8 -*-

""" Test the iotlabcli.auth_parser module """

import unittest
from mock import patch

from iotlabcli import auth_parser


@patch('iotlabcli.helpers')
class TestStoreCredentials(unittest.TestCase):
    def test_store_credentials(self, helpers_m):
        auth_parser.store_credentials('super_user', 'password')
        self.assertEquals(0, helpers_m.password_prompt.call_count)
        helpers_m.create_password_file.assert_called_with('super_user',
                                                          'password')

    def test_store_credentials_no_passwd(self, helpers_m):
        helpers_m.password_prompt.return_value = 'password'

        auth_parser.store_credentials('super_user', None)
        self.assertEquals(1, helpers_m.password_prompt.call_count)
        helpers_m.create_password_file.assert_called_with('super_user',
                                                          'password')
