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

from .c23 import patch

import iotlabcli.parser.robot as robot_parser
from iotlabcli.tests.my_mock import MainMock

# pylint: disable=too-many-public-methods
# pylint: disable=too-few-public-methods


@patch('iotlabcli.robot.robot_command')
@patch('iotlabcli.parser.common.list_nodes')
class TestMainRobotParser(MainMock):
    """ Test the robot-cli main parser """

    def test_main(self, list_nodes, robot_command):
        """ Run the parser.robot.main function """
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
