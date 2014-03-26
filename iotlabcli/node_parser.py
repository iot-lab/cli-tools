# -*- coding:utf-8 -*-
"""Node parser"""

import argparse
import json
import sys
from cStringIO import StringIO
from argparse import RawTextHelpFormatter
from iotlabcli import rest, helpers, help_parser


def parse_options():
    """
    Handle node-cli command-line options with argparse
    """
    parent_parser = argparse.ArgumentParser(add_help=False)
    # We create top level parser
    parser = argparse.ArgumentParser(
        parents=[parent_parser],
        epilog=help_parser.PARSER_EPILOG
        % {'cli': 'node', 'option': '--update'}
        + help_parser.COMMAND_EPILOG,
        formatter_class=RawTextHelpFormatter)

    parser.add_argument('-u', '--user', dest='username')
    parser.add_argument('-p', '--password', dest='password')

    parser.add_argument(
        '-i', '--id', dest='experiment_id', type=int,
        help='experiment id submission')

    parser.add_argument(
        '-l', '--list', action='append',
        dest='command_list',
        help='nodes list')

    parser.add_argument(
        '-b',
        '--battery',
        action='store_true', dest='battery',
        help='battery mode for start command (dc mode by default)')

    command_group = parser.add_mutually_exclusive_group(required=True)

    command_group.add_argument(
        '--start', action='store_true',
        help='start command')

    command_group.add_argument(
        '--stop', action='store_true',
        help='stop command')

    command_group.add_argument(
        '--reset', action='store_true',
        help='reset command')

    command_group.add_argument(
        '--update', dest='path_file',
        help='firmware path file')

    return parser


def command_node(parser_options, request, parser):
    """ Launch commands (start, stop, reset, update)
    on resources (JSONArray) user experiment

    :param parser_options: command-line parser options
    :type parser_options: Namespace object with options attribute
    :param request: API Rest request object
    :param parser: command-line parser
    """
    if parser_options.experiment_id is not None:
        experiment_id = parser_options.experiment_id
    else:
        queryset = "state=Running&limit=0&offset=0"
        experiments_json = json.loads(request.get_experiments(queryset))
        experiment_id = helpers.check_experiments_running(
            experiments_json, parser)
    nodes = []
    if parser_options.command_list is not None:
        for nodes_list in parser_options.command_list:
            param_list = helpers.check_command_list(nodes_list, parser)
            sites_json = json.loads(request.get_sites())
            site = helpers.check_site(param_list[0], sites_json, parser)
            archi = helpers.check_archi(param_list[1], parser)
            nodes += helpers.check_nodes_list(site,
                                              param_list[0],
                                              archi,
                                              parser)
        nodes_json = json.dumps(
            nodes, cls=rest.Encoder, sort_keys=True, indent=4)
    else:
        # all the nodes
        nodes_json = '[]'
    if parser_options.start:
        if parser_options.battery:
            json_start = request.start_command(experiment_id, nodes_json, battery=True)
        else:
            json_start = request.start_command(experiment_id, nodes_json)
        print json.dumps(json.loads(json_start), indent=4, sort_keys=True)
    elif parser_options.stop:
        json_stop = request.stop_command(experiment_id, nodes_json)
        print json.dumps(json.loads(json_stop), indent=4, sort_keys=True)
    elif parser_options.reset:
        json_reset = request.reset_command(experiment_id, nodes_json)
        print json.dumps(json.loads(json_reset), indent=4, sort_keys=True)
    elif parser_options.path_file is not None:
        command_files = {}
        firmware_name, firmware_data = helpers.open_file(
            parser_options.path_file, parser)
        command_files[firmware_name] = firmware_data
        command_filehandle = StringIO(nodes_json)
        command_files['nodes.json'] = command_filehandle.read()
        command_filehandle.close()
        json_update = request.update_command(experiment_id, command_files)
        print json.dumps(json.loads(json_update), indent=4, sort_keys=True)


def main(args=sys.argv[1:]):
    """
    Main command-line execution loop."
    """
    try:
        parser = parse_options()
        parser_options = parser.parse_args(args)
        request = rest.Api(
            username=parser_options.username,
            password=parser_options.password,
            parser=parser)
        command_node(parser_options, request, parser)
    except KeyboardInterrupt:
        print >> sys.stderr, "\nStopped."
        sys.exit()
