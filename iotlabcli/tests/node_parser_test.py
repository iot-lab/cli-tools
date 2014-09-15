# -*- coding: utf-8 -*-

""" Test the iotlabcli.parser.node module """

import unittest
import mock
from iotlabcli.parser import node
from iotlabcli.tests.main_mock import MainMock

# pylint: disable=missing-docstring,too-many-public-methods,maybe-no-member
# pylint: disable=too-many-arguments

# TODO remove 'api' checks from here


@mock.patch('iotlabcli.node.node_command')
@mock.patch('iotlabcli.parser.node.list_nodes')
class TestMainNodeParser(MainMock):
    def test_main(self, list_nodes, node_command):
        """ Run the parser.node.main function """
        api = self.api_class.return_value
        node_command.return_value = {'result': 'test'}

        list_nodes.return_value = []
        # start
        args = ['--start']
        node.main(args)
        list_nodes.assert_called_with(api, 123, None, None)
        node_command.assert_called_with(api, 'start', 123, [], None)
        # stop
        args = ['--stop']
        node.main(args)
        list_nodes.assert_called_with(api, 123, None, None)
        node_command.assert_called_with(api, 'stop', 123, [], None)

        # Reset command with many arguments
        args = ['--reset', '-l', 'grenoble,m3,1-2', '-l', 'grenoble,m3,3']
        list_nodes.return_value = ['m3-1', 'm3-2', 'm3-3']  # simplify
        node.main(args)
        list_nodes.assert_called_with(
            api, 123,
            [['m3-1.grenoble.iot-lab.info', 'm3-2.grenoble.iot-lab.info'],
             ['m3-3.grenoble.iot-lab.info']], None)
        node_command.assert_called_with(
            api, 'reset', 123, ['m3-1', 'm3-2', 'm3-3'], None)

        # update with exclude list
        args = ['--update', 'tp.elf', '-e', 'grenoble,m3,1-2']
        list_nodes.return_value = ['m3-3']  # simplify
        node.main(args)
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
            "items": [
                {"network_address": "m3-1.grenoble.iot-lab.info"},
                {"network_address": "m3-2.grenoble.iot-lab.info"},
                {"network_address": "m3-3.grenoble.iot-lab.info"},
                {"network_address": "m3-1.strasbourg.iot-lab.info"},
                {"network_address": "m3-2.strasbourg.iot-lab.info"},
                {"network_address": "m3-3.strasbourg.iot-lab.info"},
            ]
        }

        nodes_ll = [
            ["m3-1.grenoble.iot-lab.info", "m3-2.grenoble.iot-lab.info"],
            ["m3-1.strasbourg.iot-lab.info", "m3-2.strasbourg.iot-lab.info"],
        ]

        # No nodes provided => all nodes, no external requests
        res = node.list_nodes(api, 123)
        self.assertEquals(res, [])
        self.assertEquals(0, api.get_experiment_resources.call_count)

        # Normal case, no external requests, only list of all provided nodes
        res = node.list_nodes(api, 123, nodes_ll=nodes_ll)
        self.assertEquals(res, ["m3-1.grenoble.iot-lab.info",
                                "m3-2.grenoble.iot-lab.info",
                                "m3-1.strasbourg.iot-lab.info",
                                "m3-2.strasbourg.iot-lab.info"])
        self.assertEquals(0, api.get_experiment_resources.call_count)

        res = node.list_nodes(api, 123, excl_nodes_ll=nodes_ll)
        self.assertEquals(res, ["m3-3.grenoble.iot-lab.info",
                                "m3-3.strasbourg.iot-lab.info"])
        self.assertEquals(1, api.get_experiment_resources.call_count)
