# -*- coding: utf-8 -*-

""" Test the iotlabcli.parser.robot module """

from iotlabcli.tests import patch

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
        args = ['--status']
        robot_parser.main(args)
        list_nodes.assert_called_with(self.api, 123, None, None)
        robot_command.assert_called_with(self.api, 'status', 123, [])

        args = ['-s', '-l', 'grenoble,m3,1-2', '-l', 'grenoble,m3,3']
        list_nodes.return_value = ['m3-1', 'm3-2', 'm3-3']  # simplify
        robot_parser.main(args)
        robot_command.assert_called_with(self.api, 'status', 123,
                                         ['m3-1', 'm3-2', 'm3-3'])
