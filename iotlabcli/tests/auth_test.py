# -*- coding: utf-8 -*-
""" Test the iotlabcli.auth module """

# pylint:disable=too-many-public-methods

import os
import unittest
from iotlabcli.tests import patch, mock_open
from iotlabcli import auth

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
        self.assertEquals(('username', 'password'),
                          auth.get_user_credentials())

    def test_read_with_no_file(self):
        """ Test reading password with no file """
        # pylint: disable=protected-access
        self.assertEquals((None, None), auth._read_password_file())

    @patch('iotlabcli.auth._read_password_file')
    def test_get_user_credentials(self, m_read):
        """ Test auth.get_user_credentials """
        m_read.return_value = ('super_user', 'super_passwd')
        # passwords given
        self.assertEquals(('user', 'passwd'),
                          auth.get_user_credentials('user', 'passwd'))
        self.passwords = ['password_prompt']
        self.assertEquals(('user', 'password_prompt'),
                          auth.get_user_credentials('user'))

        self.assertEquals(('super_user', 'super_passwd'),
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
