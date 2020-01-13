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

"""Main parser."""

import sys
from argparse import ArgumentParser

import iotlabcli.parser.auth
import iotlabcli.parser.experiment
import iotlabcli.parser.node
import iotlabcli.parser.profile
import iotlabcli.parser.robot
import iotlabcli.parser.status

# from aggregation-tools
try:
    import iotlabaggregator.serial
    import iotlabaggregator.sniffer
except (ImportError, TypeError):
    # TypeError for aggregation-tools, not py3 compatible yet
    iotlabaggregator = None  # pylint:disable=invalid-name

# from ssh-cli-tools
try:
    import iotlabsshcli.parser.open_a8_parser
except ImportError:
    iotlabsshcli = None  # pylint:disable=invalid-name

# from oml-plot-tools
try:
    import oml_plot_tools
    import oml_plot_tools.consum
    import oml_plot_tools.radio
    import oml_plot_tools.traj
except (ImportError, SyntaxError, TypeError):
    oml_plot_tools = None  # pylint:disable=invalid-name


def parse_subcommands(commands, args):
    """ common function to parse `iotlab` or other with subcommands """

    parser = ArgumentParser()
    commands['help'] = lambda args: parser.print_help()
    parser.add_argument('command', nargs='?',
                        choices=commands.keys(), default='help')

    opts, _ = parser.parse_known_args(args[:1])

    sys.argv[0] = 'iotlab %s' % opts.command
    return commands[opts.command](args[1:])


def oml_plot(args):
    """'iotlab oml-plot' main function."""

    commands = {
        'consum': oml_plot_tools.consum.main,
        'radio': oml_plot_tools.radio.main,
        'traj': oml_plot_tools.traj.main
    }
    parse_subcommands(commands, args)


def main(args=None):
    """'iotlab' main function."""
    args = args or sys.argv[1:]

    commands = {
        'auth': iotlabcli.parser.auth.main,
        'experiment': iotlabcli.parser.experiment.main,
        'node': iotlabcli.parser.node.main,
        'profile': iotlabcli.parser.profile.main,
        'robot': iotlabcli.parser.robot.main,
        'status': iotlabcli.parser.status.main
    }
    if iotlabaggregator:
        commands['serial'] = iotlabaggregator.serial.main
        commands['sniffer'] = iotlabaggregator.sniffer.main
    if oml_plot_tools:
        commands['plot'] = oml_plot
    if iotlabsshcli:
        commands['ssh'] = iotlabsshcli.parser.open_a8_parser.main

    return parse_subcommands(commands, args)
