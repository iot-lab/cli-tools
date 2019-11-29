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

iotlab-node manages interaction with nodes.
You can launch commands on your experiment's nodes.

"""

NODE_EPILOG = """

Examples:
    * update firmware on all experiment nodes
        $ iotlab-node --flash /home/tp.hex
        Note : with one experiment in the state Running
    * Launch command stop on experiment nodes list
        $ iotlab-node --sto -l grenoble,m3,1-5+10+12
    * update firmware on all experiment nodes except two
        $ iotlab-node --flash /home/tp.hex -e grenoble,m3,1-2
    * commmand list : site_name,archi,nodeid_list
        $ iotlab-node --reset -l grenoble,wsn430,1-34+72
    * command with several experiments with state Running
        $ iotlab-node -i <expid> --reset

"""


def parse_options():
    """ Handle iotlab-node command-line options with argparse """

    parent_parser = common.base_parser()
    # We create top level parser
    parser = argparse.ArgumentParser(
        description=NODE_PARSER,
        parents=[parent_parser], formatter_class=RawTextHelpFormatter,
        epilog=(help_msgs.PARSER_EPILOG.format(cli='node', option='--flash') +
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
    cmd_group.add_argument('-fl', '--flash',
                           dest='firmware_path', default=None,
                           help='flash firmware command with path file')
    cmd_group.add_argument(
        '--flash-idle', help='flash idle firmware', const='flash-idle',
        dest='command', action='store_const')
    cmd_group.add_argument(
        '--debug-start', help='start debugger', const='debug-start',
        dest='command', action='store_const')
    cmd_group.add_argument(
        '--debug-stop', help='stop debugger', const='debug-stop',
        dest='command', action='store_const')
    cmd_group.add_argument('--profile', '--update-profile',
                           dest='profile_name', default=None,
                           help='change nodes current monitoring profile')
    cmd_group.add_argument('--profile-load',
                           dest='profile_path', default=None,
                           help=('change nodes current monitoring profile'
                                 ' with provided JSON'))
    cmd_group.add_argument('--profile-reset',
                           dest='command', const='profile-reset',
                           action='store_const',
                           help='reset to default no monitoring profile')
    cmd_group.add_argument(
        '--update-idle', help='DEPRECATED: use --flash-idle',
        const='update-idle', dest='command', action='store_const')
    cmd_group.add_argument('-up', '--update',
                           dest='up_firmware_path', default=None,
                           help='DEPRECATED: use -fl or --flash option')
    # nodes list or exclude list
    common.add_nodes_selection_list(parser)

    return parser


def node_parse_and_run(opts):
    """ Parse namespace 'opts' object and execute requested command """
    user, passwd = auth.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)
    exp_id = helpers.get_current_experiment(api, opts.experiment_id)

    _deprecate_cmd(opts)

    if opts.command == 'with_argument':
        command, cmd_opt = _node_parse_command_and_opt(**vars(opts))
    else:
        # opts.command has a real value
        command, cmd_opt = (opts.command, None)

    nodes = common.list_nodes(api, exp_id, opts.nodes_list,
                              opts.exclude_nodes_list)

    return iotlabcli.node.node_command(api, command, exp_id, nodes, cmd_opt)


def _deprecate_cmd(opts):
    if opts.command == 'update-idle':
        new_cmd = 'flash-idle'
        helpers.deprecate_warn_cmd(opts.command, new_cmd, 7)
        opts.command = new_cmd
    if opts.up_firmware_path:
        helpers.deprecate_warn_cmd('update', 'flash', 7)
        opts.firmware_path = opts.up_firmware_path


def _node_parse_command_and_opt(**opts_dict):
    """Return 'command' and 'command_opt' from **opts_dict.


    Find which command has a non null attribute and returns it.

    >>> _node_parse_command_and_opt(firmware_path='/tmp/test',
    ...                             profile_name=None,
    ...                             profile_path=None,
    ...                             command='with_argument')
    ('flash', '/tmp/test')

    >>> _node_parse_command_and_opt(firmware_path=None,
    ...                             profile_name='consumption',
    ...                             profile_path=None,
    ...                             command='with_argument')
    ('profile', 'consumption')

    >>> _node_parse_command_and_opt(firmware_path=None,
    ...                             profile_name=None,
    ...                             profile_path='/tmp/prof.json',
    ...                             command='with_argument')
    ('profile-load', '/tmp/prof.json')

    # Case where the command is not managed
    >>> _node_parse_command_and_opt(firmware_path=None,
    ...                             profile_name=None,
    ...                             profile_path=None,
    ...                             command='with_argument')
    Traceback (most recent call last):
    ...
    ValueError: Unknown command
    """
    # Mapping between 'command' and argparse option name
    commands_arguments = {
        'flash': 'firmware_path',
        'profile': 'profile_name',
        'profile-load': 'profile_path',
    }

    for command, argname in commands_arguments.items():
        cmd_opt = opts_dict.get(argname, None)
        if cmd_opt is not None:
            return command, cmd_opt

    raise ValueError('Unknown command')


def main(args=None):
    """ Main command-line execution loop." """
    args = args or sys.argv[1:]
    parser = parse_options()
    common.main_cli(node_parse_and_run, parser, args)
