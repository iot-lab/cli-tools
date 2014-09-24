# -*- coding: utf-8 -*-

""" Test the iotlabcli.experiment module """

# pylint:disable=too-many-public-methods
# pylint:disable=protected-access

import os.path
import unittest
try:
    # pylint: disable=import-error,no-name-in-module
    from mock import patch, mock_open
except ImportError:  # pragma: no cover
    # pylint: disable=import-error,no-name-in-module
    from unittest.mock import patch, mock_open
import json
import iotlabcli
from iotlabcli import json_dumps
from iotlabcli import experiment
from iotlabcli.tests.my_mock import CommandMock, API_RET

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
        exp_d_2 = experiment.experiment_dict(nodes_list_2, firmware_2, 'prof2')
        exp_d_3 = experiment.experiment_dict(nodes_list_3, firmware_3, 'prof3')

        # pylint:disable=protected-access
        exp = experiment._Experiment('ExpName', 30, None)

        exp.add_experiment_dict(exp_d_2)
        exp.add_experiment_dict(exp_d_3)

        self.assertEquals(exp.type, 'physical')
        self.assertEquals(exp.nodes, ['m3-%u.grenoble.iot-lab.info' % num for
                                      num in (0, 1, 2, 3, 4, 6, 8, 9, 27)])
        self.assertIsNotNone(exp.firmwareassociations)
        self.assertIsNotNone(exp.profileassociations)
        self.assertEquals(2, len(exp.firmwareassociations))
        self.assertEquals(2, len(exp.profileassociations))


class TestExperimentSubmit(CommandMock):
    """ Test iotlabcli.experiment.submit_experiment """

    def test_experiment_submit_physical(self):
        """ Run experiment_submit physical """

        # Physical tests
        nodes_list = [experiment.experiment_dict(
            ['m3-%u.grenoble.iot-lab.info' % i for i in range(1, 6)])]
        experiment.submit_experiment(self.api, 'exp_name', 20, nodes_list,
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
            'firmwareassociations': None
        }
        self.assertEquals(expected, json.loads(call_dict['new_exp.json']))

        # Try 'print', should return exp_dict
        ret = experiment.submit_experiment(self.api, 'exp_name', 20,
                                           nodes_list, start_time=314159,
                                           print_json=True)
        self.assertEquals(ret.__dict__, expected)

    def test_experiment_submit_alias(self):
        """ Run experiment_submit alias """
        # Alias tests
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

        experiment.submit_experiment(self.api, None, 20, nodes_list)
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

    def test_exp_submit_types_detect(self):
        """ Try experiment submit types detection"""
        # Physical tests and Alias Nodes
        nodes_list = []
        nodes_list.append(experiment.experiment_dict(
            ['m3-%u.grenoble.iot-lab.info' % i for i in range(1, 6)]))
        nodes_list.append(experiment.experiment_dict(
            experiment.AliasNodes(1, 'grenoble', 'm3:at86rf231', False),
            CURRENT_DIR + '/firmware.elf', 'profile1'))

        self.assertRaises(ValueError, experiment.submit_experiment,
                          self.api, 'exp_name', 20, nodes_list)

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

        experiment.load_experiment(self.api, experiment.EXP_FILENAME,
                                   ['firmware.elf'])
        # check calls
        _calls = read_file_mock.call_args_list
        for fmw in [experiment.EXP_FILENAME, 'firmware.elf', 'firmware_2.elf']:
            for _call in _calls:
                if fmw in _call[0]:
                    break
            else:
                self.assertIn(fmw, _calls)

        self.assertRaises(
            iotlabcli.Error,
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
    """ Test iotlabcli.experiment.stop_experiment """

    def test_get_experiments_list(self):
        """ Test experiment.get_experiments_list """
        experiment.get_experiments_list(self.api, 'Running', 100, 100)
        self.api.get_experiments.assert_called_with('Running', 100, 100)

    @patch('iotlabcli.experiment._write_experiment_archive')
    def test_get_experiment(self, w_exp_archive):
        """ Test experiment.get_experiment """

        ret = experiment.get_experiment(self.api, 123)
        self.assertEquals(ret, API_RET)
        self.assertFalse(w_exp_archive.called)

        ret = experiment.get_experiment(self.api, 123, command='resources')
        self.assertEquals(ret, API_RET)
        self.assertFalse(w_exp_archive.called)

        ret = experiment.get_experiment(self.api, 123, command='data')
        self.assertEquals(ret, 'Written')
        w_exp_archive.assert_called_with(123, API_RET)


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
        dict_val = {'test': ['value', 'value2']}
        m_open = mock_open()
        with patch(open_name, m_open, create=True):
            experiment._write_experiment_archive(123, dict_val)

            file_handle = m_open.return_value
            file_handle.write.assert_called_with(json_dumps(dict_val))
