# -*- coding: utf-8 -*-

""" Test the iotlabcli.parser.common module """
# pylint: disable=missing-docstring,too-many-public-methods

import unittest
try:
    # pylint: disable=import-error,no-name-in-module
    from mock import patch
except ImportError:  # pragma: no cover
    # pylint: disable=import-error,no-name-in-module
    from unittest.mock import patch
from iotlabcli.parser import common


class TestSitesList(unittest.TestCase):

    @patch('iotlabcli.rest.Api.get_sites')
    def test_sites_list(self, get_sites):
        get_sites.return_value = {
            "items": [{'site': 'grenoble'}, {'site': 'strasbourg'}]
        }

        self.assertEquals(['grenoble', 'strasbourg'], common.sites_list())
