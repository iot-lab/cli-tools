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

""" Test the iotlabcli.robot module """

# pylint: disable=too-many-public-methods
# Issues with 'mock'
# pylint: disable=no-member
import unittest
from iotlabcli import robot
from iotlabcli.tests import my_mock


class TestRobot(unittest.TestCase):
    """ Test the iotlabcli.node module """

    def setUp(self):
        self.api = my_mock.api_mock()

    def tearDown(self):
        my_mock.api_mock_stop()

    def test_robot_command(self):
        """Test 'robot_command'."""
        nodes_list = ["m3-1", "m3-2", "m3-3"]

        ret = robot.robot_command(self.api, 'status', 123, nodes_list)
        self.assertEqual(my_mock.API_RET, ret)

        self.api.robot_command.assert_called_with('status', 123, nodes_list)

    def test_robot_update_mobility(self):
        """Test robot_update_mobility."""
        nodes_list = ["m3-1", "m3-2", "m3-3"]

        # With site name
        ret = robot.robot_update_mobility(self.api, 123,
                                          'mob_name', 'grenoble', nodes_list)
        self.assertEqual(my_mock.API_RET, ret)
        self.api.robot_update_mobility.assert_called_with(
            123, 'mob_name', 'grenoble', nodes_list)

    def test_mobility_command(self):
        """Test 'mobility_command'."""

        # mobility-list
        ret = robot.mobility_command(self.api, 'list')
        self.assertEqual(my_mock.API_RET, ret)
        self.api.mobility_user_list.assert_called_with()
        self.api.reset_mock()

        # mobility-get
        ret = robot.mobility_command(self.api, 'get', ('m_name', 'm_site'))
        self.assertEqual(my_mock.API_RET, ret)
        self.api.mobility_user_get.assert_called_with('m_name', 'm_site')
        self.api.reset_mock()

    def test_robot_get_map(self):
        """Test robot_get_map."""
        ret = robot.robot_get_map('grenoble')
        self.assertEqual(sorted(ret.keys()), ['config', 'dock', 'image'])
        # Lazy to check calls to Api.method should use proxy to call it...
