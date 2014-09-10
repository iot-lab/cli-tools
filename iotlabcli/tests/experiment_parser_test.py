# -*- coding: utf-8 -*-

""" Test the iotlabcli.experiment_parser module """
from os import path
import unittest
import json
from mock import patch
from iotlabcli import experiment_parser
CURRENT_DIR = path.dirname(path.abspath(__file__))


@patch('iotlabcli.helpers.get_current_experiment',
       (lambda a, x: 123 if x is None else x))
@patch('iotlabcli.helpers.get_user_credentials')
@patch('iotlabcli.rest.Api')
class TestMainInfoParser(unittest.TestCase):

    def test_main_info_parser(self, api_class, get_credentials):
        """ Run experiment_parser.main.info """
        api = api_class.return_value
        get_credentials.return_value = 'username', 'password'
        api.get_resources.return_value = {}
        api.get_resources.return_value = {}

        experiment_parser.main(['info', '--list'])
        api.get_resources.assert_called_with(False, None)
        api.reset_mock()

        experiment_parser.main(['info', '--list-id', '--site', 'grenoble'])
        api.get_resources.assert_called_with(True, 'grenoble')

    def test_main_stop_parser(self, api_class, get_credentials):
        """ Run experiment_parser.main.stop """
        api = api_class.return_value
        api.stop_experiment.return_value = {}
        get_credentials.return_value = 'username', 'password'

        experiment_parser.main(['stop'])
        api.stop_experiment.assert_called_with(123)
        api.reset_mock()

        experiment_parser.main(['stop', '-i', '345'])
        api.stop_experiment.assert_called_with(345)

    def test_main_get_parser(self, api_class, get_credentials):
        """ Run experiment_parser.main.get """
        api = api_class.return_value

        get_credentials.return_value = 'username', 'password'

        api.get_experiment_info.return_value = {}
        api.get_experiments.return_value = {}

        api.reset_mock()
        experiment_parser.main(['get', '--id', '18', '--print'])
        api.get_experiment_info.assert_called_with(18, '')

        api.reset_mock()
        experiment_parser.main(['get', '--resources'])
        api.get_experiment_info.assert_called_with(123, 'resources')

        api.reset_mock()
        experiment_parser.main(['get', '--resources-id'])
        api.get_experiment_info.assert_called_with(123, 'id')

        api.reset_mock()
        experiment_parser.main(['get', '--exp-state'])
        api.get_experiment_info.assert_called_with(123, 'state')

        with patch('iotlabcli.helpers.write_experiment_archive') as w_mock:
            api.reset_mock()
            experiment_parser.main(['get', '--archive'])
            api.get_experiment_info.assert_called_with(123, 'data')
            self.assertTrue(w_mock.called)

        api.reset_mock()
        experiment_parser.main(['get', '--list', '--state=Running',
                                '--limit=10', '--offset=50'])
        api.get_experiments.assert_called_with('Running', 10, 50)

        api.reset_mock()
        experiment_parser.main(['get', '--list'])
        api.get_experiments.assert_called_with(
            'Terminated,Waiting,Launching,Finishing,Running,Error', 0, 0)

    @patch('iotlabcli.parser_common.Singleton')
    def test_main_submit_parser(self, plat_class, api_class, get_credentials):
        """ Run experiment_parser.main.submit """
        plat_class.return_value.sites.return_value = ['grenoble', 'strasbourg']
        api = api_class.return_value
        api.submit_experiment.return_value = {}
        get_credentials.return_value = 'username', 'password'

        # Physical tests
        api.reset_mock()
        experiment_parser.main(['submit', '--name', 'exp_name',
                                '--duration', '20', '--reservation', '314159',
                                '--list', 'grenoble,m3,1-5'])
        call_dict = api.submit_experiment.call_args[0][0]
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

        # Alias tests
        api.reset_mock()
        experiment_parser.main([
            'submit', '-d', '20', '-l',
            '1,archi=m3:at86rf231+site=grenoble,%s/firmware.elf,profile1' %
            CURRENT_DIR, '-l',
            '1,archi=m3:at86rf231+site=grenoble,%s/firmware.elf,profile1' %
            CURRENT_DIR, '-l',
            '1,archi=m3:at86rf231+site=grenoble,%s/firmware_2.elf,profile2' %
            CURRENT_DIR,
        ])

        files_dict = api.submit_experiment.call_args[0][0]
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
                {"alias": '2', "nbnodes": 1, "properties": {
                    "archi": "m3:at86rf231", "site": "grenoble",
                    "mobile": False
                }},
                {"alias": '3', "nbnodes": 1, "properties": {
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

        # print with simple options
        api.reset_mock()
        experiment_parser.main(['submit', '-p', '-d', '20',
                                '-l', '9,archi=m3:at86rf231+site=grenoble'])
        self.assertFalse(api.submit_experiment.called)
