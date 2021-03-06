# -*- coding:utf-8 -*-

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

"""Robot parser"""
import sys
import argparse

from iotlabcli import rest
from iotlabcli import auth
from iotlabcli import helpers
from iotlabcli.parser import common
import iotlabcli.robot

ROBOT_PARSER = """iotlab-robot manages interaction with nodes \
on a turtlebot."""


def parse_options():
    """ Handle iotlab-robot command-line options with argparse """

    parent_parser = common.base_parser()
    # We create top level parser
    parser = argparse.ArgumentParser(parents=[parent_parser])

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True  # not required by default in Python3

    # Robot Commands

    # 'status' command
    status_parser = subparsers.add_parser('status', help='Get robot status')
    common.add_nodes_selection_list(status_parser)
    common.add_expid_arg(status_parser)

    # 'update' command
    up_parser = subparsers.add_parser('update', help='Update robot mobility')
    up_parser.add_argument('-n', '--name', dest='up_name', required=True,
                           help='Update robot mobility')
    common.add_nodes_selection_list(up_parser)
    common.add_expid_arg(up_parser)

    # Mobility commands

    # 'get' command
    get_parser = subparsers.add_parser('get',
                                       help='Get robot mobilities')
    get_group = get_parser.add_mutually_exclusive_group(required=True)
    get_group.add_argument('-l', '--list', dest='list',
                           action='store_true',
                           help='Get circuits list')
    get_group.add_argument('-n', '--name', dest='get_name',
                           help='Get circuit')
    get_parser.add_argument('--site', action='append', dest='get_selection',
                            type=lambda x: ('site', x),
                            help='filter list by site')
    get_parser.add_argument('--type', action='append', dest='get_selection',
                            type=lambda x: ('type', x),
                            help='filter list by circuit type')

    return parser


def robot_parse_and_run(opts):  # noqa  # Too complex but straightforward
    """ Parse namespace 'opts' object and execute requested command """
    user, passwd = auth.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)

    command = opts.command

    if command == 'status':
        exp_id = helpers.get_current_experiment(api, opts.experiment_id)
        nodes = common.list_nodes(api, exp_id, opts.nodes_list,
                                  opts.exclude_nodes_list)
        ret = iotlabcli.robot.robot_command(api, 'status', exp_id, nodes)
    elif command == 'update':
        exp_id = helpers.get_current_experiment(api, opts.experiment_id)
        nodes = common.list_nodes(api, exp_id, opts.nodes_list,
                                  opts.exclude_nodes_list)
        ret = iotlabcli.robot.robot_update_mobility(api, exp_id,
                                                    opts.up_name, nodes)
    elif command == 'get' and opts.list:
        selection = dict(opts.get_selection or ())
        ret = iotlabcli.robot.circuit_command(api, 'list', **selection)
    elif command == 'get' and opts.get_name is not None:
        ret = iotlabcli.robot.circuit_command(api, 'get', opts.get_name)

    else:  # pragma: no cover
        raise ValueError('Unknown command')

    return ret


def main(args=None):
    """ Main command-line execution loop." """
    args = args or sys.argv[1:]
    parser = parse_options()
    common.main_cli(robot_parse_and_run, parser, args)
