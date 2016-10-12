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

"""Test iotlabcli.parser.admin module."""

import sys
import unittest

import iotlabcli.parser.admin as admin_parser

from .c23 import patch


class TestWaitParser(unittest.TestCase):
    """Test wait.parser."""

    @patch('iotlabcli.admin.wait_user_experiment')
    def test_wait_experiment_parser(self, wait_user_exp):
        """Test wait_experiment_parser."""

        wait_user_exp.return_value = 'Running'
        with patch('sys.stderr', sys.stdout):
            admin_parser.main(['wait', '-i', '123', '--exp-user', 'harter'])

        wait_user_exp.assert_called_with(123, 'harter',
                                         'Running', 5, float('+inf'))
        self.assertEqual(wait_user_exp.call_count, 1)

        wait_user_exp.reset_mock()
        wait_user_exp.return_value = 'Terminated'
        with patch('sys.stderr', sys.stdout):
            admin_parser.main(['wait', '--id', '123', '--exp-user', 'harter',
                               '--state', 'Terminated,Error',
                               '--step', '10',
                               '--timeout', '100'])

        wait_user_exp.assert_called_with(123, 'harter',
                                         'Terminated,Error', 10, 100.0)
        self.assertEqual(wait_user_exp.call_count, 1)
