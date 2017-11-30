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

"""Admin parser."""

import sys
from argparse import ArgumentParser

from iotlabcli.parser import common
from iotlabcli.parser import experiment
from iotlabcli import admin


def parse_options():
    """ Handle experiment-cli command-line options with argparse """
    parent_parser = common.base_parser()

    # We create top level parser
    parser = ArgumentParser(parents=[parent_parser])
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True  # not required by default in Python3

    # ####### WAIT PARSER ###############
    wait_parser = experiment.parser_add_wait_subparser(subparsers,
                                                       expid_required=True)
    wait_parser.add_argument('--exp-user', required=True)

    return parser


def wait_experiment_parser(opts):
    """ Parse namespace 'opts' object and execute requested 'wait' command """

    sys.stderr.write(
        "Waiting that experiment {}/{} gets in state {}\n".format(
            opts.experiment_id, opts.exp_user, opts.state))

    return admin.wait_user_experiment(opts.experiment_id, opts.exp_user,
                                      opts.state, opts.step, opts.timeout)


def admin_parse_and_run(opts):
    """ Parse namespace 'opts' object and execute requested command
    Return result object
    """
    command = {
        'wait': wait_experiment_parser,
    }[opts.command]

    # Disable similar lines in 2 files
    return command(opts)


def main(args=None):
    """'admin-cli' main function."""
    args = args or sys.argv[1:]
    parser = parse_options()
    common.main_cli(admin_parse_and_run, parser, args)
