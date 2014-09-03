# -*- coding: utf-8 -*-

""" Test the iotlabcli.node_parser module """

import sys
import unittest
import mock
from iotlabcli import node_parser
from iotlabcli import Error


class TestNodeParser(unittest.TestCase):
    def test_list_nodes(self):
        """ Run the different list_nodes cases """
        api = mock.Mock()
        api.get_experiment_resources.return_value = {
            "items": [{"network_address": "m3-1.grenoble.iot-lab.info"},
                      {"network_address": "m3-2.grenoble.iot-lab.info"},
                      {"network_address": "m3-3.grenoble.iot-lab.info"},
                      {"network_address": "m3-1.strasbourg.iot-lab.info"},
                      {"network_address": "m3-2.strasbourg.iot-lab.info"},
                      {"network_address": "m3-3.strasbourg.iot-lab.info"},
                      ]
        }

        nodes_list = [
            ["m3-1.grenoble.iot-lab.info", "m3-2.grenoble.iot-lab.info"],
            ["m3-1.strasbourg.iot-lab.info", "m3-2.strasbourg.iot-lab.info"],
        ]

        # No nodes provided => all nodes, no external requests
        res = node_parser.list_nodes(api, 123)
        self.assertEquals(res, [])
        self.assertEquals(0, api.get_experiment_resources.call_count)

        # Normal case, no external requests, only list of all provided nodes
        res = node_parser.list_nodes(api, 123, nodes_list=nodes_list)
        self.assertEquals(res, ["m3-1.grenoble.iot-lab.info",
                                "m3-2.grenoble.iot-lab.info",
                                "m3-1.strasbourg.iot-lab.info",
                                "m3-2.strasbourg.iot-lab.info"])
        self.assertEquals(0, api.get_experiment_resources.call_count)

        # Normal case, no external requests, only list of all provided nodes
        res = node_parser.list_nodes(api, 123, excl_nodes_list=nodes_list)
        self.assertEquals(res, ["m3-3.grenoble.iot-lab.info",
                                "m3-3.strasbourg.iot-lab.info"])
        self.assertEquals(1, api.get_experiment_resources.call_count)

    @mock.patch('iotlabcli.helpers.open_file')
    def test_node_command(self, open_file_mock):
        """ Run the different list_nodes cases """

        nodes_list = ["m3-1", "m3-2", "m3-3"]
        open_file_mock.return_value = ("filename", "file_data")

        _api_result = {'result': 'test'}
        api = mock.Mock()
        api.start_command.return_value = _api_result
        api.stop_command.return_value = _api_result
        api.reset_command.return_value = _api_result
        api.update_command.return_value = _api_result

        api.reset_mock()
        res = node_parser.node_command(api, 'start', 123, nodes_list)
        self.assertEquals(_api_result, res)
        self.assertEquals(1, api.start_command.call_count)

        api.reset_mock()
        res = node_parser.node_command(api, 'stop', 123, nodes_list)
        self.assertEquals(_api_result, res)
        self.assertEquals(1, api.stop_command.call_count)

        api.reset_mock()
        res = node_parser.node_command(api, 'reset', 123, nodes_list)
        self.assertEquals(_api_result, res)
        self.assertEquals(1, api.reset_command.call_count)

        api.reset_mock()
        res = node_parser.node_command(api, 'update', 123, nodes_list,
                                       'firmware_path')
        self.assertEquals(_api_result, res)
        self.assertEquals(1, api.update_command.call_count)
        api.update_command.assert_called_with(123, {
            "filename": "file_data",
            'nodes.json': '["m3-1", "m3-2", "m3-3"]',
        })

        # no firmware for update command
        self.assertRaises(Error, node_parser.node_command,
                          api, 'update', 123, nodes_list)

        # branch coverage, invalid command, empty result
        res = node_parser.node_command(api, 'invalid_cmd', 123, nodes_list)
        self.assertIsNone(res)
