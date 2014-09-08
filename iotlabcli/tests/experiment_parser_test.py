# -*- coding: utf-8 -*-

""" Test the iotlabcli.experiment_parser module """
import unittest
from mock import patch
from iotlabcli import experiment_parser


@patch('iotlabcli.helpers.get_current_experiment',
       (lambda x: 123 if x is None else x))
@patch('iotlabcli.helpers.get_user_credentials')
@patch('iotlabcli.rest.Api')
class TestMainInfoParser(unittest.TestCase):

    def test_main_info_parser(self, api_class, get_credentials):
        """ Run experiment_parser.main.info """
        api = api_class.return_value
        api.get_resources.return_value = {}
        api.get_resources.return_value = {}
        get_credentials.return_value = 'username', 'password'

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
