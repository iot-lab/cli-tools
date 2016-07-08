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

""" Test the iotlabcli.parser.auth module """

import sys
import unittest

import iotlabcli.parser.auth as auth_parser
from .c23 import patch

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
        # Replacing 'side_effect'
        # pylint:disable=redefined-variable-type
        with patch('iotlabcli.auth.Api') as api_class:
            api = api_class.return_value
            api.check_credential.return_value = True

            store_m.side_effect = IOError('message')
            self.assertRaises(SystemExit, auth_parser.main,
                              ['-u', 'error', '-p', 'password'])

            store_m.side_effect = KeyboardInterrupt()
            self.assertRaises(SystemExit, auth_parser.main,
                              ['-u', 'ctrl_c', '-p', 'password'])
