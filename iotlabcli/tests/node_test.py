# -*- coding: utf-8 -*-

""" Test the iotlabcli.node module """

# pylint: disable=too-many-public-methods
import unittest
from iotlabcli.tests import patch
from iotlabcli import node
from iotlabcli.tests import my_mock


class TestNode(unittest.TestCase):
    """ Test the 'iotlabcli.node' module """
    def tearDown(self):
        my_mock.api_mock_stop()

    @patch('iotlabcli.helpers.read_file')
    def test_node_command(self, read_file_mock):
        """ Test 'node_command' """

        nodes_list = ["m3-1", "m3-2", "m3-3"]
        read_file_mock.return_value = 'file_data'

        api = my_mock.api_mock()

        api.reset_mock()
        res = node.node_command(api, 'start', 123, nodes_list)
        self.assertEquals(my_mock.API_RET, res)
        api.node_command.assert_called_with('start', 123, nodes_list)

        api.reset_mock()
        res = node.node_command(api, 'stop', 123, nodes_list)
        self.assertEquals(my_mock.API_RET, res)
        api.node_command.assert_called_with('stop', 123, nodes_list)

        api.reset_mock()
        res = node.node_command(api, 'reset', 123, nodes_list)
        self.assertEquals(my_mock.API_RET, res)
        api.node_command.assert_called_with('reset', 123, nodes_list)

        api.reset_mock()
        res = node.node_command(api, 'update', 123, nodes_list,
                                '~/../filename.elf')
        self.assertEquals(my_mock.API_RET, res)
        self.assertEquals(1, api.node_update.call_count)
        api.node_update.assert_called_with(123, {
            "filename.elf": "file_data",
            'nodes.json': '["m3-1", "m3-2", "m3-3"]',
        })

        # no firmware for update command
        self.assertRaises(AssertionError, node.node_command,
                          api, 'update', 123, nodes_list)
