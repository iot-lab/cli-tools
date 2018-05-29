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

from .c23 import patch


@pytest.mark.parametrize('entry',
                         ['auth', 'admin', 'experiment',
                          'node', 'profile', 'robot'])
def test_main_parser(entry):
    """ Experiment parser """
    with patch('iotlabcli.parser.%s.main' % entry) as entrypoint_func:
        main_parser.main([entry, '-i', '123'])
        entrypoint_func.assert_called_with(['-i', '123'])


@pytest.mark.parametrize('argv,exc', argvalues=(
    (['iotlab'], None), (['iotlab', 'help'], None),
    (['iotlab', '--help'], SystemExit),
), ids=['no subcommand', 'help subcommand', '--help argument'])
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
