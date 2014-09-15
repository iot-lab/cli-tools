# -*- coding: utf-8 -*-

""" Test the iotlabcli.experiment_parser module """

# pylint:disable=missing-docstring,too-many-public-methods
from mock import patch

from iotlabcli.tests.main_mock import MainMock
import iotlabcli.parser.experiment as experiment_parser
from iotlabcli import experiment


class TestMainInfoParser(MainMock):
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

    @patch('iotlabcli.experiment.Experiment')
    @patch('iotlabcli.experiment.submit_experiment')
    def test_main_submit_parser(self, submit_exp, exp_class):
        """ Run experiment_parser.main.submit """
        submit_exp.return_value = {}
        exp = exp_class.return_value

        # Physical tests
        experiment_parser.main(['submit', '--name', 'exp_name',
                                '--duration', '20', '--reservation', '314159',
                                '--list', 'grenoble,m3,1-5'])
        nodes_list = [
            experiment.experiment_dict(
                ['m3-%u.grenoble.iot-lab.info' % i for i in range(1, 6)],
                None, None)
        ]
        submit_exp.assert_called_with(self.api, exp, nodes_list, False)

        # print with simple options
        nodes = [experiment.experiment_dict(['m3-1.grenoble.iot-lab.info'])]
        experiment_parser.main(
            ['submit', '-p', '-d', '20', '-l', 'grenoble,m3,1'])
        submit_exp.assert_called_with(self.api, exp, nodes, True)

        # Alias tests
        experiment_parser.main([
            'submit', '-d', '20',
            '-l', '1,archi=m3:at86rf231+site=grenoble,firmware.elf,profile1',
            '-l', '2,archi=m3:at86rf231+site=grenoble,firmware.elf,profile1',
            '-l', '3,archi=m3:at86rf231+site=grenoble,firmware_2.elf,profile2',
        ])
        experiment.AliasNodes._alias = 0  # pylint:disable=protected-access
        nodes_list = [
            experiment.experiment_dict(
                experiment.AliasNodes(1, 'grenoble', 'm3:at86rf231', False),
                'firmware.elf', 'profile1'),
            experiment.experiment_dict(
                experiment.AliasNodes(2, 'grenoble', 'm3:at86rf231', False),
                'firmware.elf', 'profile1'),
            experiment.experiment_dict(
                experiment.AliasNodes(3, 'grenoble', 'm3:at86rf231', False),
                'firmware_2.elf', 'profile2'),
        ]

        submit_exp.assert_called_with(self.api, exp, nodes_list, False)

    def test_main_submit_parser_error(self):
        """ Run experiment_parser.main.submit with error"""
        # Physical tests
        self.assertRaises(
            SystemExit, experiment_parser.main,
            ['submit', '--duration', '20',
             '-l', 'grenoble,m3,1-5,firmware, profile,toomanyvalues'])

    @patch('iotlabcli.experiment.load_experiment')
    def test_main_load_parser(self, load_exp):
        """ Run experiment_parser.main.load """
        load_exp.return_value = {}
        experiment_parser.main(['load', '-f', '../test_exp.json',
                                '-l', '~/firmware.elf,./firmware_2.elf'])
        load_exp.assert_called_with(self.api, '../test_exp.json',
                                    ['~/firmware.elf', './firmware_2.elf'])
