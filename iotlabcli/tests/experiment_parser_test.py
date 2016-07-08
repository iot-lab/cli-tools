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

""" Test the iotlabcli.experiment_parser module """
# pylint: disable=too-many-public-methods

import unittest

from iotlabcli.tests.my_mock import MainMock
import iotlabcli.parser.experiment as experiment_parser
from iotlabcli import experiment

from .c23 import patch


class TestMainInfoParser(MainMock):
    """Test experimen.parser."""

    def setUp(self):
        MainMock.setUp(self)
        experiment.AliasNodes._alias = 0  # pylint:disable=protected-access

    @patch('iotlabcli.experiment.info_experiment')
    def test_main_info_parser(self, info_exp):
        """ Run experiment_parser.main.info """
        info_exp.return_value = {}

        experiment_parser.main(['info', '--list'])
        info_exp.assert_called_with(self.api, False, None)
        experiment_parser.main(['info', '--list-id', '--site', 'grenoble'])
        info_exp.assert_called_with(self.api, True, 'grenoble')

    @patch('iotlabcli.experiment.stop_experiment')
    def test_main_stop_parser(self, stop_exp):
        """ Run experiment_parser.main.stop """
        stop_exp.return_value = {}
        experiment_parser.main(['stop'])
        stop_exp.assert_called_with(self.api, 123)
        experiment_parser.main(['stop', '-i', '345'])
        stop_exp.assert_called_with(self.api, 345)

    @patch('iotlabcli.experiment.get_experiments_list')
    @patch('iotlabcli.experiment.get_experiment')
    def test_main_get_parser(self, get_exp, get_exp_list):
        """ Run experiment_parser.main.get """
        get_exp.return_value = {}
        get_exp_list.return_value = {}

        get_exp.return_value = {'start_time': 1423131729}
        experiment_parser.main(['get', '--start-time'])
        get_exp.assert_called_with(self.api, 234, 'start')

        # No value is treated inside
        get_exp.return_value = {}

        experiment_parser.main(['get', '--id', '18', '--print'])
        get_exp.assert_called_with(self.api, 18, '')

        experiment_parser.main(['get', '--resources'])
        get_exp.assert_called_with(self.api, 123, 'resources')

        experiment_parser.main(['get', '--resources-id'])
        get_exp.assert_called_with(self.api, 123, 'id')

        experiment_parser.main(['get', '--exp-state'])
        get_exp.assert_called_with(self.api, 123, 'state')

        experiment_parser.main(['get', '--archive'])
        get_exp.assert_called_with(self.api, 123, 'data')

        experiment_parser.main(
            ['get', '--list', '--state=Running', '--limit=10', '--offset=50'])
        get_exp_list.assert_called_with(self.api, 'Running', 10, 50)

        experiment_parser.main(['get', '--list'])
        get_exp_list.assert_called_with(self.api, None, 0, 0)

    def test_parser_error(self):
        """ Test some parser errors directly """
        parser = experiment_parser.parse_options()
        # Python3 didn't raised error without subcommand
        self.assertRaises(SystemExit, parser.parse_args, [])

    @patch('iotlabcli.experiment.get_experiment')
    def test_experiment_get_start_time(self, get_exp):
        """ Test the get-start-time parser """
        cmd = ['-u', 'test', '-p', 'password', 'get', '--start-time']
        args = experiment_parser.parse_options().parse_args(cmd)

        get_exp.return_value = {'start_time': 1423131729}
        ret = experiment_parser.get_experiment_parser(args)
        get_exp.assert_called_with(self.api, 234, 'start')
        # don't expect anything on local time
        self.assertTrue('2015' in ret['local_date'])

        # No start_time
        get_exp.return_value = {'start_time': 0}
        ret = experiment_parser.get_experiment_parser(args)
        get_exp.assert_called_with(self.api, 234, 'start')
        self.assertEqual('Unknown', ret['local_date'])

    @patch('iotlabcli.experiment.submit_experiment')
    def test_main_submit_parser(self, submit_exp):
        """ Run experiment_parser.main.submit """
        submit_exp.return_value = {}

        # Physical tests
        experiment_parser.main(['submit', '--name', 'exp_name',
                                '--duration', '20', '--reservation', '314159',
                                '--list', 'grenoble,m3,1-5'])
        resources = [
            experiment.exp_resources(
                ['m3-%u.grenoble.iot-lab.info' % i for i in range(1, 6)],
                None, None)
        ]
        submit_exp.assert_called_with(self.api, 'exp_name', 20, resources,
                                      314159, False)

        # print with simple options
        nodes = [experiment.exp_resources(['m3-1.grenoble.iot-lab.info'])]
        experiment_parser.main(
            ['submit', '-p', '-d', '20', '-l', 'grenoble,m3,1'])
        submit_exp.assert_called_with(self.api, None, 20, nodes,
                                      None, True)

        # Alias tests
        experiment_parser.main([
            'submit', '-d', '20',
            '-l', '1,archi=m3:at86rf231+site=grenoble,firmware.elf,profile1',
            '-l', '2,archi=m3:at86rf231+site=grenoble,firmware.elf,profile1',
            '-l', '3,archi=m3:at86rf231+site=grenoble,firmware_2.elf,profile2',
        ])
        experiment.AliasNodes._alias = 0  # pylint:disable=protected-access
        resources = [
            experiment.exp_resources(
                experiment.AliasNodes(1, 'grenoble', 'm3:at86rf231', False),
                'firmware.elf', 'profile1'),
            experiment.exp_resources(
                experiment.AliasNodes(2, 'grenoble', 'm3:at86rf231', False),
                'firmware.elf', 'profile1'),
            experiment.exp_resources(
                experiment.AliasNodes(3, 'grenoble', 'm3:at86rf231', False),
                'firmware_2.elf', 'profile2'),
        ]

        submit_exp.assert_called_with(self.api, None, 20, resources,
                                      None, False)

    @patch('iotlabcli.experiment.submit_experiment')
    def test_main_submit_parser_assocs(self, submit_exp):
        """Run experiment_parser.main.submit mobility."""
        submit_exp.return_value = {}

        # Physical tests
        experiment_parser.main(
            ['submit', '--name', 'exp_name', '--duration', '20',
             '--list',
             ('grenoble,m3,1,'
              'mobility=controlled,kernel=linux,firmware=m3.elf')])

        assocs = {'mobility': 'controlled', 'kernel': 'linux'}
        resources = [
            experiment.exp_resources(['m3-1.grenoble.iot-lab.info'],
                                     'm3.elf', None, **assocs)
        ]
        submit_exp.assert_called_with(self.api, 'exp_name', 20, resources,
                                      None, False)

    def test_main_submit_parser_error(self):
        """ Run experiment_parser.main.submit with error"""
        # Physical tests
        self.assertRaises(
            SystemExit, experiment_parser.main,
            ['submit', '--duration', '20',
             '-l', 'grenoble,m3,1-5,firmware, profile,toomanyvalues'])

        # Physical tests
        self.assertRaises(
            SystemExit, experiment_parser.main,
            ['submit', '--duration', '20', '-l', 'grenoble,m3,100-1'])

    @patch('iotlabcli.experiment.wait_experiment')
    def test_main_wait_parser(self, wait_exp):
        """ Run experiment_parser.main.info """
        wait_exp.return_value = {}

        experiment_parser.main(['wait'])
        wait_exp.assert_called_with(self.api, 234, 'Running', 5, float('+inf'))
        experiment_parser.main(['wait', '--id', '42',
                                '--state', 'Launching,Running', '--step', '1',
                                '--timeout', '60'])
        wait_exp.assert_called_with(self.api, 42, 'Launching,Running', 1, 60)

    @patch('iotlabcli.experiment.load_experiment')
    def test_main_load_parser(self, load_exp):
        """ Run experiment_parser.main.load """
        load_exp.return_value = {}
        experiment_parser.main(['load', '-f', '../test_exp.json',
                                '-l', '~/firmware.elf,./firmware_2.elf'])
        load_exp.assert_called_with(self.api, '../test_exp.json',
                                    ['~/firmware.elf', './firmware_2.elf'])


# pylint:disable=protected-access
class TestAssociationParser(unittest.TestCase):
    """Test experiment submit associations."""

    def _assert_assoc(self, params, expected):
        """Check given params return expected associations."""
        ret = experiment_parser._extract_associations(params)
        self.assertEqual(ret, expected)

    def _assert_fail_assoc(self, params):
        """Check given params fails."""
        self.assertRaises(ValueError,
                          experiment_parser._extract_associations, params)

    def test_legacy_assocs(self):
        """Valid legacy mode associations."""

        # Nothing given
        self._assert_assoc([], {})
        self._assert_assoc(['', ''], {})

        # Only one
        self._assert_assoc(['tutorial_m3.elf'],
                           {'firmware': 'tutorial_m3.elf'})
        self._assert_assoc(['', 'battery'],
                           {'profile': 'battery'})
        # Firmware and profile
        self._assert_assoc(['tuto_m3.elf', 'battery'],
                           {'firmware': 'tuto_m3.elf', 'profile': 'battery'})

    def test_valid_new_assocs(self):
        """Valid new mode associations."""
        # Nothing given
        self._assert_assoc(['', '', 'firmware='], {})

        # With new value
        self._assert_assoc(['tuto_m3.elf', 'battery', 'mobility=JHall'],
                           {'firmware': 'tuto_m3.elf', 'profile': 'battery',
                            'mobility': 'JHall'})
        self._assert_assoc(['', 'battery', 'mobility=JHall'],
                           {'profile': 'battery', 'mobility': 'JHall'})
        self._assert_assoc(['', 'firmware=m3.elf'],
                           {'firmware': 'm3.elf'})

    def test_invalid_legacy_assocs(self):
        """Invalid legacy mode associations."""
        self._assert_fail_assoc(['tuto.elf', 'battery', 'extra_unknown'])

    def test_invalid_new_assocs(self):
        """Invalid new mode associations."""
        self._assert_fail_assoc(['mobility=JHall', 'm3.elf'])
        self._assert_fail_assoc(['m3.elf', 'mobility=JHall', 'batt'])
        self._assert_fail_assoc(['m3.elf', 'firmware=tuto.elf'])
        self._assert_fail_assoc(['val aue'])
