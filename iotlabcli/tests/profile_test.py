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

""" Test the iotlabcli.module """
# pylint:disable=missing-docstring,too-many-public-methods

import unittest
from iotlabcli import profile


class TestM3Profile(unittest.TestCase):

    def test_valid_full_profile_rssi(self):
        m3_prof = profile.ProfileM3('name', 'dc')
        m3_prof.set_consumption(140, 1, True, True, True)
        m3_prof.set_radio('rssi', (11, 12, 13), period=1, num_per_channel=1)

        self.assertEqual(
            m3_prof.__dict__,
            {
                'power': 'dc',
                'profilename': 'name',
                'nodearch': 'm3',
                'radio': {
                    'channels': (11, 12, 13),
                    'num_per_channel': 1,
                    'mode': 'rssi',
                    'period': 1,
                },
                'consumption': {
                    'current': True,
                    'average': 1,
                    'period': 140,
                    'power': True,
                    'voltage': True,
                },
            }
        )

        # Test with default values for num_per_channel
        m3_prof = profile.ProfileM3('name', 'dc')
        m3_prof.set_consumption(None, None)
        m3_prof.set_radio('rssi', (26,), period=42)
        self.assertEqual(
            m3_prof.__dict__,
            {
                'power': 'dc',
                'profilename': 'name',
                'nodearch': 'm3',
                'radio': {
                    'channels': (26,),
                    'num_per_channel': 0,
                    'mode': 'rssi',
                    'period': 42,
                },
                'consumption': None,
            }
        )

    def test_valid_sniffer_profile(self):
        m3_prof = profile.ProfileM3('sniff_11', 'dc')
        m3_prof.set_consumption(None, None)
        m3_prof.set_radio('sniffer', (11,))

        self.assertEqual(
            m3_prof.__dict__,
            {
                'power': 'dc',
                'profilename': 'sniff_11',
                'nodearch': 'm3',
                'radio': {
                    'channels': (11,),
                    'mode': 'sniffer',
                    'num_per_channel': None,
                    'period': None,
                },
                'consumption': None,
            }
        )

    def test_valid_empty_profile(self):
        m3_prof = profile.ProfileM3('name', 'dc')
        m3_prof.set_consumption(None, None)
        m3_prof.set_radio(mode=None, channels=None)

        self.assertEqual(
            m3_prof.__dict__,
            {
                'power': 'dc',
                'profilename': 'name',
                'nodearch': 'm3',
                'consumption': None,
                'radio': None,
            }
        )


class TestWSN430Profile(unittest.TestCase):

    def test_valid_full_profile(self):
        wsn430_prof = profile.ProfileWSN430('name', 'dc')
        wsn430_prof.set_consumption(5000, True, True, True)
        wsn430_prof.set_radio(5000)
        wsn430_prof.set_sensors(30000, True, True)

        self.assertEqual(
            wsn430_prof.__dict__,
            {
                'profilename': 'name',
                'power': 'dc',
                'nodearch': 'wsn430',
                'consumption': {
                    'frequency': 5000,
                    'current': True,
                    'voltage': True,
                    'power': True,
                },
                'radio': {
                    'frequency': 5000,
                    'rssi': True,
                },
                'sensor': {
                    'frequency': 30000,
                    'luminosity': True,
                    'temperature': True,
                }
            }
        )

    def test_valid_empty_profile(self):
        wsn430_prof = profile.ProfileWSN430('name', 'dc')
        wsn430_prof.set_consumption(None)
        wsn430_prof.set_radio(frequency=None)
        wsn430_prof.set_sensors(None)

        self.assertEqual(
            wsn430_prof.__dict__,
            {
                'profilename': 'name',
                'power': 'dc',
                'nodearch': 'wsn430',
                'consumption': None,
                'radio': None,
                'sensor': None,
            }
        )
