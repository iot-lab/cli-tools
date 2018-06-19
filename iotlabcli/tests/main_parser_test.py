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

import iotlabcli.parser.main as main_parser

from .c23 import patch, version_info


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


try:
    import iotlabsshcli
except ImportError:
    iotlabsshcli = None


try:
    import iotlabaggregator
    if version_info[0] != 2:
        # pylint: disable=invalid-name
        iotlabaggregator = None  # noqa
except (ImportError, TypeError):
    iotlabaggregator = None

try:
    import oml_plot_tools
    if version_info[0] != 2:
        # pylint: disable=invalid-name
        oml_plot_tools = None  # noqa
except ImportError:
    oml_plot_tools = None


def with_ssh_tools(function):
    """decorator, skip test if iotlabsshcli is not installed"""
    return pytest.mark.skipif(
        iotlabsshcli is None,
        reason="iotlabsshcli is required")(function)


def with_aggregator_tools(function):
    """decorator, skip test if iotlabaggregator is not installed"""
    return pytest.mark.skipif(
        iotlabaggregator is None,
        reason="iotlabaggregator is required")(function)


def with_oml_plot_tools(function):
    """decorator, skip test if oml_plot_tools not installed"""
    return pytest.mark.skipif(
        oml_plot_tools is None,
        reason="oml_plot_tools is required")(function)


def without_tools(function):
    """decorator, skip test if any tool is installed"""
    return pytest.mark.skipif(
        oml_plot_tools is not None or
        iotlabaggregator is not None or
        iotlabsshcli is not None,
        reason="No tools should be installed")(function)


@with_aggregator_tools
def test_main_parser_aggregator():
    """ Experiment parser """
    entry = 'aggregator'
    with patch('iotlabcli.parser.main.aggregator') as entrypoint_func:
        main_parser.main([entry, '-i', '123'])
        entrypoint_func.assert_called_with(['-i', '123'])


@with_oml_plot_tools
def test_main_parser_oml_plot():
    """ Experiment parser """
    entry = 'oml-plot'
    with patch('iotlabcli.parser.main.oml_plot') as entrypoint_func:
        main_parser.main([entry, '-i', '123'])
        entrypoint_func.assert_called_with(['-i', '123'])


@without_tools
def test_main_parser_no_tools():
    """tools subcommands returning"""
    pytest.raises(SystemExit,
                  lambda: main_parser.main(['ssh']))
    pytest.raises(SystemExit,
                  lambda: main_parser.main(['aggregator']))
    pytest.raises(SystemExit,
                  lambda: main_parser.main(['oml-plot']))


@with_aggregator_tools
def test_aggregator_tools_detect():
    """
    tests that we detect the aggregator-tools correctly
    """
    assert main_parser.AGGREGATION_TOOLS


@with_oml_plot_tools
def test_oml_plot_tools_detect():
    """
    tests that we detect the oml-plot-tools correctly
    """
    assert main_parser.OMLPLOT_TOOLS


@with_ssh_tools
def test_ssh_tools_detect():
    """
    tests that we detect the ssh-cli-tools correctly
    """
    assert main_parser.SSH_TOOLS


@without_tools
def test_detect_tools_not_installed():
    """
    tests that we detect the non installed modules correctly
    """

    assert not main_parser.AGGREGATION_TOOLS
    assert not main_parser.OMLPLOT_TOOLS
    assert not main_parser.SSH_TOOLS
