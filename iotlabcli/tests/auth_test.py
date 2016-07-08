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

""" Test the iotlabcli.auth module """

# pylint:disable=too-many-public-methods

import os
import unittest

from iotlabcli import auth

from .c23 import patch, mock_open

TEST_RC_FILE = 'test_iotlabrc_file'


class TestAuthModule(unittest.TestCase):
    """ Test the experiment.auth module """
    def setUp(self):
        try:
            os.remove(TEST_RC_FILE)
        except OSError:
            pass
        patch('iotlabcli.auth.RC_FILE', TEST_RC_FILE).start()
        self.passwords = []
        m_getpass = patch('getpass.getpass').start()
        m_getpass.side_effect = self.getpass

    def tearDown(self):
        try:
            os.remove(TEST_RC_FILE)
        except OSError:
            pass
        patch.stopall()

    def getpass(self):
        """ Getpass mock """
        return self.passwords.pop()

    def test_write_then_read(self):
        """ Test writing auth then reading it back """
        # pylint: disable=protected-access
        auth.write_password_file('username', 'password')
        self.assertEqual(('username', 'password'),
                         auth.get_user_credentials())

    def test_read_with_no_file(self):
        """ Test reading password with no file """
        # pylint: disable=protected-access
        self.assertEqual((None, None), auth._read_password_file())

    @patch('iotlabcli.auth._read_password_file')
    def test_get_user_credentials(self, m_read):
        """ Test auth.get_user_credentials """
        m_read.return_value = ('super_user', 'super_passwd')
        # passwords given
        self.assertEqual(('user', 'passwd'),
                         auth.get_user_credentials('user', 'passwd'))
        self.passwords = ['password_prompt']
        self.assertEqual(('user', 'password_prompt'),
                         auth.get_user_credentials('user'))

        self.assertEqual(('super_user', 'super_passwd'),
                         auth.get_user_credentials())

    def test_error__read_password_file(self):
        """ Test Error while reading password file """
        # pylint: disable=protected-access
        open_name = 'iotlabcli.auth.open'
        m_open = mock_open(read_data='invalid_format:paswd:third_field')
        open(TEST_RC_FILE, 'wb').close()
        with patch(open_name, m_open, create=True):
            self.assertRaises(ValueError, auth._read_password_file)

    @patch('iotlabcli.auth.Api')
    def test_check_user_credentials(self, m_api_class):
        """ Check the check_user_credentials function """
        api = m_api_class.return_value
        api.check_credential.return_value = True
        self.assertEqual(True, auth.check_user_credentials('user', 'password'))
