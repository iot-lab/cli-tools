# -*- coding: utf-8 -*-

""" common TestCase class  for testing commands """
from unittest import TestCase
from iotlabcli import experiment
try:
    # pylint: disable=import-error,no-name-in-module
    from mock import patch
except ImportError:  # pragma: no cover
    # pylint: disable=import-error,no-name-in-module
    from unittest.mock import patch


class CommandMock(TestCase):  # pylint: disable=too-many-public-methods
    """ Common mock needed for testing commands """
    def setUp(self):
        self.api = patch('iotlabcli.rest.Api').start().return_value
        self.api.submit_experiment.return_value = {}
        experiment.AliasNodes._alias = 0  # pylint:disable=protected-access

    def tearDown(self):
        patch.stopall()
