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

""" Test the iotlabcli.parser.node module """

import iotlabcli.parser.node as node_parser
from iotlabcli.tests.my_mock import MainMock

from .c23 import patch

# pylint: disable=too-many-public-methods
# pylint: disable=too-few-public-methods


@patch('iotlabcli.node.node_command')
@patch('iotlabcli.parser.common.list_nodes')
class TestMainNodeParser(MainMock):
    """ Test node-cli main parser """
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

        # profile update
        args = ['--profile', 'profm3']
        node_parser.main(args)
        list_nodes.assert_called_with(self.api, 123, None, None)
        node_command.assert_called_with(self.api, 'profile', 123, [], 'profm3')

        # debug-start
        args = ['--debug-start']
        node_parser.main(args)
        list_nodes.assert_called_with(self.api, 123, None, None)
        node_command.assert_called_with(self.api, 'debug-start', 123, [], None)
        # debug-stop
        args = ['--debug-stop']
        node_parser.main(args)
        list_nodes.assert_called_with(self.api, 123, None, None)
        node_command.assert_called_with(self.api, 'debug-stop', 123, [], None)

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
