# -*- coding: utf-8 -*-

""" Test the iotlabcli.experiment_parser module """
import unittest
import mock
from iotlabcli import experiment_parser


@mock.patch('iotlabcli.helpers.get_user_credentials')
@mock.patch('iotlabcli.rest.Api')
class TestMainInfoParser(unittest.TestCase):

    def test_main_info_parser(self, api_class, get_credentials):
        """ Run experiment_parser.main.info """
        api = api_class.return_value
        api.get_resources.return_value = {}
        api.get_resources_id.return_value = {}
        get_credentials.return_value = 'username', 'password'

        experiment_parser.main(['info', '--list'])
        api.get_resources.assert_called_with(None)
        self.assertFalse(api.get_resources_id.called)
        api.reset_mock()

        experiment_parser.main(['info', '--list-id', '--site', 'grenoble'])
        self.assertFalse(api.get_resources.called)
        api.get_resources_id.assert_called_with('grenoble')

    def test_main_stop_parser(self, api_class, get_credentials):
        """ Run experiment_parser.main.stop """
        api = api_class.return_value
        api.stop_experiment.return_value = {}
        get_credentials.return_value = 'username', 'password'
        api.get_current_experiment.side_effect = (
            lambda x: 123 if x is None else x)

        experiment_parser.main(['stop'])
        api.stop_experiment.assert_called_with(123)
        api.reset_mock()

        experiment_parser.main(['stop', '-i', '345'])
        api.stop_experiment.assert_called_with(345)
