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

"""Test the iotlabcli.admin module."""

# pylint:disable=attribute-defined-outside-init
# pylint:disable=invalid-name

import unittest

from iotlabcli import admin

from .c23 import patch


class TestAdminWaitUserExperiment(unittest.TestCase):
    """Test admin.wait_user_experiment."""

    def setUp(self):
        exp_mock = patch('iotlabcli.rest.Api.get_any_experiment_state')
        self._get_exp = exp_mock.start()

        self._states = []
        self._get_exp.side_effect = self._get_exp_method

    def tearDown(self):
        patch.stopall()

    def _get_exp_method(self, *_):
        """Get any exp mock"""
        try:
            state = self._states.pop(0)
        except IndexError:
            state = self._last_state
        return {'state': state}

    def test_admin_wait_user_experiment(self):
        """Test wait_user_experiment starting."""
        # Waiting -> Launching -> Running
        self._states = ['Waiting', 'Launching']
        self._last_state = 'Running'

        # Starting experiment
        ret = admin.wait_user_experiment(123, 'harter', step=0)
        self.assertEqual(ret, 'Running')
        self._get_exp.assert_called_with(123, 'harter')
        self.assertEqual(self._get_exp.call_count, 3)

    def test_admin_wait_user_experiment_error(self):
        """Test wait_user_experiment starting to error."""
        # Waiting -> Launching -> Error
        self._states = ['Waiting', 'Launching']
        self._last_state = 'Error'

        # Directly to error
        self.assertRaises(RuntimeError,
                          admin.wait_user_experiment, 123, 'harter', step=0)
        self._get_exp.assert_called_with(123, 'harter')
        self.assertEqual(self._get_exp.call_count, 3)
