# -*- coding: utf-8 -*-

""" Test the iotlabcli.auth_parser module """

import sys
import unittest
from mock import patch

import iotlabcli
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


@patch('iotlabcli.auth_parser.store_credentials')
@patch('sys.stderr', sys.stdout)
class TestMainAuthParser(unittest.TestCase):
    def test_main(self, store_m):
        """ Test main function """

        auth_parser.main(['-u', 'super_user'])
        store_m.assert_called_with('super_user', None)

        auth_parser.main(['-u', 'super_user', '-p' 'password'])
        store_m.assert_called_with('super_user', 'password')

    def test_main_exceptions(self, store_m):
        """ Test main function error cases """

        store_m.side_effect = iotlabcli.Error('message')
        self.assertRaises(SystemExit, auth_parser.main, ['-u', 'error'])

        store_m.side_effect = KeyboardInterrupt()
        self.assertRaises(SystemExit, auth_parser.main, ['-u', 'ctrl_c'])
