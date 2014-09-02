# -*- coding:utf-8 -*-
"""Node parser"""

import argparse
import json
import sys
from argparse import RawTextHelpFormatter
from iotlabcli import Error
from iotlabcli import rest, helpers, help_parser
from iotlabcli import parser_common


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
    cmd_group = parser.add_mutually_exclusive_group(required=True)

    cmd_group.add_argument(
        '-sta', '--start', action='store_true', help='start command')

    cmd_group.add_argument(
        '-sto', '--stop', action='store_true', help='stop command')

    cmd_group.add_argument(
        '-r', '--reset', action='store_true', help='reset command')

    cmd_group.add_argument('-up', '--update', dest='path_file',
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

    if nodes_list is not None:
        nodes = []
        for nodes_sublist in nodes_list:
            nodes.extend(nodes_sublist)
        return nodes

    elif excl_nodes_list is not None:
        # get nodes to exclude
        excl_nodes = []
        for nodes_sublist in excl_nodes_list:
            excl_nodes.extend(nodes_sublist)

        # get experiment nodes
        exp_resources = api.get_experiment_resources(exp_id)
        exp_nodes = [res["network_address"] for res in exp_resources["items"]]

        # remove exclude nodes from experiment nodes
        nodes = [node for node in exp_nodes if node not in excl_nodes]
        return nodes
    else:
        # all the nodes
        return []


def node_command(api, command, exp_id, nodes_list, firmware_path=None):
    """ Launch commands (start, stop, reset, update)
    on resources (JSONArray) user experiment

    :param api: API Rest api object
    :param command: command that should be run
    :param exp_id: Target experiment id
    :param nodes_list: List of nodes where to run command
    :param firmware_path: Firmware path for update command
    """

    # TODO remove JSON here, I think
    nodes_json = json.dumps(nodes_list, cls=rest.Encoder, sort_keys=True)

    result = None
    if 'start' == command:
        result = api.start_command(exp_id, nodes_json)
    elif 'stop' == command:
        result = api.stop_command(exp_id, nodes_json)
    elif 'reset' == command:
        result = api.reset_command(exp_id, nodes_json)
    elif 'update' == command:
        if firmware_path is None:
            raise Error("Update command requires a firmware: %s" %
                        firmware_path)
        f_name, f_data = helpers.open_file(firmware_path)
        command_files = {
            f_name: f_data,
            'nodes.json': nodes_json
        }
        result = api.update_command(exp_id, command_files)

    return result


def node_parse_and_run(opts):
    """ Parse namespace 'opts' object and execute requested command """
    user, passwd = helpers.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)
    exp_id = helpers.get_current_experiment(opts.experiment_id)

    # TODO see if it can be included in argparse job
    firmware = None
    if opts.start:
        command = 'start'
    elif opts.stop:
        command = 'stop'
    elif opts.reset:
        command = 'reset'
    elif opts.path_file is not None:
        command = 'update'
        firmware = opts.path_file

    nodes = list_nodes(api, exp_id, opts.nodes_list, opts.exclude_nodes_list)

    return node_command(api, command, exp_id, nodes, firmware)


def main(args=sys.argv[1:]):
    """ Main command-line execution loop." """
    parser = parse_options()
    try:
        parser_opts = parser.parse_args(args)
        result = node_parse_and_run(parser_opts)
        print json.dumps(result, indent=4, sort_keys=True)
    except Error as err:
        parser.error(str(err))
    except KeyboardInterrupt:
        print >> sys.stderr, "\nStopped."
        sys.exit()
