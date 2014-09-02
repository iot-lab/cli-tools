# -*- coding:utf-8 -*-
"""Node parser"""

import argparse
import json
import sys
from cStringIO import StringIO
from argparse import RawTextHelpFormatter
from iotlabcli import Error
from iotlabcli import rest, helpers, help_parser
from iotlabcli import parser_common


def parse_options():
    """
    Handle node-cli command-line options with argparse
    """
    parent_parser = parser_common.base_parser()
    # We create top level parser
    parser = argparse.ArgumentParser(
        parents=[parent_parser],
        epilog=help_parser.PARSER_EPILOG
        % {'cli': 'node', 'option': '--update'}
        + help_parser.COMMAND_EPILOG,
        formatter_class=RawTextHelpFormatter)

    parser.add_argument(
        '-i', '--id', dest='experiment_id', type=int,
        help='experiment id submission')

    list_group = parser.add_mutually_exclusive_group()

    list_group.add_argument(
        '-e', '--exclude', action='append',
        dest='exclude_nodes_list',
        help='exclude nodes list')

    list_group.add_argument(
        '-l', '--list', action='append',
        dest='nodes_list',
        help='nodes list')

    command_group = parser.add_mutually_exclusive_group(required=True)

    command_group.add_argument('-sta', '--start', action='store_true',
                               help='start command')

    command_group.add_argument('-sto', '--stop', action='store_true',
                               help='stop command')

    command_group.add_argument('-r', '--reset', action='store_true',
                               help='reset command')

    command_group.add_argument('-up', '--update', dest='path_file',
                               help='flash firmware command with path file')

    return parser


def command_node(parser_options, request):
    """ Launch commands (start, stop, reset, update)
    on resources (JSONArray) user experiment

    :param parser_options: command-line parser options
    :type parser_options: Namespace object with options attribute
    :param request: API Rest request object
    """
    exp_id = request.get_current_experiment(parser_options.experiment_id)

    nodes = []
    if parser_options.nodes_list is not None:
        sites_json = json.loads(request.get_sites())
        for nodes_list in parser_options.nodes_list:
            param_list = helpers.check_command_list(nodes_list)
            site = helpers.check_site(param_list[0], sites_json)
            archi = helpers.check_archi(param_list[1])
            nodes += helpers.check_nodes_list(site,
                                              archi,
                                              param_list[2])
        nodes_json = json.dumps(
            nodes, cls=rest.Encoder, sort_keys=True, indent=4)
    elif parser_options.exclude_nodes_list is not None:
        exclude_nodes = []
        sites_json = json.loads(request.get_sites())
        for exclude_list in parser_options.exclude_nodes_list:
            param_list = helpers.check_command_list(exclude_list)
            sites_json = json.loads(request.get_sites())
            site = helpers.check_site(param_list[0], sites_json)
            archi = helpers.check_archi(param_list[1])
            exclude_nodes += helpers.check_nodes_list(
                site, archi, param_list[2])
        experiment_resources_json = \
            json.loads(request.get_experiment_resources(exp_id))
        exp_nodes = []
        for res in experiment_resources_json["items"]:
            exp_nodes.append(res["network_address"])
        nodes = [node for node in exp_nodes if node not in exclude_nodes]
        nodes_json = json.dumps(
            nodes, cls=rest.Encoder, sort_keys=True, indent=4)
    else:
        # all the nodes
        nodes_json = '[]'
    if parser_options.start:
        json_start = request.start_command(exp_id, nodes_json)
        print json.dumps(json.loads(json_start), indent=4, sort_keys=True)
    elif parser_options.stop:
        json_stop = request.stop_command(exp_id, nodes_json)
        print json.dumps(json.loads(json_stop), indent=4, sort_keys=True)
    elif parser_options.reset:
        json_reset = request.reset_command(exp_id, nodes_json)
        print json.dumps(json.loads(json_reset), indent=4, sort_keys=True)
    elif parser_options.path_file is not None:
        command_files = {}
        firmware_name, firmware_data = helpers.open_file(
            parser_options.path_file)
        command_files[firmware_name] = firmware_data
        command_filehandle = StringIO(nodes_json)
        command_files['nodes.json'] = command_filehandle.read()
        command_filehandle.close()
        json_update = request.update_command(exp_id, command_files)
        print json.dumps(json.loads(json_update), indent=4, sort_keys=True)


def main(args=sys.argv[1:]):
    """
    Main command-line execution loop."
    """
    parser = parse_options()
    try:
        parser_options = parser.parse_args(args)
        request = rest.Api(parser_options.username, parser_options.password)
        command_node(parser_options, request)
    except Error as err:
        parser.error(str(err))
    except KeyboardInterrupt:
        print >> sys.stderr, "\nStopped."
        sys.exit()
