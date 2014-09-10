# -*- coding:utf-8 -*-
"""Experiment parser"""

import argparse
import json
import sys
from argparse import RawTextHelpFormatter

from iotlabcli import Error
from iotlabcli import rest, helpers, help_parser
from iotlabcli.experiment import Experiment
from iotlabcli import parser_common

# static name for experiment file : rename by server-rest
EXP_FILENAME = 'new_exp.json'


def parse_options():
    """ Handle experiment-cli command-line options with argparse """
    parent_parser = parser_common.base_parser()

    # We create top level parser
    parser = argparse.ArgumentParser(
        description=help_parser.EXPERIMENT_PARSER,
        parents=[parent_parser],
        epilog=help_parser.PARSER_EPILOG %
        {'cli': 'experiment', 'option': 'submit'},
        formatter_class=RawTextHelpFormatter)

    subparsers = parser.add_subparsers(dest='command')

    submit_parser = subparsers.add_parser(
        'submit', help='submit user experiment',
        epilog=help_parser.SUBMIT_EPILOG, formatter_class=RawTextHelpFormatter)

    submit_parser.add_argument('-l', '--list', action='append',
                               dest='nodes_list', required=True,
                               type=helpers.experiment_dict_from_str,
                               help="experiment list")

    submit_parser.add_argument('-n', '--name', help='experiment name')

    submit_parser.add_argument('-d', '--duration', required=True, type=int,
                               help='experiment duration in minutes')

    submit_parser.add_argument('-r', '--reservation', type=int,
                               help=('experiment schedule starting : seconds '
                                     'since 1970-01-01 00:00:00 UTC'))

    submit_parser.add_argument('-p', '--print',
                               dest='print_json', action='store_true',
                               help='print experiment submission')

    # ####### STOP PARSER ###############
    stop_parser = subparsers.add_parser('stop', help='stop user experiment')
    stop_parser.add_argument('-i', '--id', dest='experiment_id', type=int,
                             help='experiment id submission')

    # ####### GET PARSER ###############
    get_parser = subparsers.add_parser(
        'get',
        epilog=help_parser.GET_EPILOG,
        help='get user\'s experiment',
        formatter_class=RawTextHelpFormatter)

    get_parser.add_argument('-i', '--id', dest='experiment_id', type=int,
                            help='experiment id')

    get_group = get_parser.add_mutually_exclusive_group(required=True)
    get_group.add_argument(
        '-r', '--resources', dest='get_cmd', action='store_const',
        const='resources', help='get an experiment resources list')
    get_group.add_argument(
        '-ri', '--resources-id', dest='get_cmd', action='store_const',
        const='id', help=('get an experiment resources id list '
                          '(EXP_LIST format : 1-34+72)'))

    get_group.add_argument(
        '-s', '--exp-state', dest='get_cmd', action='store_const',
        const='state', help='get an experiment state')
    get_group.add_argument(
        '-p', '--print', dest='get_cmd', action='store_const',
        const='', help='get an experiment submission')
    get_group.add_argument(
        '-a', '--archive', dest='get_cmd', action='store_const',
        const='data', help='get an experiment archive (tar.gz)')

    # --list with its options
    get_group.add_argument(
        '-l', '--list', dest='get_cmd', action='store_const',
        const='experiment_list', help='get user\'s experiment list')

    get_parser.add_argument('--offset', default=0, type=int,
                            help='experiment list start index')

    get_parser.add_argument('--limit', default=0, type=int,
                            help='experiment list lenght')

    get_parser.add_argument('--state', help='experiment list state filter')

    # ####### LOAD PARSER ###############
    load_parser = subparsers.add_parser('load', epilog=help_parser.LOAD_EPILOG,
                                        help='load and submit user experiment',
                                        formatter_class=RawTextHelpFormatter)

    load_parser.add_argument('-f', '--file', dest='path_file',
                             required=True, help='experiment path file')

    load_parser.add_argument('-l', '--list', dest='firmware_list', default=[],
                             type=helpers.firmwares_from_string,
                             help='firmware(s) path list')

    # ####### INFO PARSER ###############
    info_parser = subparsers.add_parser('info', epilog=help_parser.INFO_EPILOG,
                                        help='resources description list',
                                        formatter_class=RawTextHelpFormatter)

    info_parser.add_argument('--site', help='resources list filter by site')
    # subcommand
    info_group = info_parser.add_mutually_exclusive_group(required=True)
    info_group.add_argument('-l', '--list', dest='list_id',
                            action='store_false', help='list resources')
    info_group.add_argument('-li', '--list-id', dest='list_id',
                            action='store_true',
                            help=('resources id list by archi and state '
                                  '(EXP_LIST format : 1-34+72)'))
    return parser


def submit_experiment_parser(opts):
    """ Parse namespace 'opts' and execute requested 'submit' command """
    user, passwd = helpers.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)

    experiment = Experiment(opts.name, opts.duration, opts.reservation)
    return submit_experiment(api, experiment, opts.nodes_list, opts.print_json)


def submit_experiment(api, experiment, nodes_list, print_json=False):
    """ Submit user experiment with JSON Encoder serialization object
    Experiment and firmware(s). If submission is accepted by scheduler OAR
    we print JSONObject response with id submission.

    :param api: API Rest api object
    :param experiment: experiment.Experiment object
    :param nodes_list: list of 'nodes' where 'nodes' is either
        experiment.AliasNodes or a list of nodes network addresses like:
        ['m3-1.grenoble.iot-lab.info', 'wsn430-1.strasbourg.iot-lab.info']
    :param print_json: select if experiment should be printed as json instead
        of submitted
    """
    assert nodes_list, 'nodes_list should not be empty'
    exp_files = {}

    for exp_dict in nodes_list:
        experiment.add_experiment_dict(exp_dict)

        # Add firmware to experiment files too
        firmware = exp_dict.get('firmware', None)
        if firmware is None:
            continue
        helpers.add_to_dict_uniq(exp_files, firmware['name'], firmware['body'])

    if print_json:  # output experiment description
        return experiment
    else:  # submit experiment
        # Add experiment description to files
        helpers.add_to_dict_uniq(exp_files, EXP_FILENAME, json.dumps(
            experiment, cls=rest.Encoder, sort_keys=True, indent=4))

        # Actually submit experiment
        return api.submit_experiment(exp_files)


def stop_experiment_parser(opts):
    """ Parse namespace 'opts' object and execute requested 'stop' command """
    user, passwd = helpers.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)
    exp_id = helpers.get_current_experiment(api, opts.experiment_id)

    return stop_experiment(api, exp_id)


def stop_experiment(api, exp_id):
    """ Stop user experiment submission.

    :param api: API Rest api object
    :param exp_id: scheduler OAR id submission
    """
    return api.stop_experiment(exp_id)


def get_experiment_parser(opts):
    """ Parse namespace 'opts' object and execute requested 'get' command """

    user, passwd = helpers.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)

    if opts.get_cmd == 'experiment_list':
        return get_experiments_list(api, opts.state, opts.limit, opts.offset)
    else:
        exp_id = helpers.get_current_experiment(api, opts.experiment_id)
        return get_experiment(api, exp_id, opts.get_cmd)


def get_experiments_list(api, state, limit, offset):
    """ Get the experiment list with the specific restriction:
    :param state: State of the experiment
    :param limit: maximum number of outputs
    :param offset: offset of experiments to start at
    """
    state = helpers.check_experiment_state(state)
    return api.get_experiments(state, limit, offset)


def get_experiment(api, exp_id, command=''):
    """ Get user experiment's description :

    :param api: API Rest api object
    :param exp_id: experiment id
    :param option: Restrict to some values
            * '':          experiment submission
            * 'resources': resources list
            * 'id':        resources id list: (1-34+72 format)
            * 'state':     experiment state
            * 'data':      experiment tar.gz with description and firmwares
    """
    result = api.get_experiment_info(exp_id, command)
    if command == 'data':
        helpers.write_experiment_archive(exp_id, result)
        result = 'Written'

    return result


def load_experiment_parser(opts):
    """ Parse namespace 'opts' object and execute requested 'load' command """

    user, passwd = helpers.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)
    return load_experiment(api, opts.path_file, opts.firmware_list)


def load_experiment(api, exp_description_path, firmware_list=()):
    """ Load and submit user experiment description with firmware(s)

    :param api: API Rest api object
    :param exp_description_path: path to experiment json description file
    :param firmware_list: list of firmware dict {'name': name, 'body': body}
    """
    exp_files = {}

    try:
        # Open json file
        _, exp_description_str = helpers.open_file(exp_description_path)
        exp_dict = json.loads(exp_description_str)
    except ValueError as err:
        raise Error('%r: %s' % (exp_description_path, err))

    firmware_associations = exp_dict['firmwareassociations'] or []

    #
    # Add firmwares to experiment_files dictionary
    #

    # Add firmwares from manual list, may be empty
    for firmware in firmware_list:
        helpers.add_to_dict_uniq(exp_files, firmware['name'], firmware['body'])

    # Add remaining firmware from current directory
    for fw_name in [fw['firmwarename'] for fw in firmware_associations]:
        if fw_name in exp_files:
            continue
        # was not already provided by manual list
        firmware = helpers.open_firmware(fw_name)
        helpers.add_to_dict_uniq(exp_files, firmware['name'], firmware['body'])

    #
    # Sanity Check, no more firmware than required
    #
    if len(firmware_associations) != len(exp_files):
        raise Error("Too many firmwares provided")

    # Add experiment description
    helpers.add_to_dict_uniq(exp_files, EXP_FILENAME, exp_description_str)
    return api.submit_experiment(exp_files)


def info_experiment_parser(opts):
    """ Parse namespace 'opts' object and execute requested 'info' command """

    user, passwd = helpers.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)
    return info_experiment(api, opts.list_id, opts.site)


def info_experiment(api, list_id=False, site=None):
    """ Print testbed information for user experiment submission:
    * resources description
    * resources description in short mode

    :param api: API Rest api object
    :param list_id: By default, return full nodes list, if list_id
        return output in exp_list format '3-12+42'
    :param site: Restrict informations collection on site
    """
    return api.get_resources(list_id, site)


def experiment_parse_and_run(opts):
    """ Parse namespace 'opts' object and execute requested command
    Return result object
    """
    command = {
        'submit': submit_experiment_parser,
        'stop': stop_experiment_parser,
        'get': get_experiment_parser,
        'load': load_experiment_parser,
        'info': info_experiment_parser,
    }[opts.command]

    return command(opts)


def main(args=sys.argv[1:]):
    """ Main command-line execution loop." """
    parser = parse_options()
    parser_common.main_cli(experiment_parse_and_run, parser, args)
