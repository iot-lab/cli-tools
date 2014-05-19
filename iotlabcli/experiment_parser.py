# -*- coding:utf-8 -*-
"""Experiment parser"""

import argparse
import json
import sys
from cStringIO import StringIO
from argparse import RawTextHelpFormatter

from iotlabcli import rest, helpers, help_parser
from iotlabcli.experiment import Experiment
from iotlabcli import version

def parse_options():
    """
    Handle experiment-cli command-line options with argparse
    """
    parent_parser = argparse.ArgumentParser(add_help=False)
    # We create top level parser
    parser = argparse.ArgumentParser(
        description=help_parser.EXPERIMENT_PARSER,
        parents=[parent_parser],
        epilog=help_parser.PARSER_EPILOG %
        {'cli': 'experiment', 'option': 'submit'},
        formatter_class=RawTextHelpFormatter)

    parser.add_argument('-u', '--user', dest='username')
    parser.add_argument('-p', '--password', dest='password')
    parser.add_argument('-v', '--version', action='version', version=version)

    subparsers = parser.add_subparsers(dest='subparser_name')

    submit_parser = subparsers.add_parser(
        'submit',
        help='submit user experiment',
        epilog=help_parser.SUBMIT_EPILOG,
        formatter_class=RawTextHelpFormatter)

    submit_parser.add_argument(
        '-l', '--list',
        action='append', dest='exp_list', required=True,
        help="experiment list")

    submit_parser.add_argument(
        '-n', '--name', dest='name',
        help='experiment name')

    submit_parser.add_argument(
        '-d', '--duration',
        dest='duration', required=True, type=int,
        help='experiment duration in minutes')

    submit_parser.add_argument(
        '-r', '--reservation',
        dest='reservation', type=int,
        help='experiment schedule starting : seconds \
        since 1970-01-01 00:00:00 UTC')

    submit_parser.add_argument(
        '-p', '--print',
        dest='json', action='store_true',
        help='print experiment submission')

    ######## STOP PARSER ###############
    stop_parser = subparsers.add_parser(
        'stop',
        help='stop user experiment')

    stop_parser.add_argument(
        '-i', '--id',
        dest='experiment_id', type=int,
        help='experiment id submission')

    ######## GET PARSER ###############
    get_parser = subparsers.add_parser(
        'get',
        epilog=help_parser.GET_EPILOG,
        help='get user\'s experiment',
        formatter_class=RawTextHelpFormatter)

    get_parser.add_argument(
        '-i', '--id',
        dest='experiment_id', type=int,
        help='experiment id')

    get_parser.add_argument(
        '--offset',
        dest='offset', type=int,
        help='experiment list start index')

    get_parser.add_argument(
        '--limit',
        dest='limit', type=int,
        help='experiment list lenght')

    get_parser.add_argument(
        '--state', dest='state',
        help='experiment list state filter')

    get_group = get_parser.add_mutually_exclusive_group(required=True)

    get_group.add_argument(
        '-a', '--archive',
        action='store_true', dest='archive',
        help='get an experiment archive (tar.gz)')

    get_group.add_argument(
        '-p', '--print', action='store_true', dest='json',
        help='get an experiment submission')

    get_group.add_argument(
        '-s', '--exp-state',
        action='store_true', dest='exp_state',
        help='get an experiment state')

    get_group.add_argument(
        '-r', '--resources',
        action='store_true', dest='resources',
        help='get an experiment resources list')

    get_group.add_argument(
        '-l', '--list',
        action='store_true',
        dest='experiment_list',
        help='get user\'s experiment list')

    ######## LOAD PARSER ###############
    load_parser = subparsers.add_parser(
        'load',
        epilog=help_parser.LOAD_EPILOG,
        formatter_class=RawTextHelpFormatter,
        help='load and submit user experiment')

    load_parser.add_argument(
        '-f', '--file',
        dest='path_file', required=True,
        help='experiment path file')

    load_parser.add_argument(
        '-l', '--list',
        dest='firmware_list',
        help='firmware(s) path list')

    ######## INFO PARSER ###############
    info_parser = subparsers.add_parser(
        'info',
        epilog=help_parser.INFO_EPILOG,
        formatter_class=RawTextHelpFormatter,
        help='resource\'s description list')

    info_parser.add_argument(
        '--site',
        dest='site',
        help='resources list filter by site')

    info_group = info_parser.add_mutually_exclusive_group(required=True)

    info_group.add_argument(
        '-l', '--list',
        dest='resources_list',
        action='store_true',
        help='resources list')

    info_group.add_argument(
        '-li', '--list-id',
        dest='resources_id',
        action='store_true',
        help=('resources id list by archi and state '
              '(EXP_LIST submission format : 1-34+72)'))

    return parser


def submit_experiment(parser_options, request, parser):
    """ Submit user experiment with JSON Encoder serialization object
    Experiment and firmware(s). If submission is accepted by scheduler OAR
    we print JSONObject response with id submission.

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
    experiment = Experiment(
        name=parser_options.name,
        duration=parser_options.duration,
        reservation=parser_options.reservation)
    sites_json = json.loads(request.get_sites())
    for exp_list in parser_options.exp_list:
        experiment_type, param_list = \
            helpers.check_experiment_list(exp_list, parser)
        experiment.type = experiment_type
        if experiment_type == 'physical' and not alias_type:
            physical_type = True
            site = helpers.check_site(param_list[0], sites_json, parser)
            archi = helpers.check_archi(param_list[1], parser)
            nodes_list = param_list[2]
            nodes = helpers.check_nodes_list(site, archi, nodes_list, parser)
            experiment.set_physical_nodes(nodes)
        # experiment alias type
        elif experiment_type == 'alias' and not physical_type:
            alias_type = True
            alias_number += 1
            nb_nodes = param_list[0]
            properties_list = param_list[1]
            properties = helpers.check_properties(properties_list,
                                                  sites_json,
                                                  parser)
            experiment.set_alias_nodes(str(alias_number), int(nb_nodes),
                                       properties)
            nodes = ["%d" % alias_number]
        else:
            parser.error("Experiment list is not valid with \
                two different types : alias and physical")
        if experiment_type == "physical":
            index_list = 3
        else:
            # alias experiment type
            index_list = 2
        # firmware associations
        if len(param_list) > index_list and param_list[index_list] != "":
            firmware_path = param_list[index_list]
            firmware_name, firmware_body, firmwares = \
                helpers.check_experiment_firmwares(firmware_path,
                                                   firmwares,
                                                   parser)
            experiment_files[firmware_name] = firmware_body
            experiment.set_firmware_associations(firmware_name, nodes)
        # profile associations
        index_list += 2
        if len(param_list) == index_list and param_list[index_list-1] != "":
            profile_name = param_list[index_list-1]
            experiment.set_profile_associations(profile_name, nodes)
    experiment_json = json.dumps(experiment,
                                 cls=rest.Encoder,
                                 sort_keys=True, indent=4)
    if parser_options.json:
        print experiment_json
    else:
        experiment_filehandle = StringIO(experiment_json)
        # static name for experiment file : rename by server-rest
        experiment_files['new_exp.json'] = experiment_filehandle.read()
        experiment_filehandle.close()
        oar_json = request.submit_experiment(experiment_files)
        print json.dumps(json.loads(oar_json), indent=4, sort_keys=True)


def stop_experiment(parser_options, request, parser):
    """ Stop user experiment submission.

    :param experiment_id: scheduler OAR id submission
    :type experiment_id: string
    :param request: API Rest request object
    """
    if parser_options.experiment_id is not None:
        experiment_id = parser_options.experiment_id
    else:
        queryset = "state=Running&limit=0&offset=0"
        experiments_json = json.loads(request.get_experiments(queryset))
        experiment_id = \
            helpers.check_experiments_running(experiments_json, parser)
    request.stop_experiment(experiment_id)


def get_experiment(parser_options, request, parser):
    """ Get user experiment's description :
    _ download archive file (tar.gz) with JSONObject experiment
      description and firmware(s)
    _ print JSONObject with experiment state
    _ print JSONObject with experiment owner
    _ print JSONObject with experiment description

    :param parser_options: command-line parser options
    :type parser_options: Namespace object with options attribute
    :param request: API Rest request object
    :param parser: command-line parser
    """
    if parser_options.experiment_list:
        state = helpers.check_experiment_state(parser_options.state, parser)
        queryset = 'state='+state
        if parser_options.limit is not None:
            queryset += '&limit=%s' % parser_options.limit
        else:
            queryset += '&limit=0'
        if parser_options.offset is not None:
            queryset += '&offset=%s' % parser_options.offset
        else:
            queryset += '&offset=0'
        experiment_json = request.get_experiments(queryset)
        print json.dumps(json.loads(experiment_json), indent=4, sort_keys=True)
    else:
        if parser_options.experiment_id is not None:
            experiment_id = parser_options.experiment_id
        else:
            queryset = "state=Running&limit=0&offset=0"
            experiments_json = json.loads(request.get_experiments(queryset))
            experiment_id = \
                helpers.check_experiments_running(experiments_json, parser)
        if parser_options.archive:
            data = request.get_experiment_archive(experiment_id)
            helpers.write_experiment_archive(experiment_id, data, parser)
        else:
            if parser_options.json:
                experiment_json = request.get_experiment(experiment_id)
            elif parser_options.exp_state:
                experiment_json = request.get_experiment_state(experiment_id)
            elif parser_options.resources:
                experiment_json = \
                    request.get_experiment_resources(experiment_id)
            print json.dumps(json.loads(experiment_json), indent=4,
                             sort_keys=True)


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
    experiment_file_name, experiment_file_data = \
        helpers.open_file(parser_options.path_file, parser)
    experiment_json = helpers.read_json_file(
        experiment_file_name, experiment_file_data, parser)
    firmware_associations = experiment_json['firmwareassociations']
    # static name for experiment file : rename by server-rest with id_oar.json
    experiment_files['new_exp.json'] = experiment_file_data
    if firmware_list is not None and firmware_associations is None:
        parser.error("You don't have firmware(s) in your "
                     "experiment JSON description")
    elif firmware_list is not None:
        firmware = firmware_list.split(',')
        for firmware_path in firmware:
            firmware_name, firmware_body, firmwares = helpers. \
                check_experiment_firmwares(firmware_path, firmwares, parser)
            experiment_files[firmware_name] = firmware_body
    if firmware_associations is not None:
        for firmware in firmware_associations:
            firmware_name = firmware['firmwarename']
            if not firmware_name in experiment_files:
                firmware_name, firmware_body, firmwares = \
                    helpers.check_experiment_firmwares(firmware_name,
                                                       firmwares, parser)
                experiment_files[firmware_name] = firmware_body
        if not len(firmware_associations) == len(experiment_files)-1:
            parser.error("You have more firmware(s) in your firmware list \
                than in experiment JSON description")
    oar_json = request.submit_experiment(experiment_files)
    print json.dumps(json.loads(oar_json), indent=4, sort_keys=True)


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
    _ = parser
    if parser_options.resources_list:
        info_json = request.get_resources(parser_options.site)
    elif parser_options.resources_id:
        info_json = request.get_resources_id(parser_options.site)
    print json.dumps(json.loads(info_json), indent=4, sort_keys=True)


def main(args=sys.argv[1:]):
    """
    Main command-line execution loop."
    """
    try:
        parser = parse_options()
        parser_options = parser.parse_args(args)
        request = rest.Api(username=parser_options.username,
                           password=parser_options.password,
                           parser=parser)
        subparser_name = parser_options.subparser_name
        if subparser_name == 'submit':
            submit_experiment(parser_options, request, parser)
        elif subparser_name == 'stop':
            stop_experiment(parser_options, request, parser)
        elif subparser_name == 'get':
            get_experiment(parser_options, request, parser)
        elif subparser_name == 'load':
            load_experiment(parser_options, request, parser)
        elif subparser_name == 'info':
            info_experiment(parser_options, request, parser)
    except KeyboardInterrupt:
        print >> sys.stderr, "\nStopped."
        sys.exit()
