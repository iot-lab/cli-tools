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

import sys
import time
from datetime import datetime

import argparse
from argparse import ArgumentParser, RawTextHelpFormatter

from iotlabcli import experiment
from iotlabcli import helpers
from iotlabcli import rest
from iotlabcli import auth
from iotlabcli.parser import common, help_msgs

EXPERIMENT_PARSER = """

iotlab-experiment command-line manages experiments on testbed.

"""


def parse_options():
    """ Handle iotlab-experiment command-line options with argparse """
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

    # ####### SUBMIT PARSER ###############
    parser_add_submit_subparser(subparsers)

    # ####### SCRIPT PARSER ###############
    parser_add_script_subparser(subparsers)

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
        '-d', '--deployment', dest='get_cmd', action='store_const',
        const='deployment', help='get an experiment deployment')

    get_group.add_argument(
        '-n', '--nodes', dest='get_cmd', action='store_const',
        const='nodes', help='get an experiment nodes list')
    get_group.add_argument(
        '-ni', '--nodes-id', dest='get_cmd', action='store_const',
        const='nodes_ids', help=('get an experiment nodes id list '
                                 '(EXP_LIST format : 1-34+72)'))
    get_group.add_argument(
        '-p', '--print', dest='get_cmd', action='store_const',
        const='', help='get an experiment description')
    get_group.add_argument(
        '-a', '--archive', dest='get_cmd', action='store_const',
        const='data', help='get an experiment archive (tar.gz)')

    # --list with its options
    get_group.add_argument(
        '-l', '--list', dest='get_cmd', action='store_const',
        const='experiment_list', help='get user\'s experiment list')
    get_group.add_argument(
        '-r', '--resources', dest='get_cmd', action='store_const',
        const='resources', help='DEPRECATED: use -n or --nodes option')
    get_group.add_argument(
        '-ri', '--resources-id', dest='get_cmd', action='store_const',
        const='resources_ids',
        help=('DEPRECATED: use -ni or --nodes-id option'))
    get_group.add_argument(
        '-s', '--exp-state', dest='get_cmd', action='store_const',
        const='state', help='DEPRECATED: use -p or --print option')
    get_group.add_argument(
        '-st', '--start-time', dest='get_cmd', action='store_const',
        const='start_date',
        help='DEPRECATED: use -p or --print option')
    get_parser.add_argument('--offset', default=0, type=int,
                            help='experiment list start index')

    get_parser.add_argument('--limit', default=0, type=int,
                            help='experiment list maximum length')

    get_parser.add_argument('--state', help='experiment list state filter')

    get_group.add_argument('-e', '--experiments', dest='get_cmd',
                           action='store_const',
                           const='experiments',
                           help='get running experiments ids')
    get_parser.add_argument(
        '--active', action='store_true', default=False,
        help='experiments: include waiting/starting experiments')

    # ####### LOAD PARSER ###############
    load_parser = subparsers.add_parser('load', epilog=help_msgs.LOAD_EPILOG,
                                        help='load and submit user experiment',
                                        formatter_class=RawTextHelpFormatter)

    load_parser.add_argument('-f', '--file', dest='path_file',
                             metavar='EXP_JSON', required=True,
                             help='experiment path file')

    _load_list_help = ('file path for firmware/script/... if not in'
                       ' current directory.')

    load_parser.add_argument('-l', '--list', metavar='FILEPATH',
                             dest='files', default=[],
                             type=(lambda s: s.split(',')), action='append',
                             help=_load_list_help)

    # ####### RELOAD PARSER ###############
    reload_parser = subparsers.add_parser('reload',
                                          epilog=help_msgs.RELOAD_EPILOG,
                                          help='reload user experiment',
                                          formatter_class=RawTextHelpFormatter)
    common.add_expid_arg(reload_parser, required=True)

    _parser_add_duration_and_reservation(reload_parser,
                                         duration_required=False)

    # ####### INFO PARSER ###############
    class DeprecateHelpFormatter(argparse.HelpFormatter):
        """ Add drepecate help formatter """
        def add_usage(self, usage, actions, groups, prefix=None):
            helpers.deprecate_warn_cmd('info', 'iotlab-status', 19)
            return super(DeprecateHelpFormatter, self).add_usage(usage,
                                                                 actions,
                                                                 groups,
                                                                 prefix)

    help_msg = 'DEPRECATED: use iotlab-status command instead'
    info_parser = subparsers.add_parser('info', help=help_msg,
                                        formatter_class=DeprecateHelpFormatter)

    info_parser.add_argument('--site',
                             action='append', dest='info_selection',
                             type=lambda x: ('site', x),
                             help='nodes list filter by site')
    info_parser.add_argument('--archi',
                             action='append', dest='info_selection',
                             type=lambda x: ('archi', x),
                             help='nodes list filter by architecture')
    info_parser.add_argument('--state', action='append', dest='info_selection',
                             type=lambda x: ('state', x),
                             help='nodes list filter by state')

    # subcommand
    info_group = info_parser.add_mutually_exclusive_group(required=True)
    info_group.add_argument('-l', '--list', dest='list_id',
                            action='store_false', help='nodes list')
    info_group.add_argument('-li', '--list-id', dest='list_id',
                            action='store_true',
                            help=('nodes id list by archi and state '
                                  '(EXP_LIST format : 1-34+72)'))

    # ####### WAIT PARSER ###############
    parser_add_wait_subparser(subparsers, expid_required=False)

    return parser


def parser_add_submit_subparser(subparsers):
    """Add 'submit' subparser and return it."""
    submit_parser = subparsers.add_parser(
        'submit', help='submit user experiment',
        epilog=help_msgs.SUBMIT_EPILOG, formatter_class=RawTextHelpFormatter)

    submit_parser.add_argument('-p', '--print',
                               dest='print_json', action='store_true',
                               help='print experiment submission')

    # General experiment configuration
    conf_parser = submit_parser.add_argument_group('experiment configuration')

    conf_parser.add_argument('-n', '--name', help='experiment name')
    _parser_add_duration_and_reservation(conf_parser, duration_required=True)

    # Resources
    res_parser = submit_parser.add_argument_group('resource configuration')
    res_parser.add_argument('-l', '--list', action='append',
                            dest='nodes_list', required=True,
                            type=exp_resources_from_str,
                            help="experiment list")
    res_parser.add_argument('-s', '--site-association', action='append',
                            type=site_association_from_str,
                            help='sites associations')

    # Help messages for resources
    help_parser = submit_parser.add_argument_group('advanced help options')
    common.HelpAction.add_help(help_parser, '--help-list',
                               'show help on --list option',
                               help_msgs.SUBMIT_LIST_HELP)
    common.HelpAction.add_help(help_parser, '--help-site-association',
                               'show help on --site-association option',
                               help_msgs.SUBMIT_SITE_ASSOC_HELP)


def _parser_add_duration_and_reservation(  # pylint:disable=invalid-name
        subparser, duration_required):
    """Add a 'duration' and a 'reservation' argument to subparser.

    :param subparser: subparser instance
    :param duration_required: select if duration is required or optional
    """
    subparser.add_argument('-d', '--duration', required=duration_required,
                           type=int, help='experiment duration in minutes')

    subparser.add_argument('-r', '--reservation', type=int,
                           help=('experiment schedule starting : seconds '
                                 'since 1970-01-01 00:00:00 UTC'))


def parser_add_wait_subparser(subparsers, expid_required=False):
    """Add wait experiment subparser and return it."""
    wait_parser = subparsers.add_parser(
        'wait', help='wait user experiment started',
        epilog=help_msgs.WAIT_EPILOG, formatter_class=RawTextHelpFormatter)

    common.add_expid_arg(wait_parser, required=expid_required)

    wait_parser.add_argument(
        '--state', default='Running',
        help="wait states `State1,State2` or Finished, default 'Running'")
    wait_parser.add_argument(
        '--step', default=5, type=int,
        help="Wait time in seconds between each check")
    wait_parser.add_argument(
        '--timeout', default=experiment.WAIT_TIMEOUT_DEFAULT, type=float,
        help="Max time to wait in seconds")
    wait_parser.add_argument(
        '--cancel-on-timeout', action='store_true',
        help="Cancel experiment if timeout is reached")

    return wait_parser


def parser_add_script_subparser(subparsers):
    """Add suparser for 'script'."""
    _script_parser = subparsers.add_parser(
        'script', help='run script on sites frontends',
        epilog=help_msgs.SCRIPT_EPILOG, formatter_class=RawTextHelpFormatter)
    common.add_expid_arg(_script_parser)

    script_group = _script_parser.add_argument_group("Command")
    script_group = script_group.add_mutually_exclusive_group(required=True)

    script_group.add_argument('--run', type=run_site_association_from_str,
                              metavar=RUN_SITE_ASSOCIATION_METAVAR,
                              dest='run_script_site', nargs='+',
                              help="sites association with 'script'")
    script_group.add_argument('--kill', type=common.site_with_domain_checked,
                              metavar='site', dest='kill_sites',
                              nargs='*', help='sites list')
    script_group.add_argument('--status', type=common.site_with_domain_checked,
                              metavar='site', dest='status_sites',
                              nargs='*', help='sites list')
    return _script_parser


def exp_infos_from_str(exp_str):
    """Extract nodes and associations."""
    try:
        params = exp_str.split(',')
        nodes, params = _extract_firmware_nodes_list(params)
        associations = _extract_associations(params)
    except ValueError as err:
        raise argparse.ArgumentTypeError(
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


def site_association_from_str(site_assoc_str):
    """Extract site_association from given string.

    Format is:

        site,name=value
        site1,site2,site3,assoc_name=assoc_value,assoc2=assoc_val2

    Sites validity is checked

    :raises argparse.ArgumentTypeError: on invalid site_assoc_str
    """
    # Decode keywoard associations
    try:
        sites, kwassocs = _args_kwargs(site_assoc_str.split(','))

        # Validate site and add domain
        sites = [common.site_with_domain_checked(site) for site in sites]
        return experiment.site_association(*sites, **kwassocs)
    except ValueError as err:
        raise argparse.ArgumentTypeError('Invalid site_association: %s' % err)


RUN_SITE_ASSOCIATIONS_STR = ('script=script_path'
                             '[,scriptconfig=scriptconfig_path]')
RUN_SITE_ASSOCIATION_METAVAR = 'site,site,%s' % (RUN_SITE_ASSOCIATIONS_STR,)


def _run_associations_arg_check(script, scriptconfig=None):
    # pylint:disable=unused-argument,unnecessary-pass
    """To be used with **associations to check given arguments."""
    pass


def run_site_association_from_str(site_assoc_str):
    """Extract site_association and verify given associations.

    'script' association is mandatory.
    No other associations allowed.
    """
    site_association = site_association_from_str(site_assoc_str)

    associations = site_association.associations
    try:
        _run_associations_arg_check(**associations)
    except TypeError:
        raise argparse.ArgumentTypeError(
            'Invalid associations in %s should match %s' %
            (site_assoc_str, RUN_SITE_ASSOCIATIONS_STR))

    return site_association


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

    >>> _args_kwargs(['e=f', 'e=i'])
    Traceback (most recent call last):
    ValueError: keyword argument "e" specified multiple times

    :returns: (`args`, `kwargs`)
    """
    args, kwargs = [], {}

    _check_args_then_kwargs(params)

    for param in params:
        _valid_param(param)
        if '=' in param:
            # Parsing kwargs
            key, value = param.split('=', 1)
            _add_key_value(kwargs, key, value)
        else:
            # Parsing args
            args.append(param)

    return args, kwargs


def _check_args_then_kwargs(params):
    """Check that args are first, and then kwargs only."""
    is_kwargs = ['=' in param for param in params]
    # Should be many False then many True
    if is_kwargs != sorted(is_kwargs):
        raise ValueError('got argument after keyword argument')


def _add_key_value(kwargs, key, value=''):
    """Add `key`,`value` if value is not empty.

    Raise an error if key exists.
    """
    error = 'keyword argument "%s" specified multiple times'
    if key in kwargs:
        raise ValueError(error % key)
    if value:
        kwargs[key] = value


def _submit_args_to_dict(firmware='', profile=''):
    """Return kwargs for this arguments. Remove empty values"""
    kwargs = {}
    if firmware:
        kwargs['firmware'] = firmware
    if profile:
        kwargs['profile'] = profile
    return kwargs


def _merge_assocs_args_d_kwargs(args_dict, kwargs):
    """Merge args_dict and kwargs. Detect duplicate keys."""

    error_str = 'Association "%s" provided by argument and keyword argument'
    for key in args_dict:
        if key in kwargs:
            raise ValueError(error_str % key)

    merged = {}
    merged.update(args_dict)
    merged.update(kwargs)
    return merged


SUBMIT_ASSOC_ARGS_KWARGS = '[firmware][,profile][,assoc=value][,assoc=...]'


def _extract_associations(params):
    """Extract 'associations'.

    Firmware, profile at positional args then keyword arguments.
    :raises ValueError: on invalid input.
    """
    args, kwargs = _args_kwargs(params)
    try:
        args_dict = _submit_args_to_dict(*args)
    except TypeError:
        raise ValueError('Invalid positional arguments, should be %s' %
                         SUBMIT_ASSOC_ARGS_KWARGS)
    associations = _merge_assocs_args_d_kwargs(args_dict, kwargs)

    return associations


def get_alias_properties(properties_str):
    """ Extract nodes selection properties from given properties_str

    >>> get_alias_properties("site=grenoble+archi=wsn430:cc1101+mobile=True")
    ('grenoble', 'wsn430:cc1101', 'True')

    >>> get_alias_properties("site=strasbourg+archi=m3:at86rf231")
    ('strasbourg', 'm3:at86rf231', None)

    >>> get_alias_properties("site=strasbourg")
    Traceback (most recent call last):
    ValueError: Properties should be "archi", "site" and optional "mobile".

    >>> inval_prop = "site=strasbourg+archi=val+uknown=test"
    >>> get_alias_properties(inval_prop)
    Traceback (most recent call last):
    ValueError: Properties should be "archi", "site" and optional "mobile".
    """
    properties_dict = _properties_str_to_dict(properties_str)

    try:
        properties = _alias_properties_from_kwargs(**properties_dict)
    except TypeError:
        raise ValueError('Properties should be "archi", "site"'
                         ' and optional "mobile".')

    # Forward check if there are more properties
    site, archi, mobile = properties

    return site, archi, mobile


def _alias_properties_from_kwargs(site, archi, mobile=None):
    """To be used with **properties, checks given keys.

    Returns values.
    """
    return site, archi, mobile


def _properties_str_to_dict(properties_str):
    """Extract a properties string to a dict:

    >>> _properties_str_to_dict('a=1+b=3') == {'a': '1', 'b': '3'}
    True

    >>> _properties_str_to_dict('a=1+a=2')
    Traceback (most recent call last):
    ValueError: Property "a" should appear only once

    >>> _properties_str_to_dict('a=+b=2')
    Traceback (most recent call last):
    ValueError: Invalid empty value for property "a"
    """
    properties = [p.split('=', 1) for p in properties_str.split('+')]

    prop_dict = {}

    for key, value in properties:
        if key in prop_dict:
            raise ValueError('Property "%s" should appear only once' % key)
        if value == '':
            raise ValueError('Invalid empty value for property "%s"' % key)
        prop_dict[key] = value

    return prop_dict


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

    for convert_fct in (_mobile_str_true_false, _mobile_str_as_bool):
        try:
            return convert_fct(mobile_str)
        except (KeyError, ValueError):
            pass

    raise ValueError("Invalid 'mobile' property: %r."
                     " Should be in 'true|false|0|1'")


def _mobile_str_true_false(mobile_str):
    """Try checking for 'true', 'false' in any case."""
    mobile_str = mobile_str.title()  # upper first letter
    return {'True': True, 'False': False}[mobile_str]


def _mobile_str_as_bool(mobile_str):
    """Try converting to an int-bool."""
    return bool(int(mobile_str))


def _extract_firmware_nodes_list(param_list):
    """
    Extract a firmware nodes list from param_list
    param_list is modified by the function call
    :param param_list: can have following formats
        * ['9', 'archi=wsn430:cc1101+site=grenoble', ...]  Alias type
        * ['grenoble', 'm3', '1-4+8-12+7', ...]  Physical type
    """

    # list in iotlab-experiment (alias or physical)
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


def submit_experiment_parser(opts):
    """ Parse namespace 'opts' and execute requested 'submit' command """
    user, passwd = auth.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)

    return experiment.submit_experiment(api, opts.name, opts.duration,
                                        opts.nodes_list, opts.reservation,
                                        opts.print_json,
                                        opts.site_association)


def script_parser(opts):
    """Parse namespace 'opts' and execute requestes 'run' command."""
    user, passwd = auth.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)
    exp_id = helpers.get_current_experiment(api, opts.experiment_id)

    command, options = _script_command_options(opts)

    return experiment.script_experiment(api, exp_id, command, *options)


def _script_command_options(opts):
    """Extract `command` and `options` from argparse 'opts'."""
    if opts.run_script_site is not None:
        command = 'run'
        options = opts.run_script_site
    elif opts.kill_sites is not None:
        command = 'kill'
        options = opts.kill_sites
    elif opts.status_sites is not None:
        command = 'status'
        options = opts.status_sites
    else:  # pragma: no cover
        raise ValueError('Unknown request')

    return command, options


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
    # pylint:disable=no-else-return
    if opts.get_cmd == 'experiment_list':
        return experiment.get_experiments_list(api, opts.state, opts.limit,
                                               opts.offset)
    elif opts.get_cmd == 'start_date' or opts.get_cmd == 'state':
        return _get_experiment_attr(api, opts)
    elif opts.get_cmd == 'experiments':
        return experiment.get_active_experiments(api,
                                                 running_only=not opts.active)
    else:
        exp_id = helpers.get_current_experiment(api, opts.experiment_id)

        return experiment.get_experiment(api, exp_id,
                                         _deprecate_cmd(opts.get_cmd))


def _deprecate_cmd(cmd):
    if cmd == 'resources':
        new_cmd = 'nodes'
        helpers.deprecate_warn_cmd(cmd, new_cmd, 8)
        return new_cmd
    if cmd == 'resources_ids':
        helpers.deprecate_warn_cmd('resources-id', 'nodes-ids', 8)
        return 'nodes_ids'
    return cmd


def _get_experiment_attr(api, opts):
    """ Return start_time or state experiment attribute with old api format"""
    assert opts.get_cmd in ('state', 'start_date',)
    exp_id = helpers.get_current_experiment(api, opts.experiment_id,
                                            running_only=False)
    ret = experiment.get_experiment(api, exp_id, '')
    if opts.get_cmd == 'state':
        helpers.deprecate_warn_cmd('exp-state', 'print', 8)
        return {opts.get_cmd: ret[opts.get_cmd]}
    helpers.deprecate_warn_cmd('start-time', 'print', 8)
    # start_date option
    utc_date = datetime.strptime(ret[opts.get_cmd],
                                 '%Y-%m-%dT%H:%M:%SZ')
    timestamp = (utc_date - datetime(1970, 1, 1)).total_seconds()
    local_date = time.ctime(timestamp) if timestamp else 'Unknown'
    return {'start_time': int(timestamp),
            'local_date': local_date}


def load_experiment_parser(opts):
    """ Parse namespace 'opts' object and execute requested 'load' command """

    user, passwd = auth.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)
    files = helpers.flatten_list_list(opts.files)
    return experiment.load_experiment(api, opts.path_file, files)


def reload_experiment_parser(opts):
    """Parse namespace 'opts' object and execute requested 'reload' command."""
    user, passwd = auth.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)
    return experiment.reload_experiment(api, opts.experiment_id,
                                        opts.duration, opts.reservation)


def info_experiment_parser(opts):
    """ Parse namespace 'opts' object and execute requested 'info' command """
    user, passwd = auth.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)

    helpers.deprecate_warn_cmd('info', 'iotlab-status', 7)
    selection = dict(opts.info_selection or ())
    return experiment.info_experiment(api, opts.list_id, **selection)


def wait_experiment_parser(opts):
    """ Parse namespace 'opts' object and execute requested 'wait' command """

    user, passwd = auth.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)

    exp_id = helpers.get_current_experiment(
        api, opts.experiment_id, running_only=False)

    sys.stderr.write("Waiting that experiment {} gets in state {}\n".format(
        exp_id, opts.state))

    return experiment.wait_experiment(api, exp_id, opts.state,
                                      opts.step, opts.timeout,
                                      opts.cancel_on_timeout)


def experiment_parse_and_run(opts):
    """ Parse namespace 'opts' object and execute requested command
    Return result object
    """
    command = {
        'submit': submit_experiment_parser,
        'script': script_parser,
        'stop': stop_experiment_parser,
        'get': get_experiment_parser,
        'load': load_experiment_parser,
        'reload': reload_experiment_parser,
        'info': info_experiment_parser,
        'wait': wait_experiment_parser,
    }[opts.command]

    return command(opts)


def main(args=None):
    """Main command-line execution loop."""
    args = args or sys.argv[1:]
    parser = parse_options()
    common.main_cli(experiment_parse_and_run, parser, args)
