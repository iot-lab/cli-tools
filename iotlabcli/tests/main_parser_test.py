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
import os
import sys

import pytest
from pytest import skip

import iotlabcli.parser.main as main_parser

from .c23 import patch, version_info


PY3 = version_info[0] == 3


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


test_tools = 'TEST_IOTLAB_TOOLS' in os.environ  # pylint: disable=invalid-name

with_tools = pytest.mark.skipif(  # pylint: disable=invalid-name
    not test_tools,
    reason="needs TEST_IOTLAB_TOOLS env. variable set to run")

without_tools = pytest.mark.skipif(  # pylint: disable=invalid-name
    test_tools,
    reason="needs TEST_IOTLAB_TOOLS env. variable not set to run")


@with_tools
def test_main_parser_aggregator():
    """ Experiment parser """
    if PY3:
        skip('aggregation-tools not py3 compatible')
    entry = 'aggregator'
    with patch('iotlabcli.parser.main.aggregator') as entrypoint_func:
        main_parser.main([entry, '-i', '123'])
        entrypoint_func.assert_called_with(['-i', '123'])


@with_tools
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


@with_tools
def test_detect_tools_installed():
    """
    tests that we detect the tools modules correctly
    only run in the tox env where the tools are installed
    """

    if not PY3:
        assert main_parser.AGGREGATION_TOOLS
    assert main_parser.OMLPLOT_TOOLS
    assert main_parser.SSH_TOOLS


@without_tools
def test_detect_tools_not_installed():
    """
    tests that we detect the non installed modules correctly
    """

    assert not main_parser.AGGREGATION_TOOLS
    assert not main_parser.OMLPLOT_TOOLS
    assert not main_parser.SSH_TOOLS
