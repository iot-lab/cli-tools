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

"""Status parser"""

import sys
import argparse
from argparse import RawTextHelpFormatter

from iotlabcli import rest
from iotlabcli import auth
import iotlabcli.status
from iotlabcli.parser import help_msgs
from iotlabcli.parser import common

STATUS_PARSER = """

iotlab-status provides testbed status with informations about sites
experiments and nodes.

"""

STATUS_EPILOG = """

Examples:
    * get testbed sites list
        $ iotlab-status --sites
    * get testbed nodes list
        $ iotlab-status --nodes
    * get available (state=Alive) M3 nodes list on Grenoble site
        $ iotlab-status --nodes --site grenoble --archi m3 --state Alive
    * get testbed running experiments list
        $ iotlab-status --running

"""


def parse_options():
    """ Handle iotlab-status command-line options with argparse """

    parent_parser = common.base_parser()
    # We create top level parser
    epilog_msg = help_msgs.PARSER_EPILOG.format(cli='status',
                                                option='--sites')
    epilog_msg += STATUS_EPILOG
    parser = argparse.ArgumentParser(
        description=STATUS_PARSER,
        parents=[parent_parser], formatter_class=RawTextHelpFormatter,
        epilog=epilog_msg,
    )

    parser.set_defaults(command='with_argument')
    status_group = parser.add_mutually_exclusive_group(required=True)
    status_group.add_argument(
        '-s', '--sites', help='get testbed sites list', const='sites',
        dest='command', action='store_const')

    status_group.add_argument(
        '-n', '--nodes', help='get testbed nodes list', const='nodes',
        dest='command', action='store_const')

    status_group.add_argument(
        '-ni', '--nodes-ids', help='get testbed nodes ids list (1-3+5)',
        const='nodes-ids', dest='command', action='store_const')

    status_group.add_argument(
        '-er', '--experiments-running',
        help='get testbed running experiments list', const='experiments',
        dest='command', action='store_const')

    parser.add_argument('--site',
                        action='append', dest='nodes_selection',
                        type=lambda x: ('site', x),
                        help='testbed nodes list filter by site')
    parser.add_argument('--archi',
                        action='append', dest='nodes_selection',
                        type=lambda x: ('archi', x),
                        help='testbed nodes list filter by architecture')
    parser.add_argument('--state', action='append', dest='nodes_selection',
                        type=lambda x: ('state', x),
                        help='testbed nodes list filter by state')

    return parser


def status_parse_and_run(opts):
    """ Parse namespace 'opts' object and execute requested command """
    user, passwd = auth.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)
    selection = dict(opts.nodes_selection or ())
    return iotlabcli.status.status_command(api, opts.command, **selection)


def main(args=None):
    """ Main command-line execution loop." """
    args = args or sys.argv[1:]
    parser = parse_options()
    common.main_cli(status_parse_and_run, parser, args)
