# -*- coding: utf-8 -*-

""" Test the iotlabcli.parser.node module """

import unittest
from iotlabcli.tests import patch

from argparse import ArgumentTypeError
import iotlabcli.parser.node as node_parser
from iotlabcli.tests.my_mock import MainMock, api_mock, api_mock_stop

# pylint: disable=missing-docstring,too-many-public-methods
# pylint: disable=too-few-public-methods


@patch('iotlabcli.node.node_command')
@patch('iotlabcli.parser.node.list_nodes')
class TestMainNodeParser(MainMock):
    def test_main(self, list_nodes, node_command):
        """ Run the parser.node.main function """
        node_command.return_value = {'result': 'test'}

        list_nodes.return_value = []
        # start
        args = ['--start']
        node_parser.main(args)
        list_nodes.assert_called_with(self.api, 123, None, None)
        node_command.assert_called_with(self.api, 'start', 123, [], None)
        # stop
        args = ['--stop']
        node_parser.main(args)
        list_nodes.assert_called_with(self.api, 123, None, None)
        node_command.assert_called_with(self.api, 'stop', 123, [], None)

        # Reset command with many arguments
        args = ['--reset', '-l', 'grenoble,m3,1-2', '-l', 'grenoble,m3,3']
        list_nodes.return_value = ['m3-1', 'm3-2', 'm3-3']  # simplify
        node_parser.main(args)
        list_nodes.assert_called_with(
            self.api, 123,
            [['m3-1.grenoble.iot-lab.info', 'm3-2.grenoble.iot-lab.info'],
             ['m3-3.grenoble.iot-lab.info']], None)
        node_command.assert_called_with(
            self.api, 'reset', 123, ['m3-1', 'm3-2', 'm3-3'], None)

        # update with exclude list
        args = ['--update', 'tp.elf', '-e', 'grenoble,m3,1-2']
        list_nodes.return_value = ['m3-3']  # simplify
        node_parser.main(args)
        list_nodes.assert_called_with(
            self.api, 123, None,
            [['m3-1.grenoble.iot-lab.info', 'm3-2.grenoble.iot-lab.info']])
        node_command.assert_called_with(
            self.api, 'update', 123, ['m3-3'], 'tp.elf')


class TestNodeParser(unittest.TestCase):
    def tearDown(self):
        api_mock_stop()

    @patch('iotlabcli.parser.node._get_experiment_nodes_list')
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
        res = node_parser.list_nodes(api, 123)
        self.assertEquals(res, [])
        self.assertFalse(g_nodes_list.called)

        # Normal case, no external requests, only list of all provided nodes
        res = node_parser.list_nodes(api, 123, nodes_ll=nodes_ll)
        self.assertEquals(res, ["m3-1.grenoble.iot-lab.info",
                                "m3-2.grenoble.iot-lab.info",
                                "m3-1.strasbourg.iot-lab.info",
                                "m3-2.strasbourg.iot-lab.info"])
        self.assertFalse(g_nodes_list.called)

        res = node_parser.list_nodes(api, 123, excl_nodes_ll=nodes_ll)
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
        self.assertEquals(node_parser._get_experiment_nodes_list(api, 3),
                          ["m3-1.grenoble.iot-lab.info",
                           "m3-2.grenoble.iot-lab.info",
                           "m3-3.grenoble.iot-lab.info"])

    @patch('iotlabcli.parser.common.check_site_with_server')
    def test_nodes_list_from_str(self, _):
        """ Run error case from test_nodes_list_from_str invalid string """

        self.assertRaises(ArgumentTypeError, node_parser.nodes_list_from_str,
                          'grenoble,m3_no_numbers')
