# -*- coding: utf-8 -*-
""" Tests for iotlabcli package """

# Python2/3 imports
# pylint: disable=import-error,no-name-in-module
# flake8: noqa
try:
    from mock import patch, mock_open
except ImportError:  # pragma: no cover
    from unittest.mock import patch, mock_open
