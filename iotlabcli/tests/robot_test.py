# -*- coding: utf-8 -*-
""" Test the iotlabcli.robot module """

# pylint: disable=too-many-public-methods
import unittest
from iotlabcli import robot
from iotlabcli.tests import my_mock


class TestRobot(unittest.TestCase):
    """ Test the iotlabcli.node module """

    def tearDown(self):
        my_mock.api_mock_stop()

    def test_robot_command(self):
        """ Test 'robot_command' """

        api = my_mock.api_mock()

        nodes_list = ["m3-1", "m3-2", "m3-3"]
        api.reset_mock()
        res = robot.robot_command(api, 'status', 123, nodes_list)
        self.assertEquals(my_mock.API_RET, res)

        api.robot_command.assert_called_with('status', 123, nodes_list)
