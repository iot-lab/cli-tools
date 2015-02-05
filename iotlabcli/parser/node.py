# -*- coding:utf-8 -*-
"""Node parser"""

import argparse
import sys
import itertools
from argparse import RawTextHelpFormatter, ArgumentTypeError
from iotlabcli import rest
from iotlabcli import helpers
from iotlabcli import auth
import iotlabcli.node
from iotlabcli.parser import help_msgs
from iotlabcli.parser import common


def parse_options():
    """ Handle node-cli command-line options with argparse """

    parent_parser = common.base_parser()
    # We create top level parser
    parser = argparse.ArgumentParser(
        parents=[parent_parser], formatter_class=RawTextHelpFormatter,
        epilog=(help_msgs.PARSER_EPILOG.format(cli='node', option='--update')
                + help_msgs.COMMAND_EPILOG),
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
        type=nodes_list_from_str,
        dest='exclude_nodes_list', help='exclude nodes list')
    list_group.add_argument(
        '-l', '--list', action='append',
        type=nodes_list_from_str,
        dest='nodes_list', help='nodes list')

    return parser


def nodes_list_from_str(nodes_list_str):
    """ Convert the nodes_list_str to a list of nodes hostname
    Checks that given site exist
    :param nodes_list_str: short nodes format: site_name,archi,node_id_list
                           example: 'grenoble,m3,1-34+72'
    :returns: ['m3-1.grenoble.iot-lab.info', ...]
    """
    try:
        # 'grenoble,m3,1-34+72' -> ['grenoble', 'm3', '1-34+72']
        site, archi, nodes_str = nodes_list_str.split(',')
    except ValueError:
        raise ArgumentTypeError(
            'Invalid number of argument in nodes list: %r' % nodes_list_str)
    common.check_site_with_server(site)  # needs an external request
    return common.nodes_list_from_info(site, archi, nodes_str)


def _get_experiment_nodes_list(api, exp_id):
    """ Get the nodes_list for given experiment"""
    exp_resources = api.get_experiment_info(exp_id, 'resources')
    exp_nodes = [res["network_address"] for res in exp_resources["items"]]
    return exp_nodes


def list_nodes(api, exp_id, nodes_ll=None, excl_nodes_ll=None):
    """ Return the list of nodes where the command will apply """

    if nodes_ll is not None:
        # flatten lists into one
        nodes = list(itertools.chain.from_iterable(nodes_ll))

    elif excl_nodes_ll is not None:
        # flatten lists into one
        excl_nodes = set(itertools.chain.from_iterable(excl_nodes_ll))

        # remove exclude nodes from experiment nodes
        exp_nodes = set(_get_experiment_nodes_list(api, exp_id))
        nodes = list(exp_nodes - excl_nodes)
    else:
        nodes = []  # all the nodes

    return sorted(nodes, key=helpers.node_url_sort_key)


def node_parse_and_run(opts):
    """ Parse namespace 'opts' object and execute requested command """
    user, passwd = auth.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)
    exp_id = helpers.get_current_experiment(api, opts.experiment_id)

    command = opts.command
    firmware = opts.firmware_path  # None if command != 'update'

    nodes = list_nodes(api, exp_id, opts.nodes_list, opts.exclude_nodes_list)

    return iotlabcli.node.node_command(api, command, exp_id, nodes, firmware)


def main(args=None):
    """ Main command-line execution loop." """
    args = args or sys.argv[1:]
    parser = parse_options()
    common.main_cli(node_parse_and_run, parser, args)
