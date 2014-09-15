# -*- coding: utf-8 -*-

""" Test the iotlabcli.parser.auth module """

import sys
import unittest
from mock import patch

import iotlabcli
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

        auth_parser.main(['-u', 'super_user', '-p' 'password'])
        store_m.assert_called_with('super_user', 'password')
        self.assertFalse(getpass_m.called)

        auth_parser.main(['-u', 'super_user'])
        store_m.assert_called_with('super_user', 'password2')
        self.assertTrue(getpass_m.called)

    def test_main_exceptions(self, store_m):
        """ Test parser.auth.main error cases """

        store_m.side_effect = iotlabcli.Error('message')
        self.assertRaises(SystemExit, auth_parser.main,
                          ['-u', 'error', '-p', 'password'])

        store_m.side_effect = KeyboardInterrupt()
        self.assertRaises(SystemExit, auth_parser.main,
                          ['-u', 'ctrl_c', '-p', 'password'])
