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


""" Test the iotlabcli.parser.robot module """

import iotlabcli.parser.robot as robot_parser
from iotlabcli.tests.my_mock import MainMock

from .c23 import patch

# pylint: disable=too-many-public-methods
# pylint: disable=too-few-public-methods


class TestMainRobotParser(MainMock):
    """Test the robot-cli main parser."""

    @patch('iotlabcli.robot.robot_command')
    @patch('iotlabcli.parser.common.list_nodes')
    def test_main_status(self, list_nodes, robot_command):
        """Run the parser.robot.main function for status commands."""
        robot_command.return_value = {'result': 'test'}

        list_nodes.return_value = []
        args = ['status']
        robot_parser.main(args)
        list_nodes.assert_called_with(self.api, 123, None, None)
        robot_command.assert_called_with(self.api, 'status', 123, [])

        args = ['status', '-l', 'grenoble,m3,1-2', '-l', 'grenoble,m3,3']
        list_nodes.return_value = ['m3-1', 'm3-2', 'm3-3']  # simplify
        robot_parser.main(args)
        robot_command.assert_called_with(self.api, 'status', 123,
                                         ['m3-1', 'm3-2', 'm3-3'])

    @patch('iotlabcli.robot.robot_update_mobility')
    @patch('iotlabcli.parser.common.list_nodes')
    def test_main_update(self, list_nodes, robot_update_mobility):
        """Run the parser.robot.main function for update commands."""
        robot_update_mobility.return_value = {'result': 'test'}

        list_nodes.return_value = []
        args = ['update', 'traj,grenoble']
        robot_parser.main(args)
        list_nodes.assert_called_with(self.api, 123, None, None)
        robot_update_mobility.assert_called_with(
            self.api, 123, 'traj', 'grenoble', [])

        # Invalid mobility format
        robot_update_mobility.reset_mock()
        args = ['update', 'traj',
                '-l', 'grenoble,m3,1-2',
                '-l', 'grenoble,m3,3']
        self.assertRaises(SystemExit, robot_parser.main, args)
        self.assertFalse(robot_update_mobility.called)

    @patch('iotlabcli.robot.mobility_command')
    def test_main_mobility(self, mobility_command):
        """Run the parser.robot.main function for mobility commands."""
        mobility_command.return_value = {'result': 'test'}

        # List mobility
        args = ['get', '--list']
        robot_parser.main(args)
        mobility_command.assert_called_with(self.api, 'list')

        # Get mobility
        args = ['get', '-n', 'traj_name,site_name']
        robot_parser.main(args)
        mobility_command.assert_called_with(self.api, 'get',
                                            ('traj_name', 'site_name'))
