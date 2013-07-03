import argparse
import rest
import helpers
import json
import sys
from help_parser import *
from cStringIO import StringIO
from argparse import RawTextHelpFormatter

def parse_options():
    """
    Handle node-cli command-line options with argparse
    """
    parent_parser = argparse.ArgumentParser(add_help=False)
    # We create top level parser
    parser = argparse.ArgumentParser(parents=[parent_parser], epilog=PARSER_EPILOG % {'cli' : 'node', 'option' : '--update'}+COMMAND_EPILOG, 
        formatter_class=RawTextHelpFormatter)
    parser.add_argument('-u', '--user', dest='username')
    parser.add_argument('-p', '--password', dest='password')

    parser.add_argument('-i', '--id',dest='experiment_id', type=int, help='experiment id submission')
    parser.add_argument('-a', '--append', action='append', dest='command_list', 
         help='nodes list')
    parser.add_argument('-b', '--battery', action='store_true', dest='battery',
         help='battery mode for start command (dc mode by default)')
    command_group = parser.add_mutually_exclusive_group(required=True)
    command_group.add_argument('--start', action='store_true', help='start command')
    command_group.add_argument('--stop', action='store_true', help='stop command')
    command_group.add_argument('--reset', action='store_true', help='reset command')
    command_group.add_argument('--update', dest='path_file', help='firmware path file')

    return parser

def command_node(parser_options, request, parser):
    """ Launch commands (start, stop, reset, update) on resources (JSONArray) user experiment

    :param parser_options: command-line parser options
    :type parser_options: Namespace object with options attribute
    :param request: API Rest request object
    :param parser: command-line parser
    """
    if (parser_options.experiment_id is not None):
       experiment_id = parser_options.experiment_id
    else:
       queryset = "state=Running&limit=0&offset=0"
       experiments_json = json.loads(request.get_experiments(queryset))    
       experiment_id = helpers.check_experiments_running(experiments_json, parser)
    nodes = []
    if (parser_options.command_list is not None):
       for nodes_list in parser_options.command_list:
           param_list  = helpers.check_command_list(nodes_list, parser)
           sites_json = json.loads(request.get_sites())
           site = helpers.check_site(param_list[0], sites_json, parser)
           nodes += helpers.check_nodes_list(site, param_list[1], parser)
       nodes_json = json.dumps(nodes, cls=rest.Encoder, sort_keys=True, indent=4)
    else:
       # all the nodes
       nodes_json = '[]'
    if (parser_options.start):
       if (parser_options.battery):
          request.start_command(experiment_id, nodes_json, battery=True)
       else:
          request.start_command(experiment_id, nodes_json)
    elif (parser_options.stop):
       request.stop_command(experiment_id, nodes_json)
    elif (parser_options.reset):
       request.reset_command(experiment_id, nodes_json)
    elif (parser_options.path_file is not None):
       command_files = {}
       firmware_name, firmware_body = helpers.check_command_firmware(parser_options.path_file, parser)
       command_files[firmware_name] = firmware_body
       command_filehandle = StringIO(nodes_json)
       command_files['nodes.json']=command_filehandle.read()
       command_filehandle.close()
       request.update_command(experiment_id, command_files)

def main():
    """
    Main command-line execution loop."
    """
    try:
       parser = parse_options()
       parser_options = parser.parse_args()
       request = rest.Api(username=parser_options.username, password=parser_options.password, 
           parser=parser)
       command_node(parser_options, request, parser)
    except KeyboardInterrupt:
        print >> sys.stderr, "\nStopped."
        sys.exit()

