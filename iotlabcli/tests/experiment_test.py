# -*- coding: utf-8 -*-

""" Test the iotlabcli.experiment module """

import unittest
from iotlabcli import experiment


class TestExperiment(unittest.TestCase):

    def test_create_experiment(self):

        fw_dict_2 = {'name': 'firmware_2.elf', 'body': 'elf32content'}
        nodes_list_2 = ['m3-%u.grenoble.iot-lab.info' % num for num in
                        (0, 2, 4, 6, 8)]

        fw_dict_3 = {'name': 'firmware_3.elf', 'body': 'elf32content'}
        nodes_list_3 = ['m3-%u.grenoble.iot-lab.info' % num for num in
                        (1, 3, 9, 27)]
        exp_d_2 = experiment.experiment_dict(nodes_list_2, fw_dict_2, 'prof2')
        exp_d_3 = experiment.experiment_dict(nodes_list_3, fw_dict_3, 'prof3')

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
