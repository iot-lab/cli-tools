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

""" Test the iotlabcli.status module """

# pylint: disable=too-many-public-methods
# Issues with 'mock'
# pylint: disable=no-member,maybe-no-member
import unittest

from iotlabcli import status
from iotlabcli.tests import my_mock


class TestStatus(unittest.TestCase):
    """ Test the 'iotlabcli.status' module """
    def tearDown(self):
        my_mock.api_mock_stop()

    def test_status_command(self):
        """ Test 'status_command' """

        api = my_mock.api_mock()

        api.reset_mock()
        res = status.status_command(api, 'sites')
        self.assertEqual(my_mock.API_RET, res)
        api.get_sites_details.assert_called()

        api.reset_mock()
        res = status.status_command(api, 'nodes')
        self.assertEqual(my_mock.API_RET, res)
        api.get_nodes.assert_called()

        api.reset_mock()
        res = status.status_command(api, 'nodes-ids', site='grenoble')
        self.assertEqual(my_mock.API_RET, res)
        api.get_nodes.assert_called_with(list_id=True, site='grenoble')

        api.reset_mock()
        res = status.status_command(api, 'experiments')
        self.assertEqual(my_mock.API_RET, res)
        api.get_running_experiments.assert_called()
