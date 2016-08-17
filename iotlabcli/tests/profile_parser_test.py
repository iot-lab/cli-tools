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

""" Test the iotlabcli.parser.profile module """
# pylint:disable=missing-docstring,too-many-public-methods
# Mock object not being recognized
# pylint: disable=no-member

from iotlabcli.tests.my_mock import MainMock
import iotlabcli.parser.profile as profile_parser
import iotlabcli.profile as profile

from .c23 import patch


class TestMainProfileParser(MainMock):

    def test_main_add_parser(self):
        # add simple add
        profile_parser.main(['addwsn430', '-n', 'profile_name', '-p', 'dc'])
        self.api.add_profile.assert_called_with(
            'profile_name', profile.ProfileWSN430('profile_name', 'dc'))

        profile_parser.main(['addm3', '-n', 'profile_name', '-p', 'dc'])
        self.api.add_profile.assert_called_with(
            'profile_name', profile.ProfileM3('profile_name', 'dc'))

        profile_parser.main(['adda8', '-n', 'profile_name', '-p', 'dc'])
        self.api.add_profile.assert_called_with(
            'profile_name', profile.ProfileA8('profile_name', 'dc'))

        profile_parser.main(['addcustom', '-n', 'profile_name', '-p', 'dc'])
        self.api.add_profile.assert_called_with(
            'profile_name', profile.ProfileCustom('profile_name', 'dc'))

        # invalid configuration 'power' without period and average
        self.assertRaises(
            SystemExit, profile_parser.main,
            ['addm3', '-n', 'profile_name', '-p', 'dc', '-power'])

    @staticmethod
    @patch('iotlabcli.parser.profile.ProfileM3')
    def test_opts_parsing_m3(prof_m3_class):
        """ Test that M3profile parsing matches profile class
        Check that default values are ok and that values are correctly passed
        """
        # keep 'choices' valid for argparse
        prof_m3_class.choices = profile.ProfileM3.choices
        profilem3 = prof_m3_class.return_value
        parser = profile_parser.parse_options()

        args = ['addm3', '-n', 'name', '-p', 'dc']
        opts = parser.parse_args(args)
        profile_parser._m3_profile(opts)  # pylint: disable=protected-access
        profilem3.set_consumption.assert_called_with(
            period=None, average=None, power=False,
            voltage=False, current=False)
        profilem3.set_radio.assert_called_with(
            mode=None, channels=None, period=None, num_per_channel=None)

        # Test for RSSI
        args = ['addm3', '-n', 'name', '-p', 'dc']
        args += ['-period', '140', '-avg', '1',
                 '-power', '-voltage', '-current']
        args += ['-rssi', '-channels', '11', '12', '13',
                 '-num', '1', '-rperiod', '1']
        opts = parser.parse_args(args)
        profile_parser._m3_profile(opts)  # pylint: disable=protected-access
        profilem3.set_consumption.assert_called_with(
            period=140, average=1, power=True, voltage=True, current=True)
        profilem3.set_radio.assert_called_with(
            mode='rssi', channels=[11, 12, 13], period=1, num_per_channel=1)

        # Test for Radio Sniffer only
        args = ['addm3', '-n', 'name', '-p', 'dc']
        args += ['-sniffer', '-channels', '11']
        opts = parser.parse_args(args)
        profile_parser._m3_profile(opts)  # pylint: disable=protected-access
        profilem3.set_consumption.assert_called_with(
            period=None, average=None, power=False,
            voltage=False, current=False)
        profilem3.set_radio.assert_called_with(
            mode='sniffer', channels=[11], period=None, num_per_channel=None)

    @staticmethod
    @patch('iotlabcli.parser.profile.ProfileWSN430')
    def test_opts_parsing_wsn430(prof_wsn430_class):
        """ Test that WSN430profile parsing matches profile class
        Check that default values are ok and that values are correctly passed
        """
        # keep 'choices' valid for argparse
        prof_wsn430_class.choices = profile.ProfileWSN430.choices
        profilewsn430 = prof_wsn430_class.return_value
        parser = profile_parser.parse_options()

        # pylint: disable=protected-access
        args = ['addwsn430', '-n', 'name', '-p', 'dc']
        opts = parser.parse_args(args)
        profile_parser._wsn430_profile(opts)
        profilewsn430.set_consumption.assert_called_with(
            frequency=None, power=False, voltage=False, current=False)
        profilewsn430.set_radio.assert_called_with(frequency=None)
        profilewsn430.set_sensors.assert_called_with(
            frequency=None, temperature=False, luminosity=False)

        args += ['-cfreq', '70', '-power', '-voltage', '-current']
        args += ['-rfreq', '500']
        args += ['-sfreq', '1000', '-luminosity', '-temperature']
        opts = parser.parse_args(args)
        profile_parser._wsn430_profile(opts)
        profilewsn430.set_consumption.assert_called_with(
            frequency=70, power=True, voltage=True, current=True)
        profilewsn430.set_radio.assert_called_with(frequency=500)
        profilewsn430.set_sensors.assert_called_with(
            frequency=1000, temperature=True, luminosity=True)

    def test__add_profile(self):
        ret = profile_parser._add_profile(  # pylint: disable=protected-access
            self.api, 'name', {'test_profile': 1}, json_out=True)
        self.assertEqual(ret, {'test_profile': 1})
        self.assertFalse(self.api.add_profile.called)

    def test_main_get_parser(self):
        profile_parser.main(['get', '--name', 'profile_name'])
        self.api.get_profile.assert_called_with('profile_name')

        profile_parser.main(['get', '--list'])
        self.api.get_profiles.assert_called_with()

    def test_main_del_parser(self):
        profile_parser.main(['del', '--name', 'profile_name'])
        self.api.del_profile.assert_called_with('profile_name')

    @patch('iotlabcli.helpers.read_file')
    def test_main_load_parser(self, read_file_mock):
        read_file_mock.return_value = '{"profilename": "prof_name"}'
        profile_parser.main(['load', '--file', 'prof.json'])
        self.api.add_profile.assert_called_with('prof_name',
                                                {'profilename': "prof_name"})
        # invalid profile file
        self.api.add_profile.reset_mock()
        read_file_mock.return_value = '{"not_profilename_field": null}'
        self.assertRaises(SystemExit, profile_parser.main,
                          ['load', '--file', 'prof.json'])

    def test_parser_error(self):
        """ Test some parser errors directly """
        parser = profile_parser.parse_options()
        # Python3 didn't raised error without subcommand
        self.assertRaises(SystemExit, parser.parse_args, [])
