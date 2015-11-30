# -*- coding: utf-8 -*-

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

""" Experiment parser """
# pylint:disable=protected-access

import sys
import time

from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError

from iotlabcli import experiment
from iotlabcli import helpers
from iotlabcli import rest
from iotlabcli import auth
from iotlabcli.parser import common, help_msgs

EXPERIMENT_PARSER = """

experiment-cli command-line manages experiments on testbed.

"""


def parse_options():
    """ Handle experiment-cli command-line options with argparse """
    parent_parser = common.base_parser()

    # We create top level parser
    parser = ArgumentParser(
        description=EXPERIMENT_PARSER,
        parents=[parent_parser],
        epilog=help_msgs.PARSER_EPILOG.format(
            cli='experiment', option='submit'),
        formatter_class=RawTextHelpFormatter)

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True  # not required by default in Python3

    submit_parser = subparsers.add_parser(
        'submit', help='submit user experiment',
        epilog=help_msgs.SUBMIT_EPILOG, formatter_class=RawTextHelpFormatter)

    submit_parser.add_argument('-l', '--list', action='append',
                               dest='nodes_list', required=True,
                               type=exp_resources_from_str,
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
    common.add_expid_arg(stop_parser)

    # ####### GET PARSER ###############
    get_parser = subparsers.add_parser(
        'get',
        epilog=help_msgs.GET_EPILOG,
        help='get user\'s experiment',
        formatter_class=RawTextHelpFormatter)

    common.add_expid_arg(get_parser)

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
        '-st', '--start-time', dest='get_cmd', action='store_const',
        const='start', help='get expected experiment start time')
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
    load_parser = subparsers.add_parser('load', epilog=help_msgs.LOAD_EPILOG,
                                        help='load and submit user experiment',
                                        formatter_class=RawTextHelpFormatter)

    load_parser.add_argument('-f', '--file', dest='path_file',
                             required=True, help='experiment path file')

    load_parser.add_argument('-l', '--list', dest='firmware_list', default=[],
                             type=(lambda s: s.split(',')),
                             help='comma separated firmware(s) path list')

    # ####### INFO PARSER ###############
    info_parser = subparsers.add_parser('info', epilog=help_msgs.INFO_EPILOG,
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

    # ####### WAIT PARSER ###############
    wait_parser = subparsers.add_parser(
        'wait', help='wait user experiment started',
        epilog=help_msgs.WAIT_EPILOG, formatter_class=RawTextHelpFormatter)

    common.add_expid_arg(wait_parser)

    wait_parser.add_argument(
        '--state', default='Running',
        help="wait states `State1,State2` or Finished, default 'Running'")
    wait_parser.add_argument(
        '--step', default=5, type=int,
        help="Wait time in seconds between each check")
    wait_parser.add_argument(
        '--timeout', default=float('+inf'), type=float,
        help="Max time to wait in seconds")

    return parser


def exp_infos_from_str(exp_str):
    """Extract nodes and associations."""
    try:
        params = exp_str.split(',')
        nodes, params = _extract_firmware_nodes_list(params)
        associations = _extract_associations(params)
    except ValueError as err:
        raise ArgumentTypeError(
            'Invalid arguments in experiment list %r: %s' % (exp_str, err))

    return nodes, associations


def exp_resources_from_str(exp_str):
    """Extract an 'experiment.exp_resources' from parameter string.

    Accepted formats:
        + 9,archi=wsn430:cc1101+site=grenoble,tp.hex,battery,mobility=JHall

        + grenoble,m3,1-20,/home/cc1101.hex
        + rocquencourt,a8,1-5,,battery,firmware=a8.elf
    """
    nodes, associations = exp_infos_from_str(exp_str)
    firmware_path = associations.pop('firmware', None)
    profile_name = associations.pop('profile', None)
    return experiment.exp_resources(nodes, firmware_path, profile_name,
                                    **associations)


def _valid_param(param):
    """Check parameter are valid for _args_kwargs.

    * no space
    * a name before '='
    """
    if ' ' in param:
        raise ValueError('no space allowed')
    if param.startswith('='):
        raise ValueError("name required for kwarg '%s'" % param)


def _args_kwargs(params):
    """Separate args and kwargs from params.

    `args` must all be at first and `kwargs` at the end
    Space are forbidden as well as incomplete kwargs without name.

    >>> expected = (['a', 'b', 'c'], {'e': 'f', 'g': 'h'})
    >>> _args_kwargs(['a', 'b', 'c', 'e=f', 'g=h']) == expected
    True

    >>> _args_kwargs(['a', 'b', 'c']) ==  (['a', 'b', 'c'], {})
    True
    >>> _args_kwargs(['e=f', 'g=h']) == ([], {'e': 'f', 'g': 'h'})
    True

    # no value ignored
    >>> _args_kwargs(['e=']) == ([], {})
    True

    >>> _args_kwargs(['a==b']) == ([], {'a': '=b'})
    True

    # Space in value
    >>> _args_kwargs(['val ue'])
    Traceback (most recent call last):
    ValueError: no space allowed

    >>> _args_kwargs(['=f'])
    Traceback (most recent call last):
    ValueError: name required for kwarg '=f'

    # Order not respected
    >>> _args_kwargs(['e=f', 'a'])
    Traceback (most recent call last):
    ValueError: got argument after keyword argument
    >>> _args_kwargs(['a', 'e=f', 'b'])
    Traceback (most recent call last):
    ValueError: got argument after keyword argument

    :returns: (`args`, `kwargs`)
    """
    args, kwargs = [], {}

    parse_kwargs = False
    for param in params:
        _valid_param(param)

        if '=' in param:
            parse_kwargs = True  # kwargs after args

            # Parsing kwargs
            key, value = param.split('=', 1)
            if value:
                kwargs[key] = value
        elif parse_kwargs:
            # Should be kwargs but no '='
            raise ValueError('got argument after keyword argument')
        else:  # not parse_kwargs
            args.append(param)

    return args, kwargs


def _extract_associations(params):
    """Extract 'associations'.

    Firmware, profile at positional args then keyword arguments.
    """
    assocs = {}
    args, kwargs = _args_kwargs(params)

    # Get positional arguments 'firmware' and 'profile
    for key, value in zip(('firmware', 'profile'), args):
        if value:  # not None or empty
            assocs[key] = value
    if len(args) > 2:
        raise ValueError('Wrong number of arguments')

    # Get keyword arguments
    for key, value in kwargs.items():
        if key in assocs:
            raise ValueError("got multiple values for keyword argument "
                             "'%s'" % key)
        assocs[key] = value

    return assocs


def get_alias_properties(properties_str):
    """ Extract nodes selection properties from given properties_str

    >>> get_alias_properties("site=grenoble+archi=wsn430:cc1101+mobile=True")
    ('grenoble', 'wsn430:cc1101', 'True')

    >>> get_alias_properties("site=strasbourg+archi=m3:at86rf231")
    ('strasbourg', 'm3:at86rf231', None)

    >>> get_alias_properties("site=strasbourg")
    ... # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ArgumentTypeError: Properties "archi" and "site" are mandatory.

    >>> inval_prop = "site=strasbourg+archi=val+uknown=test"
    >>> get_alias_properties(inval_prop)
    ... # doctest: +IGNORE_EXCEPTION_DETAIL
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ArgumentTypeError: Invalid property in '...'
    Allowed values are ['archi', 'site', 'mobile']

    >>> get_alias_properties("site=")
    ... # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ArgumentTypeError: Invalid empty value for property 'site' in ['site=']
    """
    properties = properties_str.split('+')
    try:
        site = _get_property(properties, 'site')
        archi = _get_property(properties, 'archi')
        mobile = _get_property(properties, 'mobile')
    except ValueError as err:
        raise ArgumentTypeError(err)

    # check extracted values
    if archi is None or site is None:
        raise ArgumentTypeError('Properties "archi" and "site" are mandatory.')

    if len(properties) > (2 if mobile is None else 3):
        # Refuse unkown properties
        raise ArgumentTypeError(
            "Invalid property in %r\n" % properties_str +
            "Allowed values are ['archi', 'site', 'mobile']")

    return site, archi, mobile


def mobile_from_mobile_str(mobile_str=None):
    """Return the value to put in experiment json from mobile_str.

    >>> mobile_from_mobile_str(None)
    False

    >>> mobile_from_mobile_str('true')
    True
    >>> mobile_from_mobile_str('True')
    True

    >>> mobile_from_mobile_str('false')
    False

    >>> mobile_from_mobile_str('1')
    True
    >>> mobile_from_mobile_str('0')
    False

    >>> mobile_from_mobile_str('invalid_value')
    Traceback (most recent call last):
    ValueError: Invalid 'mobile' property: %r. Should be in 'true|false|0|1'
    """
    mobile_str = mobile_str or 'False'
    mobile_str = mobile_str.title()  # upper first letter

    if mobile_str == 'True':
        return True
    elif mobile_str == 'False':
        return False
    try:
        return bool(int(mobile_str))
    except ValueError:
        raise ValueError(
            "Invalid 'mobile' property: %r. Should be in 'true|false|0|1'")


def _extract_firmware_nodes_list(param_list):
    """
    Extract a firmware nodes list from param_list
    param_list is modified by the function call
    :param param_list: can have following formats
        * ['9', 'archi=wsn430:cc1101+site=grenoble', ...]  Alias type
        * ['grenoble', 'm3', '1-4+8-12+7', ...]  Physical type
    """

    # list in experiment-cli (alias or physical)
    if param_list[0].isdigit():  # alias selection
        # extract parameters
        nb_nodes, properties_str = param_list[0:2]
        param_list = param_list[2:]

        # parse parameters
        site, archi, _mobile = get_alias_properties(properties_str)
        mobile = mobile_from_mobile_str(_mobile)
        nodes = experiment.AliasNodes(int(nb_nodes), site, archi, mobile)
    else:  # physical selection
        # extract parameters
        site, archi, nodes_str = param_list[0:3]
        param_list = param_list[3:]

        # parse parameters
        nodes = common.nodes_list_from_info(site, archi, nodes_str)
    common.check_site_with_server(site)
    return nodes, param_list


def _get_property(properties, key):
    """
    >>> _get_property(['archi=val_1', 'site=grenoble', 'archi=val_2'], 'site')
    'grenoble'

    >>> _get_property(['archi=val_1'], 'site')  # None when absent

    # value should appear only once
    >>> _get_property(['archi=1', 'archi=2'], 'archi')
    ... # doctest: +IGNORE_EXCEPTION_DETAIL
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ValueError: Property 'archi' should appear only once in [...]

    # invalid format
    >>> _get_property(['archi='], 'archi')
    ... # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ValueError: Invalid empty value for property 'archi' in ['archi=']
    """
    matching = [prop.split('=').pop(1) for prop in properties
                if prop.startswith(key + '=')]
    if len(matching) > 1:
        raise ValueError('Property %r should appear only once in %r' %
                         (key, properties))
    if '' in matching:
        raise ValueError('Invalid empty value for property %r in %r' %
                         (key, properties))
    try:
        return matching.pop(0)
    except IndexError:
        return None


def submit_experiment_parser(opts):
    """ Parse namespace 'opts' and execute requested 'submit' command """
    user, passwd = auth.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)

    return experiment.submit_experiment(api, opts.name, opts.duration,
                                        opts.nodes_list, opts.reservation,
                                        opts.print_json)


def stop_experiment_parser(opts):
    """ Parse namespace 'opts' object and execute requested 'stop' command """
    user, passwd = auth.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)
    exp_id = helpers.get_current_experiment(api, opts.experiment_id)

    return experiment.stop_experiment(api, exp_id)


def get_experiment_parser(opts):
    """ Parse namespace 'opts' object and execute requested 'get' command """

    user, passwd = auth.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)

    if opts.get_cmd == 'experiment_list':
        return experiment.get_experiments_list(api, opts.state, opts.limit,
                                               opts.offset)
    elif opts.get_cmd == 'start':
        exp_id = helpers.get_current_experiment(api, opts.experiment_id,
                                                running_only=False)
        ret = experiment.get_experiment(api, exp_id, opts.get_cmd)

        # Add a 'date' field
        timestamp = ret['start_time']
        ret['local_date'] = time.ctime(timestamp) if timestamp else 'Unknown'
        return ret
    else:
        exp_id = helpers.get_current_experiment(api, opts.experiment_id)
        return experiment.get_experiment(api, exp_id, opts.get_cmd)


def load_experiment_parser(opts):
    """ Parse namespace 'opts' object and execute requested 'load' command """

    user, passwd = auth.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)
    return experiment.load_experiment(api, opts.path_file, opts.firmware_list)


def info_experiment_parser(opts):
    """ Parse namespace 'opts' object and execute requested 'info' command """
    user, passwd = auth.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)
    return experiment.info_experiment(api, opts.list_id, opts.site)


def wait_experiment_parser(opts):
    """ Parse namespace 'opts' object and execute requested 'wait' command """

    user, passwd = auth.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)

    exp_id = helpers.get_current_experiment(
        api, opts.experiment_id, running_only=False)

    sys.stderr.write("Waiting that experiment {0} gets in state {1}\n".format(
        exp_id, opts.state))

    return experiment.wait_experiment(api, exp_id, opts.state,
                                      opts.step, opts.timeout)


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
        'wait': wait_experiment_parser,
    }[opts.command]

    return command(opts)


def main(args=None):
    """ Main command-line execution loop." """
    args = args or sys.argv[1:]
    parser = parse_options()
    common.main_cli(experiment_parse_and_run, parser, args)
