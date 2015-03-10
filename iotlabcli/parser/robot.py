# -*- coding:utf-8 -*-
"""Robot parser"""
import argparse
import sys
from argparse import RawTextHelpFormatter
from iotlabcli import rest
from iotlabcli import auth
from iotlabcli import helpers
from iotlabcli.parser import help_msgs
from iotlabcli.parser import common
import iotlabcli.robot

ROBOT_PARSER = """robot-cli manages interaction with nodes on a turtlebot."""


def parse_options():
    """ Handle node-cli command-line options with argparse """

    parent_parser = common.base_parser()
    # We create top level parser
    parser = argparse.ArgumentParser(
        parents=[parent_parser], formatter_class=RawTextHelpFormatter,
        epilog=(help_msgs.PARSER_EPILOG.format(cli='robot', option='--status'))
        # + # help_msgs.COMMAND_EPILOG),  # TODO
    )

    parser.add_argument(
        '-i', '--id', dest='experiment_id', type=int,
        help='experiment id submission')

    # command
    cmd_group = parser.add_mutually_exclusive_group(required=True)

    cmd_group.add_argument(
        '-s', '--status', help='Get robot status', const='status',
        dest='command', action='store_const')

    # nodes list or exclude list
    common.add_nodes_selection_list(parser)

    return parser


def robot_parse_and_run(opts):
    """ Parse namespace 'opts' object and execute requested command """
    user, passwd = auth.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)
    exp_id = helpers.get_current_experiment(api, opts.experiment_id)

    command = opts.command
    nodes = common.list_nodes(api, exp_id, opts.nodes_list,
                              opts.exclude_nodes_list)
    return iotlabcli.robot.robot_command(api, command, exp_id, nodes)


def main(args=None):
    """ Main command-line execution loop." """
    args = args or sys.argv[1:]
    parser = parse_options()
    common.main_cli(robot_parse_and_run, parser, args)
