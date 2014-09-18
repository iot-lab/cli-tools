# -*- coding: utf-8 -*-

""" Test the iotlabcli.experiment module """

# pylint:disable=too-many-public-methods

import os.path
import unittest
try:
    # pylint: disable=import-error,no-name-in-module
    from mock import patch
except ImportError:  # pragma: no cover
    # pylint: disable=import-error,no-name-in-module
    from unittest.mock import patch
import json
from iotlabcli import experiment
from iotlabcli.tests import command_mock

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class TestExperiment(unittest.TestCase):
    """ Test ioclabcli.experiment module """

    def test_create_experiment(self):
        """ Try creating an 'Experiment' object """

        firmware_2 = 'firmware_2.elf'
        nodes_list_2 = ['m3-%u.grenoble.iot-lab.info' % num for num in
                        (0, 2, 4, 6, 8)]

        firmware_3 = 'firmware_3.elf'
        nodes_list_3 = ['m3-%u.grenoble.iot-lab.info' % num for num in
                        (1, 3, 9, 27)]
        exp_d_2 = experiment.experiment_dict(nodes_list_2, firmware_2, 'prof2')
        exp_d_3 = experiment.experiment_dict(nodes_list_3, firmware_3, 'prof3')

        exp = experiment.Experiment('ExpName', 30, None)

        exp.add_experiment_dict(exp_d_2)
        exp.add_experiment_dict(exp_d_3)

        self.assertEquals(exp.type, 'physical')
        self.assertEquals(exp.nodes, ['m3-%u.grenoble.iot-lab.info' % num for
                                      num in (0, 1, 2, 3, 4, 6, 8, 9, 27)])
        self.assertIsNotNone(exp.firmwareassociations)
        self.assertIsNotNone(exp.profileassociations)
        self.assertEquals(2, len(exp.firmwareassociations))
        self.assertEquals(2, len(exp.profileassociations))


class TestExperimentSubmit(command_mock.CommandMock):
    """ Test ioclabcli.experiment.submit_experiment """

    def test_experiment_submit_physical(self):
        """ Run experiment_submit physical """

        # Physical tests
        nodes_list = [experiment.experiment_dict(
            ['m3-%u.grenoble.iot-lab.info' % i for i in range(1, 6)])]
        exp = experiment.Experiment('exp_name', 20, 314159)
        experiment.submit_experiment(self.api, exp, nodes_list)

        call_dict = self.api.submit_experiment.call_args[0][0]
        expected = {
            'name': 'exp_name',
            'duration': 20,
            'type': 'physical',
            'nodes': [
                'm3-%u.grenoble.iot-lab.info' % num for num in range(1, 6)
            ],
            'reservation': 314159,
            'profileassociations': None,
            'firmwareassociations': None
        }
        self.assertEquals(expected, json.loads(call_dict['new_exp.json']))
        return 0

    def test_experiment_submit_alias(self):
        """ Run experiment_submit alias """
        # Alias tests
        exp = experiment.Experiment(None, 20)
        nodes_list = [
            experiment.experiment_dict(
                experiment.AliasNodes(1, 'grenoble', 'm3:at86rf231', False),
                CURRENT_DIR + '/firmware.elf', 'profile1'),
            experiment.experiment_dict(
                experiment.AliasNodes(2, 'grenoble', 'm3:at86rf231', False),
                CURRENT_DIR + '/firmware.elf', 'profile1'),
            experiment.experiment_dict(
                experiment.AliasNodes(4, 'grenoble', 'm3:at86rf231', False),
                CURRENT_DIR + '/firmware_2.elf', 'profile2'),
        ]

        experiment.submit_experiment(self.api, exp, nodes_list, False)
        files_dict = self.api.submit_experiment.call_args[0][0]
        exp_desc = json.loads(files_dict['new_exp.json'])
        expected = {
            'name': None,
            'duration': 20,
            'type': 'alias',
            'nodes': [
                {"alias": '1', "nbnodes": 1, "properties": {
                    "archi": "m3:at86rf231", "site": "grenoble",
                    "mobile": False
                }},
                {"alias": '2', "nbnodes": 2, "properties": {
                    "archi": "m3:at86rf231", "site": "grenoble",
                    "mobile": False
                }},
                {"alias": '3', "nbnodes": 4, "properties": {
                    "archi": "m3:at86rf231", "site": "grenoble",
                    "mobile": False
                }},
            ],
            'reservation': None,
            'profileassociations': [
                {'profilename': 'profile1', 'nodes': ['1', '2']},
                {'profilename': 'profile2', 'nodes': ['3']},
            ],
            'firmwareassociations': [
                {'firmwarename': 'firmware.elf', 'nodes': ['1', '2']},
                {'firmwarename': 'firmware_2.elf', 'nodes': ['3']}
            ]
        }
        self.assertEquals(expected, exp_desc)
        self.assertIn('firmware.elf', files_dict)


class TestExperimentStop(command_mock.CommandMock):
    """ Test ioclabcli.experiment.stop_experiment """

    def test_experiment_stop(self):
        """ Test running stop experiment """
        self.api.stop_experiment.return_value = {}

        experiment.stop_experiment(self.api, 123)
        self.api.stop_experiment.assert_called_with(123)


class TestExperimentGet(command_mock.CommandMock):
    """ Test ioclabcli.experiment.stop_experiment """

    @patch('iotlabcli.helpers.check_experiment_state')
    def test_get_experiments_list(self, c_exp_state):
        """ Test experiment.get_experiments_list """
        self.api.get_experiments.return_value = {}
        c_exp_state.side_effect = (lambda x: x)

        experiment.get_experiments_list(self.api, 'Running', 100, 100)
        self.api.get_experiments.assert_called_with('Running', 100, 100)

    @patch('iotlabcli.helpers.write_experiment_archive')
    def test_get_experiment(self, w_exp_archive):
        """ Test experiment.get_experiment """

        ret_val = {"ret": 0}
        self.api.get_experiment_info.return_value = ret_val

        ret = experiment.get_experiment(self.api, 123, command='resources')
        self.assertEquals(ret, ret_val)
        self.assertFalse(w_exp_archive.called)

        ret = experiment.get_experiment(self.api, 123, command='data')
        self.assertEquals(ret, 'Written')
        w_exp_archive.assert_called_with(123, ret_val)


class TestExperimentInfo(command_mock.CommandMock):
    """ Test ioclabcli.experiment.info_experiment """

    def test_info_experiment(self):
        """ Test experiment.get_resources """
        self.api.get_resources.return_value = {}

        experiment.info_experiment(self.api)
        self.api.get_resources.assert_called_with(False, None)

        experiment.info_experiment(self.api, list_id=True, site='grenoble')
        self.api.get_resources.assert_called_with(True, 'grenoble')
