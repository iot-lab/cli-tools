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
import iotlabcli.parser.admin
import iotlabcli.parser.experiment
import iotlabcli.parser.node
import iotlabcli.parser.profile
import iotlabcli.parser.robot

# from aggregation-tools
try:
    from iotlabaggregator.serial import main as aggregator_serial_main
    from iotlabaggregator.sniffer import main as aggregator_sniffer_main
    AGGREGATION_TOOLS = True
except (ImportError, TypeError):
    # TypeError for aggregation-tools, not py3 compatible yet
    AGGREGATION_TOOLS = False

# from ssh-cli-tools
try:
    from iotlabsshcli.parser.open_a8_parser import main as ssh_main
    SSH_TOOLS = True
except ImportError:
    SSH_TOOLS = False

# from oml-plot-tools
try:
    from oml_plot_tools.consum import main as oml_plot_consum_main
    from oml_plot_tools.radio import main as oml_plot_radio_main
    from oml_plot_tools.traj import main as oml_plot_traj_main
    OMLPLOT_TOOLS = True
except (ImportError, SyntaxError, TypeError):
    OMLPLOT_TOOLS = False


def parse_subcommands(commands, args=None):
    """ common function to parse `iotlab` or other with subcommands """
    args = args or sys.argv[1:]

    parser = ArgumentParser()
    parser.add_argument('command', nargs='?',
                        choices=commands.keys(), default='help')
    commands['help'] = lambda args: parser.print_help()

    opts, args = parser.parse_known_args(args)

    return commands[opts.command](args)


def aggregator(args):
    """'iotlab aggregator' main function."""

    commands = {
        'sniffer': aggregator_sniffer_main,
        'serial': aggregator_serial_main
    }
    parse_subcommands(commands, args)


def oml_plot(args):
    """'iotlab oml-plot' main function."""

    commands = {
        'consum': oml_plot_consum_main,
        'radio': oml_plot_radio_main,
        'traj': oml_plot_traj_main
    }
    parse_subcommands(commands, args)


def main(args=None):
    """'iotlab' main function."""

    commands = {
        'auth': iotlabcli.parser.auth.main,
        'admin': iotlabcli.parser.admin.main,
        'experiment': iotlabcli.parser.experiment.main,
        'node': iotlabcli.parser.node.main,
        'profile': iotlabcli.parser.profile.main,
        'robot': iotlabcli.parser.robot.main,
        'help': None
    }
    if AGGREGATION_TOOLS:
        commands['aggregator'] = aggregator
    if OMLPLOT_TOOLS:
        commands['oml-plot'] = oml_plot
    if SSH_TOOLS:
        commands['ssh'] = ssh_main

    return parse_subcommands(commands, args)
