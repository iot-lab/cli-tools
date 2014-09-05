# -*- coding: utf-8 -*-

""" Test the iotlabcli.node_parser module """

import sys
import unittest
import mock
from iotlabcli import node_parser
from iotlabcli import Error


@mock.patch('sys.stderr', sys.stdout)
@mock.patch('iotlabcli.helpers.get_user_credentials')
@mock.patch('iotlabcli.helpers.get_current_experiment')
@mock.patch('iotlabcli.rest.Api')
@mock.patch('iotlabcli.parser_common.Singleton')
@mock.patch('iotlabcli.node_parser.node_command')
@mock.patch('iotlabcli.node_parser.list_nodes')
class TestMainNodeParser(unittest.TestCase):
    def test_main(self, list_nodes, node_command, platform_class,
                  api_class, cur_exp, get_credentials):
        """ Run the main function """
        api = api_class.return_value
        platform_class.return_value.sites.return_value = [
            'grenoble', 'strasbourg', 'euratech']
        # simplify return value, use same cli parameters for correctness
        get_credentials.return_value = 'username', 'password'
        cur_exp.return_value = 123
        node_command.return_value = {'result': 'test'}

        list_nodes.return_value = []
        # start
        args = ['--start']
        node_parser.main(args)
        list_nodes.assert_called_with(api, 123, None, None)
        node_command.assert_called_with(api, 'start', 123, [], None)
        # stop
        args = ['--stop']
        node_parser.main(args)
        list_nodes.assert_called_with(api, 123, None, None)
        node_command.assert_called_with(api, 'stop', 123, [], None)

        # Reset command with many arguments
        args = ['--reset', '-l', 'grenoble,m3,1-2', '-l', 'grenoble,m3,3']
        list_nodes.return_value = ['m3-1', 'm3-2', 'm3-3']  # simplify
        node_parser.main(args)
        list_nodes.assert_called_with(
            api, 123,
            [['m3-1.grenoble.iot-lab.info', 'm3-2.grenoble.iot-lab.info'],
             ['m3-3.grenoble.iot-lab.info']], None)
        node_command.assert_called_with(
            api, 'reset', 123, ['m3-1', 'm3-2', 'm3-3'], None)

        # update with exclude list
        args = ['--update', 'tp.elf', '-e', 'grenoble,m3,1-2']
        list_nodes.return_value = ['m3-3']  # simplify
        node_parser.main(args)
        list_nodes.assert_called_with(
            api, 123, None,
            [['m3-1.grenoble.iot-lab.info', 'm3-2.grenoble.iot-lab.info']])
        node_command.assert_called_with(
            api, 'update', 123, ['m3-3'], 'tp.elf')


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
        """ Test 'node_command' """

        nodes_list = ["m3-1", "m3-2", "m3-3"]
        open_file_mock.return_value = ("filename", "file_data")

        _api_result = {'result': 'test'}
        api = mock.Mock()
        api.node_command.return_value = _api_result
        api.node_update.return_value = _api_result

        api.reset_mock()
        res = node_parser.node_command(api, 'start', 123, nodes_list)
        self.assertEquals(_api_result, res)
        api.node_command.assert_called_with('start', 123, nodes_list)

        api.reset_mock()
        res = node_parser.node_command(api, 'stop', 123, nodes_list)
        self.assertEquals(_api_result, res)
        api.node_command.assert_called_with('stop', 123, nodes_list)

        api.reset_mock()
        res = node_parser.node_command(api, 'reset', 123, nodes_list)
        self.assertEquals(_api_result, res)
        api.node_command.assert_called_with('reset', 123, nodes_list)

        api.reset_mock()
        res = node_parser.node_command(api, 'update', 123, nodes_list,
                                       'firmware_path')
        self.assertEquals(_api_result, res)
        self.assertEquals(1, api.node_update.call_count)
        api.node_update.assert_called_with(123, {
            "filename": "file_data",
            'nodes.json': '["m3-1", "m3-2", "m3-3"]',
        })

        # no firmware for update command
        self.assertRaises(Error, node_parser.node_command,
                          api, 'update', 123, nodes_list)
