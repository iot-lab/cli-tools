# -*- coding: utf-8 -*-
""" Test the iotlabcli.helpers module """
# pylint:disable=too-many-public-methods

import unittest

from iotlabcli import Error
from iotlabcli import helpers
from iotlabcli.tests import my_mock


class TestHelpers(unittest.TestCase):
    """ Test the iotlabcli.helpers module """
    def tearDown(self):
        my_mock.api_mock_stop()

    def test_get_current_experiment(self):
        """ Test get_current_experiment """
        api = my_mock.api_mock(ret={"items": [{"id": 234}]})
        self.assertEquals(123, helpers.get_current_experiment(api, 123))
        self.assertEquals(234, helpers.get_current_experiment(api, None))

    def test_check_experiments_running(self):
        """ Test check_experiments_running """
        self.assertEquals(
            123, helpers.check_experiments_running({"items": [{"id": 123}]}))
        self.assertRaises(Error, helpers.check_experiments_running,
                          {"items": []})
        self.assertRaises(Error, helpers.check_experiments_running,
                          {"items": [{"id": 123}, {"id": 124}]})
