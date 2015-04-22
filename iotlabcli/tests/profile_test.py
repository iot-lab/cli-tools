# -*- coding: utf-8 -*-

""" Test the iotlabcli.module """
# pylint:disable=missing-docstring,too-many-public-methods

import unittest
from iotlabcli import profile


class TestM3Profile(unittest.TestCase):

    def test_valid_full_profile_rssi(self):
        m3_prof = profile.ProfileM3('name', 'dc')
        m3_prof.set_consumption(140, 1, True, True, True)
        m3_prof.set_radio('rssi', (11, 12, 13), period=1, num_per_channel=1)
        m3_prof.mobility = None

        self.assertEquals(
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
                'mobility': None,
            }
        )

        # Test with default values for num_per_channel
        m3_prof = profile.ProfileM3('name', 'dc')
        m3_prof.set_consumption(None, None)
        m3_prof.set_radio('rssi', (26,), period=42)
        self.assertEquals(
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
                'mobility': None,
            }
        )

    def test_valid_sniffer_profile(self):
        m3_prof = profile.ProfileM3('sniff_11', 'dc')
        m3_prof.set_consumption(None, None)
        m3_prof.set_radio('sniffer', (11,))
        m3_prof.mobility = None

        self.assertEquals(
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
                'mobility': None,
            }
        )

    def test_valid_mobility_profile(self):
        circuit = {
            "coordinates": [
                {"name": "0", "w": 0.0, "x": 40.6, "y": 34.2, "z": 0.0},
                {"name": "1", "w": 3.14, "x": 59.4, "y": 34.2, "z": 0.0},
                {"name": "3", "w": 3.14, "x": 40.6, "y": 34.2, "z": 0.0},
                {"name": "2", "w": 0.0, "x": 17.5, "y": 34.2, "z": 0.0},
            ],
            "points": ["0", "1", "3", "2"],
            "site_name": "devgrenoble",
            "trajectory_name": "Jhall",
        }

        m3_prof = profile.ProfileM3('name', 'dc')
        m3_prof.set_consumption(None, None)
        m3_prof.set_radio(mode=None, channels=None)
        m3_prof.mobility = circuit

        self.assertEquals(
            m3_prof.__dict__,
            {
                'power': 'dc',
                'profilename': 'name',
                'nodearch': 'm3',
                'consumption': None,
                'radio': None,
                'mobility': circuit,
            }
        )

    def test_valid_empty_profile(self):
        m3_prof = profile.ProfileM3('name', 'dc')
        m3_prof.set_consumption(None, None)
        m3_prof.set_radio(mode=None, channels=None)
        m3_prof.mobility = None

        self.assertEquals(
            m3_prof.__dict__,
            {
                'power': 'dc',
                'profilename': 'name',
                'nodearch': 'm3',
                'consumption': None,
                'radio': None,
                'mobility': None,
            }
        )


class TestWSN430Profile(unittest.TestCase):

    def test_valid_full_profile(self):
        wsn430_prof = profile.ProfileWSN430('name', 'dc')
        wsn430_prof.set_consumption(5000, True, True, True)
        wsn430_prof.set_radio(5000)
        wsn430_prof.set_sensors(30000, True, True)

        self.assertEquals(
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

        self.assertEquals(
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
