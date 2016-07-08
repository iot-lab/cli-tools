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

""" Test the iotlabcli.node module """

# pylint: disable=too-many-public-methods
# Issues with 'mock'
# pylint: disable=no-member
import unittest

from iotlabcli import node
from iotlabcli.tests import my_mock

from .c23 import patch


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
        self.assertEqual(my_mock.API_RET, res)
        api.node_command.assert_called_with('start', 123, nodes_list)

        api.reset_mock()
        res = node.node_command(api, 'stop', 123, nodes_list)
        self.assertEqual(my_mock.API_RET, res)
        api.node_command.assert_called_with('stop', 123, nodes_list)

        api.reset_mock()
        res = node.node_command(api, 'reset', 123, nodes_list)
        self.assertEqual(my_mock.API_RET, res)
        api.node_command.assert_called_with('reset', 123, nodes_list)

        api.reset_mock()
        res = node.node_command(api, 'profile', 123, nodes_list, 'p_m3')
        self.assertEqual(my_mock.API_RET, res)
        api.node_command.assert_called_with('profile', 123, nodes_list,
                                            '&name=p_m3')

        api.reset_mock()
        res = node.node_command(api, 'update', 123, nodes_list,
                                '~/../filename.elf')
        self.assertEqual(my_mock.API_RET, res)
        self.assertEqual(1, api.node_update.call_count)
        api.node_update.assert_called_with(123, {
            "filename.elf": "file_data",
            'nodes.json': '["m3-1", "m3-2", "m3-3"]',
        })

        # no firmware for update command
        self.assertRaises(AssertionError, node.node_command,
                          api, 'update', 123, nodes_list)
