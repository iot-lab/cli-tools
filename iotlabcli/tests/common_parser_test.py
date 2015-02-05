# -*- coding: utf-8 -*-

""" Test the iotlabcli.parser.common module """
# pylint: disable=too-many-public-methods

import unittest
import sys
from iotlabcli.parser import common

# pylint: disable=import-error,no-name-in-module
try:
    from mock import patch, Mock
except ImportError:  # pragma: no cover
    # pylint: disable=import-error,no-name-in-module
    from unittest.mock import patch, Mock
try:
    from urllib2 import HTTPError
except ImportError:  # pragma: no cover
    from urllib.error import HTTPError


class TestCommonParser(unittest.TestCase):
    """ Test the iotlab.parser.common module """

    @patch('iotlabcli.rest.Api.method')
    def test_sites_list(self, _method_get_sited):
        """ Run get_sites method """
        _method_get_sited.return_value = {
            "items": [{'site': 'grenoble'}, {'site': 'strasbourg'}]
        }

        self.assertEquals(['grenoble', 'strasbourg'], common.sites_list())
        self.assertEquals(['grenoble', 'strasbourg'], common.sites_list())
        self.assertEquals(1, _method_get_sited.call_count)

    def test_main_cli(self):
        """ Run the main-cli function """
        function = Mock(return_value='{"result": 0}')
        parser = Mock()
        parser.error.side_effect = SystemExit

        common.main_cli(function, parser)

        function.side_effect = IOError()
        self.assertRaises(SystemExit, common.main_cli, function, parser)

        with patch('sys.stderr', sys.stdout):
            # HTTPError, both cases
            err = HTTPError(None, 401, 'msg', None, None)
            function.side_effect = err
            self.assertRaises(SystemExit, common.main_cli, function, parser)
            err = HTTPError(None, 200, 'msg', None, None)
            function.side_effect = err
            self.assertRaises(SystemExit, common.main_cli, function, parser)

            # Other exceptions
            function.side_effect = RuntimeError()
            self.assertRaises(SystemExit, common.main_cli, function, parser)

            function.side_effect = KeyboardInterrupt()
            self.assertRaises(SystemExit, common.main_cli, function, parser)
