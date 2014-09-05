# -*- coding:utf-8 -*-
"""Node parser"""

import argparse
import json
import sys
import itertools
from argparse import RawTextHelpFormatter
from iotlabcli import Error
from iotlabcli import rest, help_parser
from iotlabcli import parser_common


import iotlabcli.helpers as helpers  # for mocking


def parse_options():
    """ Handle node-cli command-line options with argparse """

    parent_parser = parser_common.base_parser()
    # We create top level parser
    parser = argparse.ArgumentParser(
        parents=[parent_parser], formatter_class=RawTextHelpFormatter,
        epilog=(help_parser.PARSER_EPILOG
                % {'cli': 'node', 'option': '--update'}
                + help_parser.COMMAND_EPILOG),
    )

    parser.add_argument(
        '-i', '--id', dest='experiment_id', type=int,
        help='experiment id submission')

    # command
    # 'update' sets firmware name to firmware_path, so cannot set command
    parser.set_defaults(command='update')
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

    cmd_group.add_argument('-up', '--update',
                           dest='firmware_path', default=None,
                           help='flash firmware command with path file')

    # nodes list or exclude list
    list_group = parser.add_mutually_exclusive_group()

    list_group.add_argument(
        '-e', '--exclude', action='append',
        type=helpers.nodes_list_from_str,
        dest='exclude_nodes_list', help='exclude nodes list')
    list_group.add_argument(
        '-l', '--list', action='append',
        type=helpers.nodes_list_from_str,
        dest='nodes_list', help='nodes list')

    return parser


def list_nodes(api, exp_id, nodes_list=None, excl_nodes_list=None):
    """ Return the list of nodes where the command will apply """

    if nodes_list is not None:
        # flatten lists into one
        nodes = list(itertools.chain.from_iterable(nodes_list))

    elif excl_nodes_list is not None:
        # flatten lists into one
        excl_nodes = list(itertools.chain.from_iterable(excl_nodes_list))

        # get experiment nodes
        exp_resources = api.get_experiment_resources(exp_id)
        exp_nodes = [res["network_address"] for res in exp_resources["items"]]

        # remove exclude nodes from experiment nodes
        nodes = [node for node in exp_nodes if node not in excl_nodes]

    else:
        nodes = []  # all the nodes

    return nodes


def node_command(api, command, exp_id, nodes_list, firmware_path=None):
    """ Launch commands (start, stop, reset, update)
    on resources (JSONArray) user experiment

    :param api: API Rest api object
    :param command: command that should be run
    :param exp_id: Target experiment id
    :param nodes_list: List of nodes where to run command
    :param firmware_path: Firmware path for update command
    """
    assert command in ('update', 'start', 'stop', 'reset')

    result = None
    if 'update' == command:
        if firmware_path is None:
            raise Error("Update cmd requires a firmware: %s" % firmware_path)
        files = {}
        helpers.add_to_dict_uniq(files, *helpers.open_file(firmware_path))
        helpers.add_to_dict_uniq(files, 'nodes.json', json.dumps(nodes_list))
        result = api.node_update(exp_id, files)
    else:
        result = api.node_command(command, exp_id, nodes_list)

    return result


def node_parse_and_run(opts):
    """ Parse namespace 'opts' object and execute requested command """
    user, passwd = helpers.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)
    exp_id = helpers.get_current_experiment(opts.experiment_id)

    command = opts.command
    firmware = opts.firmware_path  # None if command != 'update'

    nodes = list_nodes(api, exp_id, opts.nodes_list, opts.exclude_nodes_list)

    return node_command(api, command, exp_id, nodes, firmware)


def main(args=sys.argv[1:]):
    """ Main command-line execution loop." """
    parser = parse_options()
    parser_common.main_cli(node_parse_and_run, parser, args)
