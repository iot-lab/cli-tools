import argparse
import rest
import helpers
import json
import sys
from experiment import *
from help_parser import *
from cStringIO import StringIO
from argparse import RawTextHelpFormatter

def parse_options():
    """
    Handle experiment-cli command-line options with argparse
    """
    parent_parser = argparse.ArgumentParser(add_help=False)
    # We create top level parser
    parser = argparse.ArgumentParser(description=EXPERIMENT_PARSER, parents=[parent_parser], epilog=PARSER_EPILOG % {'cli' : 'experiment', 'option' : 'submit'}, 
        formatter_class=RawTextHelpFormatter)
    parser.add_argument('-u', '--user', dest='username')
    parser.add_argument('-p', '--password', dest='password')

    subparsers = parser.add_subparsers(dest='subparser_name')

    submit_experiment = subparsers.add_parser('submit', help='submit user experiment', 
        epilog=SUBMIT_EPILOG, formatter_class=RawTextHelpFormatter)
    stop_experiment = subparsers.add_parser('stop', help='stop user experiment')
    get_experiment = subparsers.add_parser('get', help='get user experiment')
    load_experiment = subparsers.add_parser('load', help='load and submit user experiment', 
        epilog=LOAD_EPILOG, formatter_class=RawTextHelpFormatter)
    info_experiment = subparsers.add_parser('info', help='testbed information for experiment submission',
        epilog=INFO_EPILOG, formatter_class=RawTextHelpFormatter)

    # submit_experiment.add_argument('-t','--type', dest='type', choices=['physical','alias'],
    #      required=True, help='experiment submission type : physical id or alias properties sensor nodes')
    submit_experiment.add_argument('-a', '--append', action='append', dest='exp_list', required=True,
         help="experiment list")
    submit_experiment.add_argument('-n', '--name', dest='name', help='experiment name')
    submit_experiment.add_argument('-d', '--duration', dest='duration', help='experiment duration in minutes',
         required=True, type=int)
    submit_experiment.add_argument('-r', '--reservation', dest='reservation', type=int,
         help='experiment schedule starting : seconds since 1970-01-01 00:00:00 UTC')
    submit_experiment.add_argument('-j', '--json', dest='json', action='store_true',
         help='print experiment JSON representation without submit it')

    stop_experiment.add_argument('-i', '--id', dest='experiment_id', type=int, help='experiment id submission')

    get_experiment.add_argument('-i', '--id', dest='experiment_id', type=int, help='experiment id submission')
    get_group = get_experiment.add_mutually_exclusive_group(required=True)
    get_group.add_argument('-a', '--archive', action='store_true', dest='archive',
         help='get experiment archive (tar.gz) with submission JSON representation and firmware(s)')
    get_group.add_argument('-j', '--json', action='store_true', dest='json', help='get experiment submission JSON representation')
    get_group.add_argument('-s', '--state', action='store_true', dest='state', help='get experiment state JSON representation')
    get_group.add_argument('-r', '--resources', action='store_true', dest='resources', help='get experiment resources list JSON representation')

    load_experiment.add_argument('-f', '--file', dest='path_file', required=True, help='experiment submission JSON representation path file')
    load_experiment.add_argument('-l', '--list', dest='path_firmware_list', help='firmware(s) path list')

    info_experiment.add_argument('--offset', dest='offset', type=int, help='start index of experiments total number')
    info_experiment.add_argument('--limit', dest='limit', type=int, help='limit number of experiments')
    info_experiment.add_argument('--state', dest='state', 
         help='experiment state filter : Terminated,Running')
    info_group = info_experiment.add_mutually_exclusive_group(required=True)
    info_group.add_argument('-s', '--sites', action='store_true', dest='sites', help='get testbed sites list JSON representation')
    info_group.add_argument('-r', '--resources', action='store_true', dest='resources', help='get testbed sensor nodes list JSON representation')
    info_group.add_argument('-t','--total',action='store_true',dest='experiment_total',
         help='get number of upcoming,running and past user\'s experiment JSON representation')
    info_group.add_argument('-e','--exp',action='store_true',dest='experiment_list',help='get user\'s experiment list JSON representation')
    info_group.add_argument('-rs',action='store_true',dest='state_list',help='get testbed sensor nodes state list JSON representation (e.g. 1-5+7)')

    return parser


def submit_experiment(parser_options, request, parser):
    """ Submit user experiment with JSON Encoder serialization object Experiment and firmware(s).
     If submission is accepted by scheduler OAR we print JSONObject response with id submission.

    :param parser_options: command-line parser options
    :type parser_options: Namespace object with options attribute
    :param request: API Rest request object
    :param parser: command-line parser
    """
    experiment_files = {}
    firmwares = {}
    alias_number = 0
    physical_type = False
    alias_type = False
    experiment = Experiment(name=parser_options.name, duration=parser_options.duration, reservation=parser_options.reservation)
    sites_json = json.loads(request.get_sites())
    for exp_list in parser_options.exp_list:
        experiment_type, param_list  = helpers.check_experiment_list(exp_list, parser)
        experiment.type = experiment_type
        if (experiment_type == 'physical' and not alias_type):
           physical_type = True
           site = helpers.check_site(param_list[0], sites_json, parser)
           nodes_list = param_list[1]
           nodes = helpers.check_nodes_list(site, nodes_list, parser)
           experiment.set_physical_nodes(nodes)
        # experiment alias type
        elif (experiment_type == 'alias' and not physical_type):
           alias_type = True
           alias_number += 1
           nb_nodes = param_list[0]
           properties_list = param_list[1]
           properties = helpers.check_properties(properties_list, sites_json, parser)
           experiment.set_alias_nodes(alias_number, int(nb_nodes), properties)
           nodes = ["%d" % alias_number]
        else:
           parser.error("Experiment list is not valid with two different types : alias and physical")
        # firmware associations
        if (len(param_list)>2 and param_list[2] != ""):
           firmware_path=param_list[2]
           firmware_name, firmware_body, firmwares = helpers.check_experiment_firmwares(firmware_path, firmwares, parser)
           experiment_files[firmware_name] = firmware_body
           experiment.set_firmware_associations(firmware_name, nodes)
        # profile associations
        if (len(param_list)==4 and param_list[3] != ""):
           profile_name=param_list[3]
           experiment.set_profile_associations(profile_name, nodes)
    experiment_json = json.dumps(experiment, cls=rest.Encoder, sort_keys=True, indent=4)
    if (parser_options.json):
       print experiment_json
    else:
       experiment_filehandle = StringIO(experiment_json)
       # static name for experiment file : rename by server-rest with id_oar.json
       experiment_files['new_exp.json']=experiment_filehandle.read()
       experiment_filehandle.close()
       oar_json = request.submit_experiment(experiment_files)
       print(json.dumps(json.loads(oar_json), indent=4, sort_keys=True))

def stop_experiment(parser_options, request, parser):
    """ Stop user experiment submission.

    :param experiment_id: scheduler OAR id submission
    :type experiment_id: string
    :param request: API Rest request object
    """
    if (parser_options.experiment_id is not None):
       experiment_id = parser_options.experiment_id
    else:
       queryset = "state=Running&limit=0&offset=0"
       experiments_json = json.loads(request.get_experiments(queryset))
       experiment_id = helpers.check_experiments_running(experiments_json, parser)
    request.stop_experiment(experiment_id)

def get_experiment(parser_options, request, parser):
    """ Get user experiment's description :
    _ download archive file (tar.gz) with JSONObject experiment description and firmware(s)
    _ print JSONObject with experiment state
    _ print JSONObject with experiment owner
    _ print JSONObject with experiment description

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
    if (parser_options.archive):
       data = request.get_experiment_archive(experiment_id)
       helpers.write_experiment_archive(experiment_id, data, parser)
    else:
       if (parser_options.json):
          experiment_json = request.get_experiment(experiment_id)
       elif (parser_options.state):
          experiment_json = request.get_experiment_state(experiment_id)
       elif (parser_options.resources):
          experiment_json = request.get_experiment_resources(experiment_id)
       print(json.dumps(json.loads(experiment_json), indent=4, sort_keys=True))

def load_experiment(parser_options, request, parser):
    """ Load and submit user experiment description with firmware(s)

    :param parser_options: command-line parser options
    :type parser_options: Namespace object with options attribute
    :param request: API Rest request object
    :param parser: command-line parser
    """
    experiment_files = {}
    firmwares = {}
    firmware_list = parser_options.firmware_list
    experiment_file_name, experiment_file_data = helpers.open_json_file(parser_options.path_file, parser)
    experiment_json = helpers.read_json_file(experiment_file_name, experiment_file_data, parser)
    firmware_associations =  experiment_json['firmwareassociations']
    # static name for experiment file : rename by server-rest with id_oar.json
    experiment_files['new_exp.json'] = experiment_file_data
    if (path_firmware_list is not None and firmware_associations is None):
       parser.error("You don't have firmware(s) in your experiment JSON description")
    elif (path_firmware_list is not None):
       firmware = firmware_list.split(',')
       for firmware_path in firmware:
           firmware_name, firmware_body, firmwares = helpers.check_experiment_firmwares(firmware_path, firmwares, parser)
           experiment_files[firmware_name] = firmware_body
    if (firmware_associations is not None):
       for firmware in firmware_associations:
           firmware_name = firmware['firmwarename']
           if (not experiment_files.has_key(firmware_name)):
              firmware_name, firmware_body, firmwares = helpers.check_experiment_firmwares(firmware_name, firmwares, parser)
              experiment_files[firmware_name] = firmware_body
    if (not len(firmware_associations) == len(experiment_files)-1):
       parser.error("You have more firmware(s) in your firmware list than in experiment JSON description")
    request.start_experiment(experiment_files)

def info_experiment(parser_options, request, parser):
    """ Print testbed information for user experiment submission:
    _ print JSONObject sites descrition
    _ print JSONObject resources description
    _ print JSONObject number of past, running, upcoming user's experiment
    _ print JSONObject user's experiment

    :param parser_options: command-line parser options
    :type parser_options: Namespace object with options attribute
    :param request: API Rest request object
    :param parser: command-line parser
    """
    if (parser_options.sites):
       info_json = request.get_sites()
    elif (parser_options.resources):
       info_json = request.get_resources()
    elif (parser_options.experiment_total):
       info_json = request.get_experiments_total()
    elif (parser_options.state_list):
       info_json = request.get_resources_state()
    elif (parser_options.experiment_list):
       limit = parser_options.limit
       offset = parser_options.offset
       state = helpers.check_experiment_state(parser_options.state, parser)
       queryset = 'state='+state
       if (parser_options.limit is not None):
          queryset += '&limit=%s' % parser_options.limit
       else:
          queryset += '&limit=0'
       if (parser_options.offset is not None):
          queryset += '&offset=%s' % parser_options.offset
       else:
          queryset += '&offset=0' 
       info_json = request.get_experiments(queryset)
    print(json.dumps(json.loads(info_json), indent=4, sort_keys=True))


def main():
    """
    Main command-line execution loop."
    """
    try:
       parser = parse_options()
       parser_options = parser.parse_args()
       request = rest.Api(username=parser_options.username, password=parser_options.password, 
           parser=parser)
       subparser_name = parser_options.subparser_name
       if (subparser_name == 'submit'):
          submit_experiment(parser_options, request, parser)
       elif (subparser_name == 'stop'):
          stop_experiment(parser_options, request, parser)
       elif (subparser_name == 'get'):
          get_experiment(parser_options, request, parser)
       elif (subparser_name == 'load'):
          load_experiment(parser_options, request, parser)
       elif (subparser_name == 'info'):
          info_experiment(parser_options, request, parser)
    except KeyboardInterrupt:
        print >> sys.stderr, "\nStopped."
        sys.exit()

