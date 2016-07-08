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

""" Test the iotlabcli.experiment module """

# pylint:disable=too-many-public-methods
# pylint:disable=protected-access
# pylint >= 1.4
# pylint:disable=too-few-public-methods
# Pylint Mock issues
# pylint: disable=no-member

import os.path
import json
import unittest

from iotlabcli import experiment
from iotlabcli import rest
from iotlabcli.tests.my_mock import CommandMock, API_RET, RequestRet

from .c23 import patch, mock_open

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class TestExperiment(unittest.TestCase):
    """ Test iotlabcli.experiment module """

    def test_create_experiment(self):
        """ Try creating an 'Experiment' object """

        firmware_2 = 'firmware_2.elf'
        nodes_list_2 = ['m3-%u.grenoble.iot-lab.info' % num for num in
                        (0, 2, 4, 6, 8)]

        firmware_3 = 'firmware_3.elf'
        nodes_list_3 = ['m3-%u.grenoble.iot-lab.info' % num for num in
                        (1, 3, 9, 27)]
        exp_d_2 = experiment.exp_resources(nodes_list_2, firmware_2, 'prof2')
        exp_d_3 = experiment.exp_resources(nodes_list_3, firmware_3, 'prof3')

        # pylint:disable=protected-access
        exp = experiment._Experiment('ExpName', 30, None)

        exp.add_exp_resources(exp_d_2)
        exp.add_exp_resources(exp_d_3)

        self.assertEqual(exp.type, 'physical')
        self.assertEqual(exp.nodes, ['m3-%u.grenoble.iot-lab.info' % num for
                                     num in (0, 1, 2, 3, 4, 6, 8, 9, 27)])
        self.assertTrue(exp.firmwareassociations is not None)
        self.assertTrue(exp.profileassociations is not None)
        self.assertEqual(2, len(exp.firmwareassociations))
        self.assertEqual(2, len(exp.profileassociations))


class TestExperimentSubmit(CommandMock):
    """ Test iotlabcli.experiment.submit_experiment """

    def test_experiment_submit_physical(self):
        """ Run experiment_submit physical """

        # Physical tests
        resources = [experiment.exp_resources(
            ['m3-%u.grenoble.iot-lab.info' % i for i in range(1, 6)])]
        experiment.submit_experiment(self.api, 'exp_name', 20, resources,
                                     start_time=314159)

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
            'firmwareassociations': None,
            'associations': None
        }
        self.assertEqual(expected, json.loads(call_dict['new_exp.json']))

        # Try 'print', should return exp_dict
        ret = experiment.submit_experiment(self.api, 'exp_name', 20,
                                           resources, start_time=314159,
                                           print_json=True)
        self.assertEqual(ret.__dict__, expected)

    def test_experiment_submit_alias(self):
        """ Run experiment_submit alias """
        # Alias tests
        resources = [
            experiment.exp_resources(
                experiment.AliasNodes(1, 'grenoble', 'm3:at86rf231', False),
                CURRENT_DIR + '/firmware.elf', 'profile1'),
            experiment.exp_resources(
                experiment.AliasNodes(2, 'grenoble', 'm3:at86rf231', False),
                CURRENT_DIR + '/firmware.elf', 'profile1'),
            experiment.exp_resources(
                experiment.AliasNodes(4, 'grenoble', 'm3:at86rf231', False),
                CURRENT_DIR + '/firmware_2.elf', 'profile2'),
        ]

        experiment.submit_experiment(self.api, None, 20, resources)
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
            ],
            'associations': None
        }
        self.assertEqual(expected, exp_desc)
        self.assertTrue('firmware.elf' in files_dict)

    def test_exp_alias_new_types(self):
        """Test submiting alias experiments with 'new' nodes types."""
        resources = [
            experiment.exp_resources(
                experiment.AliasNodes(1, 'berlin', 'des:wifi-cc1100')),
            experiment.exp_resources(
                experiment.AliasNodes(1, 'grenoble', 'custom:leonardo:')),
        ]
        experiment.submit_experiment(self.api, None, 20, resources)
        self.assertEqual(1, self.api.submit_experiment.call_count)

    def test_exp_physical_new_types(self):
        """Test submiting physical experiments with 'new' nodes types."""
        resources = [
            experiment.exp_resources(['custom-1.grenoble.iot-lab.info']),
            experiment.exp_resources(['berlin-1.berlin.iot-lab.info']),
        ]
        experiment.submit_experiment(self.api, None, 20, resources)
        self.assertEqual(1, self.api.submit_experiment.call_count)

    def test_exp_submit_associations(self):
        """Test experiment submission with associations."""
        nodes = ['m3-1.grenoble.iot-lab.info']
        assocs = {'mobility': 'controlled', 'kernel': 'linux'}
        resources = [
            experiment.exp_resources(nodes, CURRENT_DIR + '/firmware.elf',
                                     None, **assocs),
        ]

        experiment.submit_experiment(self.api, None, 20, resources)
        call_dict = self.api.submit_experiment.call_args[0][0]
        expected = {
            'name': None,
            'duration': 20,
            'type': 'physical',
            'nodes': nodes,
            'reservation': None,
            'profileassociations': None,
            'firmwareassociations': [
                {'firmwarename': 'firmware.elf', 'nodes': nodes}],
            'associations': {
                'mobility': [
                    {'mobilityname': 'controlled', 'nodes': nodes}],
                'kernel': [
                    {'kernelname': 'linux', 'nodes': nodes}],
            }
        }
        self.assertEqual(expected, json.loads(call_dict['new_exp.json']))

    def test_exp_submit_types_detect(self):
        """ Try experiment submit types detection"""
        # Physical tests and Alias Nodes
        resources = []
        resources.append(experiment.exp_resources(
            ['m3-%u.grenoble.iot-lab.info' % i for i in range(1, 6)]))
        resources.append(experiment.exp_resources(
            experiment.AliasNodes(1, 'grenoble', 'm3:at86rf231', False),
            CURRENT_DIR + '/firmware.elf', 'profile1'))

        self.assertRaises(ValueError, experiment.submit_experiment,
                          self.api, 'exp_name', 20, resources)

    def test_exp_submit_multiple_nodes(self):
        """ Experiment submit with nodes specified multiple times """

        nodes = ['m3-1.grenoble.iot-lab.info']

        resources = []
        resources.append(experiment.exp_resources(nodes))
        resources.append(experiment.exp_resources(nodes))
        self.assertRaises(ValueError, experiment.submit_experiment,
                          self.api, 'exp_name', 20, resources)

    @patch('iotlabcli.helpers.read_file')
    def test_experiment_load(self, read_file_mock):
        """ Try experiment_load """
        node_fmt = 'm3-%u.grenoble.iot-lab.info'
        expected = {
            "name": None,
            "duration": 20,
            "nodes": [node_fmt % num for num in range(1, 6)],
            "firmwareassociations": [
                {
                    "firmwarename": "firmware.elf",
                    "nodes": [node_fmt % num for num in range(1, 3)],
                },
                {
                    "firmwarename": "firmware_2.elf",
                    "nodes": [node_fmt % num for num in range(3, 5)],
                }
            ],
            "type": "physical",
            "profileassociations": None,
            "reservation": None,
        }

        def read_file(file_path, _=''):
            """ read_file mock """
            if file_path == experiment.EXP_FILENAME:
                return json.dumps(expected)
            else:
                return "elf32arm"
        read_file_mock.side_effect = read_file

        experiment.load_experiment(
            self.api, experiment.EXP_FILENAME, ['firmware.elf'])

        # read_file_calls
        _files = set([_call[0][0] for _call in read_file_mock.call_args_list])
        self.assertEqual(_files,
                         set((experiment.EXP_FILENAME,
                              'firmware.elf', 'firmware_2.elf')))

        self.assertRaises(
            ValueError,
            experiment.load_experiment,
            self.api, experiment.EXP_FILENAME,
            ['firmware.elf', 'firmware_2.elf', 'firmware_3.elf'])


class TestExperimentStop(CommandMock):
    """ Test iotlabcli.experiment.stop_experiment """

    def test_experiment_stop(self):
        """ Test running stop experiment """
        experiment.stop_experiment(self.api, 123)
        self.api.stop_experiment.assert_called_with(123)


class TestExperimentGet(CommandMock):
    """ Test iotlabcli.experiment.get_experiment """

    def test_get_experiments_list(self):
        """ Test experiment.get_experiments_list """
        experiment.get_experiments_list(self.api, 'Running', 100, 100)
        self.api.get_experiments.assert_called_with('Running', 100, 100)

    def test_get_experiment(self):
        """ Test experiment.get_experiment """

        ret = experiment.get_experiment(self.api, 123)
        self.assertEqual(ret, API_RET)

        ret = experiment.get_experiment(self.api, 123, option='resources')
        self.assertEqual(ret, API_RET)


@patch('iotlabcli.experiment.get_experiment')
class TestExperimentWait(CommandMock):
    """ Test iotlabcli.experiment.wait_experiment """
    wait_ret = []

    def _get_exp(self, *args, **kwargs):  # pylint: disable=unused-argument
        """ Get experiment state
        Return values from config list, or 'waiting' """
        try:
            state = self.wait_ret.pop(0)
        except IndexError:
            state = 'Waiting'
        return {'state': state}

    def test_wait_experiment(self, get_exp):
        """ Test the wait_experiment function """
        self.wait_ret = ['Waiting', 'Waiting', 'toLaunch', 'Launching',
                         'Running']
        get_exp.side_effect = self._get_exp

        # simple
        ret = experiment.wait_experiment(self.api, 123, step=0)
        self.assertEqual('Running', ret)

        # Error before Running
        self.wait_ret = ['Waiting', 'toLaunch', 'Launching', 'Error']
        self.assertRaises(RuntimeError, experiment.wait_experiment,
                          self.api, 123, step=0)

        # Timeout
        self.wait_ret = []
        self.assertRaises(RuntimeError, experiment.wait_experiment,
                          self.api, 123, step=0.1, timeout=0.5)


class TestExperimentGetWriteExpArchive(unittest.TestCase):
    """ Test iotlabcli.experiment.get archive """

    @patch('iotlabcli.experiment._write_experiment_archive')
    def test_get_experiment(self, w_exp_archive):
        """ Test experiment.get_experiment """
        arch_content = '\x42\x69'

        ret_val = RequestRet(content=arch_content, status_code=200)
        patch('requests.request', return_value=ret_val).start()
        api = rest.Api('user', 'password')

        ret = experiment.get_experiment(api, 123, option='data')
        self.assertEqual(ret, 'Written')
        # encode, not real but easier for tests
        w_exp_archive.assert_called_with(123, arch_content.encode('utf-8'))


class TestExperimentInfo(CommandMock):
    """ Test iotlabcli.experiment.info_experiment """

    def test_info_experiment(self):
        """ Test experiment.get_resources """
        experiment.info_experiment(self.api)
        self.api.get_resources.assert_called_with(False, None)

        experiment.info_experiment(self.api, list_id=True, site='grenoble')
        self.api.get_resources.assert_called_with(True, 'grenoble')


class TestWriteExperimentArchive(unittest.TestCase):
    """ Test iotlabcli.experiment._write_experiment_archive """
    @staticmethod
    def test_write_experiment_archive():
        """ Test experiment._write_experiment_archive """
        open_name = 'iotlabcli.experiment.open'
        exp_data = 'binary_content'
        m_open = mock_open()
        with patch(open_name, m_open, create=True):
            experiment._write_experiment_archive(123, exp_data)

            file_handle = m_open.return_value
            file_handle.write.assert_called_with(exp_data)
