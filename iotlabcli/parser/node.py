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

"""Node parser"""

import sys
import argparse
from argparse import RawTextHelpFormatter

from iotlabcli import rest
from iotlabcli import helpers
from iotlabcli import auth
import iotlabcli.node
from iotlabcli.parser import help_msgs
from iotlabcli.parser import common

NODE_PARSER = """

node-cli manages interaction with resources.
You can launch commands on your experiment's resources.

"""

NODE_EPILOG = """

Examples:
    * update firmware on all experiment resources
        $ node-cli --update /home/tp.hex
        Note : with one experiment in the state Running
    * Launch command stop on experiment resources list
        $ node-cli --sto -l grenoble,m3,1-5+10+12
    * update firmware on all experiment resources except two
        $ node-cli --update /home/tp.hex -e grenoble,m3,1-2
    * commmand list : site_name,archi,nodeid_list
        $ node-cli --reset -l grenoble,wsn430,1-34+72
    * command with several experiments with state Running
        $ node-cli -i <expid> --reset

"""


def parse_options():
    """ Handle node-cli command-line options with argparse """

    parent_parser = common.base_parser()
    # We create top level parser
    parser = argparse.ArgumentParser(
        description=NODE_PARSER,
        parents=[parent_parser], formatter_class=RawTextHelpFormatter,
        epilog=(help_msgs.PARSER_EPILOG.format(cli='node', option='--update') +
                NODE_EPILOG),
    )

    common.add_expid_arg(parser)

    # command
    # argument with parameter can't both set 'command' and set argument value
    # so save argument, and command will be left to 'with_arguments'
    parser.set_defaults(command='with_argument')
    cmd_group = parser.add_mutually_exclusive_group(required=True)

    cmd_group.add_argument(
        '-sta', '--start', help='start command', const='start',
        dest='command', action='store_const')

    cmd_group.add_argument(
        '-sto', '--stop', help='stop command', const='stop',
        dest='command', action='store_const')

    cmd_group.add_argument(
        '-r', '--reset', help='reset command', const='reset',
        dest='command', action='store_const')

    cmd_group.add_argument(
        '--debug-start', help='start debugger', const='debug-start',
        dest='command', action='store_const')

    cmd_group.add_argument(
        '--debug-stop', help='stop debugger', const='debug-stop',
        dest='command', action='store_const')

    cmd_group.add_argument('-up', '--update',
                           dest='firmware_path', default=None,
                           help='flash firmware command with path file')

    cmd_group.add_argument('--profile', '--update-profile',
                           dest='profile_name', default=None,
                           help='change nodes current monitoring profile')

    # nodes list or exclude list
    common.add_nodes_selection_list(parser)

    return parser


def node_parse_and_run(opts):
    """ Parse namespace 'opts' object and execute requested command """
    user, passwd = auth.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)
    exp_id = helpers.get_current_experiment(api, opts.experiment_id)

    command = opts.command
    if opts.command != 'with_argument':
        # opts.command has a real value
        command = opts.command
        cmd_opt = None
    elif opts.firmware_path is not None:
        # opts.command has default value
        command = 'update'
        cmd_opt = opts.firmware_path
    elif opts.profile_name is not None:
        # opts.command has default value
        command = 'profile'
        cmd_opt = opts.profile_name
    else:  # pragma: no cover
        assert False, "Unknown command %r" % opts.command

    nodes = common.list_nodes(api, exp_id, opts.nodes_list,
                              opts.exclude_nodes_list)
    return iotlabcli.node.node_command(api, command, exp_id, nodes, cmd_opt)


def main(args=None):
    """ Main command-line execution loop." """
    args = args or sys.argv[1:]
    parser = parse_options()
    common.main_cli(node_parse_and_run, parser, args)
