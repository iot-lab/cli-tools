# -*- coding: utf-8 -*-

""" Test the iotlabcli.experiment module """

# pylint:disable=too-many-public-methods
# pylint:disable=protected-access
# pylint >= 1.4
# pylint:disable=too-few-public-methods

import os.path
import unittest
try:
    # pylint: disable=import-error,no-name-in-module
    from mock import patch, mock_open
except ImportError:  # pragma: no cover
    # pylint: disable=import-error,no-name-in-module
    from unittest.mock import patch, mock_open
import json
from iotlabcli import experiment
from iotlabcli import rest
from iotlabcli.tests.my_mock import CommandMock, API_RET, RequestRet

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

        self.assertEquals(exp.type, 'physical')
        self.assertEquals(exp.nodes, ['m3-%u.grenoble.iot-lab.info' % num for
                                      num in (0, 1, 2, 3, 4, 6, 8, 9, 27)])
        self.assertTrue(exp.firmwareassociations is not None)
        self.assertTrue(exp.profileassociations is not None)
        self.assertEquals(2, len(exp.firmwareassociations))
        self.assertEquals(2, len(exp.profileassociations))


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
            'firmwareassociations': None
        }
        self.assertEquals(expected, json.loads(call_dict['new_exp.json']))

        # Try 'print', should return exp_dict
        ret = experiment.submit_experiment(self.api, 'exp_name', 20,
                                           resources, start_time=314159,
                                           print_json=True)
        self.assertEquals(ret.__dict__, expected)

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
            ]
        }
        self.assertEquals(expected, exp_desc)
        self.assertTrue('firmware.elf' in files_dict)

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
        self.assertEquals(_files,
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
        self.assertEquals(ret, API_RET)

        ret = experiment.get_experiment(self.api, 123, option='resources')
        self.assertEquals(ret, API_RET)


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
        self.assertEquals('Running', ret)

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
        self.assertEquals(ret, 'Written')
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
