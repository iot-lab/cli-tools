# -*- coding: utf-8 -*-

""" Test the iotlabcli.parser.auth module """

import sys
import unittest
from iotlabcli.tests import patch

import iotlabcli.parser.auth as auth_parser

# pylint: disable=missing-docstring,too-many-public-methods


@patch('sys.stderr', sys.stdout)
@patch('iotlabcli.auth.write_password_file')
class TestMainAuthParser(unittest.TestCase):
    @patch('getpass.getpass')
    def test_main(self, getpass_m, store_m):
        """ Test parser.auth.main function """
        store_m.return_value = 'Written'
        getpass_m.return_value = 'password2'

        with patch('iotlabcli.auth.Api') as api_class:
            api = api_class.return_value

            api.check_credential.return_value = True

            auth_parser.main(['-u', 'super_user', '-p' 'password'])
            store_m.assert_called_with('super_user', 'password')
            self.assertFalse(getpass_m.called)

            getpass_m.reset_mock()
            store_m.reset_mock()
            api.check_credential.return_value = False
            self.assertRaises(SystemExit, auth_parser.main,
                              ['-u', 'super_user'])
            self.assertTrue(getpass_m.called)
            self.assertEqual(0, store_m.call_count)

    def test_main_exceptions(self, store_m):
        """ Test parser.auth.main error cases """

        store_m.side_effect = IOError('message')
        self.assertRaises(SystemExit, auth_parser.main,
                          ['-u', 'error', '-p', 'password'])

        store_m.side_effect = KeyboardInterrupt()
        self.assertRaises(SystemExit, auth_parser.main,
                          ['-u', 'ctrl_c', '-p', 'password'])
