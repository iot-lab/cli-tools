# -*- coding: utf-8 -*-

""" common TestCase class  for testing main parsers """
import sys
import unittest
try:
    # pylint: disable=import-error,no-name-in-module
    from mock import patch, Mock
except ImportError:  # pragma: no cover
    # pylint: disable=import-error,no-name-in-module
    from unittest.mock import patch, Mock


class MainMock(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """ Common mock needed for testing main function of parsers """
    def setUp(self):
        self.api = patch('iotlabcli.rest.Api').start().return_value

        patch('sys.stderr', sys.stdout).start()
        patch('iotlabcli.parser.common.sites_list', Mock(
            return_value=['grenoble', 'strasbourg', 'euratech'])).start()

        patch('iotlabcli.auth.get_user_credentials',
              Mock(return_value=('username', 'password'))).start()

        patch('iotlabcli.helpers.get_current_experiment',
              (lambda a, x: 123 if x is None else x)).start()

    def tearDown(self):
        patch.stopall()
