# -*- coding: utf-8 -*-

# This file is a part of IoT-LAB cli-tools
# Copyright (C) 2015 INRIA (Contact: admin@iot-lab.info)
# Contributor(s) : see AUTHORS file
#
# This software is governed by the CeCILL license under French law
# and abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# http://www.cecill.info.
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

""" Test the iotlabcli.experiment_parser module """
import argparse
import sys

import pytest
from mock import Mock, mock

import iotlabcli.parser.main as main_parser

from .c23 import patch
try:
    from importlib import reload
except ImportError:
    pass


@pytest.mark.parametrize('entry',
                         ['auth', 'admin', 'experiment',
                          'node', 'profile', 'robot'])
def test_main_parser(entry):
    """ Experiment parser """
    with patch('iotlabcli.parser.%s.main' % entry) as entrypoint_func:
        main_parser.main([entry, '-i', '123'])
        entrypoint_func.assert_called_with(['-i', '123'])


@pytest.mark.parametrize('argv,exc',
                         argvalues=((['iotlab'], None),
                                    (['iotlab', 'help'], None),
                                    (['iotlab', '--help'], SystemExit),),
                         ids=['no subcommand',
                              'help subcommand',
                              '--help argument'])
def test_help(argv, exc):
    """Tests that the help entrypoints print the help."""
    with patch.object(argparse.ArgumentParser, 'print_help') \
            as argparser_print_help, \
            patch.object(sys, 'argv', argv):
        if exc:
            with pytest.raises(exc):
                main_parser.main()
        else:
            main_parser.main()
        argparser_print_help.assert_called()


def test_main_parser_aggregator():
    """ Experiment parser """
    entry = 'aggregator'
    with patch('iotlabcli.parser.main.aggregator') as entrypoint_func, \
            patch('iotlabcli.parser.main.AGGREGATION_TOOLS', True):
        main_parser.main([entry, '-i', '123'])
        entrypoint_func.assert_called_with(['-i', '123'])


def test_main_parser_no_aggregator():
    """ Experiment parser """
    with patch('iotlabcli.parser.main.AGGREGATION_TOOLS', False):
        pytest.raises(SystemExit,
                      lambda: main_parser.main(['aggregator']))


def test_main_parser_oml_plot():
    """ Experiment parser """
    entry = 'oml-plot'
    with patch('iotlabcli.parser.main.oml_plot') as entrypoint_func, \
            patch('iotlabcli.parser.main.OMLPLOT_TOOLS', True):
        main_parser.main([entry, '-i', '123'])
        entrypoint_func.assert_called_with(['-i', '123'])


def test_main_parser_no_oml_plot():
    """ Experiment parser """
    with patch('iotlabcli.parser.main.OMLPLOT_TOOLS', False):
        pytest.raises(SystemExit,
                      lambda: main_parser.main(['oml-plot']))


def get_mock_import(func):
    """factory for mock_import functions"""
    original_import = __import__

    def mock_import(name, *args, **kwargs):
        """if package matches, then call the function"""
        for package in ('iotlabsshcli', 'iotlabaggregator', 'oml_plot_tools'):
            if package in name:
                return func()

        return original_import(name, *args, **kwargs)

    return mock_import


ENTRIES = [['ssh'], ['aggregator', 'serial'], ['aggregator', 'sniffer'],
           ['oml-plot', 'consum'], ['oml-plot', 'traj'], ['oml-plot', 'radio']]

BUILTIN_IMPORT = '%s.__import__' % mock.builtin


@pytest.mark.parametrize('entry', ENTRIES, ids=' '.join)
@patch('iotlabcli.parser.main.AGGREGATION_TOOLS', True)
@patch('iotlabcli.parser.main.OMLPLOT_TOOLS', True)
@patch('iotlabcli.parser.main.SSH_TOOLS', True)
def test_main_parser_mocked_import(entry):
    """ Experiment parser """
    module_mock = Mock()

    with patch(BUILTIN_IMPORT, get_mock_import(lambda: module_mock)):
        reload(main_parser)
        main_parser.main(entry + ['-i', '123'])
        module_mock.main.assert_called_with(['-i', '123'])


def test_main_parser_no_ssh():
    """ Experiment parser """
    with patch('iotlabcli.parser.main.SSH_TOOLS', False):
        pytest.raises(SystemExit,
                      lambda: main_parser.main(['ssh']))


def test_mock_import():
    """ whether we detect the installed modules correctly """
    with patch(BUILTIN_IMPORT, get_mock_import(Mock)):
        reload(main_parser)
        assert main_parser.AGGREGATION_TOOLS
        assert main_parser.OMLPLOT_TOOLS
        assert main_parser.SSH_TOOLS


def test_mock_import_not_installed():
    """ whether we detect the non installed modules correctly """

    def raising_import_error():
        """raises ImportError"""
        raise ImportError

    with patch(BUILTIN_IMPORT, get_mock_import(raising_import_error)):
        reload(main_parser)
        assert not main_parser.AGGREGATION_TOOLS
        assert not main_parser.OMLPLOT_TOOLS
        assert not main_parser.SSH_TOOLS
