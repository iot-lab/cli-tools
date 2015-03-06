# -*- coding: utf-8 -*-

""" Test the iotlabcli.parser.common module """
# pylint: disable=too-many-public-methods

import unittest
import sys
import argparse
from iotlabcli.parser import common
from iotlabcli.tests.my_mock import api_mock, api_mock_stop

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


class TestNodeSelectionParser(unittest.TestCase):
    """ Test the common '-l' '-e' options node selection parser """
    def tearDown(self):
        api_mock_stop()

    @patch('iotlabcli.parser.common._get_experiment_nodes_list')
    def test_list_nodes(self, g_nodes_list):
        """ Run the different list_nodes cases """
        api = api_mock()
        g_nodes_list.return_value = [
            "m3-1.grenoble.iot-lab.info", "m3-2.grenoble.iot-lab.info",
            "m3-3.grenoble.iot-lab.info",
            "m3-1.strasbourg.iot-lab.info", "m3-2.strasbourg.iot-lab.info",
            "m3-3.strasbourg.iot-lab.info"
        ]

        nodes_ll = [
            ["m3-1.grenoble.iot-lab.info", "m3-2.grenoble.iot-lab.info"],
            ["m3-1.strasbourg.iot-lab.info", "m3-2.strasbourg.iot-lab.info"],
        ]

        # No nodes provided => all nodes, no external requests
        res = common.list_nodes(api, 123)
        self.assertEquals(res, [])
        self.assertFalse(g_nodes_list.called)

        # Normal case, no external requests, only list of all provided nodes
        res = common.list_nodes(api, 123, nodes_ll=nodes_ll)
        self.assertEquals(res, ["m3-1.grenoble.iot-lab.info",
                                "m3-2.grenoble.iot-lab.info",
                                "m3-1.strasbourg.iot-lab.info",
                                "m3-2.strasbourg.iot-lab.info"])
        self.assertFalse(g_nodes_list.called)

        res = common.list_nodes(api, 123, excl_nodes_ll=nodes_ll)
        self.assertEquals(res, ["m3-3.grenoble.iot-lab.info",
                                "m3-3.strasbourg.iot-lab.info"])
        self.assertTrue(g_nodes_list.called)

    def test__get_experiment_nodes_list(self):
        """ Run get_experiment_nodes_list """
        api = api_mock(
            ret={
                "items": [
                    {"network_address": "m3-1.grenoble.iot-lab.info"},
                    {"network_address": "m3-2.grenoble.iot-lab.info"},
                    {"network_address": "m3-3.grenoble.iot-lab.info"},
                ]
            }
        )
        # pylint: disable=protected-access
        self.assertEquals(common._get_experiment_nodes_list(api, 3),
                          ["m3-1.grenoble.iot-lab.info",
                           "m3-2.grenoble.iot-lab.info",
                           "m3-3.grenoble.iot-lab.info"])

    @patch('iotlabcli.parser.common.check_site_with_server')
    def test_nodes_list_from_str(self, _):
        """ Run error case from test_nodes_list_from_str invalid string """

        self.assertRaises(argparse.ArgumentTypeError,
                          common.nodes_list_from_str, 'grenoble,m3_no_numbers')
