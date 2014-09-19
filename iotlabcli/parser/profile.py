# -*- coding:utf-8 -*-
""" Profile parser"""

import json
import sys
import argparse
from argparse import RawTextHelpFormatter

from iotlabcli import helpers
from iotlabcli import rest
from iotlabcli import auth
from iotlabcli.parser import help_msgs
from iotlabcli.parser import common
from iotlabcli.profile import ProfileWSN430, ProfileM3


def parse_options():
    """ Handle profile-cli command-line opts with argparse """
    parent_parser = common.base_parser()
    # We create top level parser
    parser = argparse.ArgumentParser(
        description=help_msgs.PROFILE_PARSER,
        parents=[parent_parser], epilog=help_msgs.PARSER_EPILOG
        % {'cli': 'profile', 'option': 'add'},
        formatter_class=RawTextHelpFormatter)

    subparsers = parser.add_subparsers(dest='subparser_name')

    add_wsn430_parser = subparsers.add_parser(
        'addwsn430', help='add wsn430 user profile',
        epilog=help_msgs.ADD_EPILOG,
        formatter_class=RawTextHelpFormatter)

    add_m3_parser = subparsers.add_parser(
        'addm3', help='add m3 user profile',
        epilog=help_msgs.ADD_EPILOG,
        formatter_class=RawTextHelpFormatter)

    del_parser = subparsers.add_parser(
        'del',
        help='delete user profile')

    get_parser = subparsers.add_parser(
        'get', help='get user\'s profile')

    load_parser = subparsers.add_parser(
        'load', help='load user profile')

    add_m3_parser.add_argument(
        '-n', '--name', dest='name', required=True,
        help='profile name')

    add_m3_parser.add_argument(
        '-p', '--power', dest='power_mode', default='dc',
        help='power mode (dc by default)',
        choices=ProfileM3.choices['power_mode'])

    add_m3_parser.add_argument(
        '-j', '--json', dest='json',
        action='store_true',
        help='print profile JSON representation without add it')

    group_m3_consumption = add_m3_parser.add_argument_group(
        'M3 consumption measure')

    group_m3_consumption.add_argument(
        '-current', action='store_true',
        help='current measure')

    group_m3_consumption.add_argument(
        '-voltage', action='store_true',
        help='voltage measure')

    group_m3_consumption.add_argument(
        '-power', action='store_true',
        help='power measure')

    group_m3_consumption.add_argument(
        '-period', dest='period', type=int,
        choices=ProfileM3.choices['consumption']['period'],
        help='period measure (us)')

    group_m3_consumption.add_argument(
        '-avg', dest='average', type=int,
        choices=ProfileM3.choices['consumption']['average'],
        help='average measure')

    group_m3_radio = add_m3_parser.add_argument_group(
        'M3 radio measure')

    group_m3_radio.add_argument(
        '-rssi', action='store_true',
        help='RSSI measure')

    group_m3_radio.add_argument(
        '-channels', dest='channels', nargs='+',
        type=int, choices=ProfileM3.choices['radio']['channels'],
        metavar='{11..26}', help='List of channels (11 to 26)')

    group_m3_radio.add_argument(
        '-num', dest='num_per_channel', default=0, type=int,
        choices=ProfileM3.choices['radio']['num_per_channel'],
        metavar='{0..255}', help='Number of measure by channel')

    group_m3_radio.add_argument(
        '-rperiod', dest='rperiod', type=int,
        choices=ProfileM3.choices['radio']['period'],
        metavar='{1..65535}', help='period measure')

    #
    # WSN430 profile
    #

    add_wsn430_parser.add_argument('-n', '--name', required=True,
                                   help='profile name')
    add_wsn430_parser.add_argument(
        '-j', '--json', action='store_true',
        help='print profile JSON representation without add it')

    add_wsn430_parser.add_argument(
        '-p', '--power',
        dest='power_mode', default='dc',
        help='power mode (dc by default)',
        choices=ProfileWSN430.choices['power_mode'])

    # WSN430 Consumption
    group_wsn430_consumption = add_wsn430_parser.add_argument_group(
        'WSN430 consumption measure')

    group_wsn430_consumption.add_argument(
        '-cfreq', dest='cfreq', type=int,
        choices=ProfileWSN430.choices['consumption']['frequency'],
        help='frequency measure (ms)')

    group_wsn430_consumption.add_argument(
        '-power', action='store_true',
        help='power measure')
    group_wsn430_consumption.add_argument(
        '-voltage', action='store_true',
        help='voltage measure')
    group_wsn430_consumption.add_argument(
        '-current', action='store_true',
        help='current measure')

    # WSN430 Radio
    group_wsn430_radio = add_wsn430_parser.add_argument_group(
        'WSN430 radio measure')
    group_wsn430_radio.add_argument(
        '-rfreq', dest='rfreq', type=int,
        choices=ProfileWSN430.choices['radio']['frequency'],
        help='frequency measure (ms)')
    group_wsn430_radio.add_argument(
        '-rssi', action='store_true',
        help='RSSI measure')

    # WSN430 Sensor
    group_wsn430_sensor = add_wsn430_parser.add_argument_group(
        'WSN430 sensor measure')
    group_wsn430_sensor.add_argument(
        '-sfreq', dest='sfreq', type=int,
        choices=ProfileWSN430.choices['sensor']['frequency'],
        help='frequency measure (ms)')

    group_wsn430_sensor.add_argument(
        '-temperature', action='store_true',
        help='temperature measure')
    group_wsn430_sensor.add_argument(
        '-luminosity', action='store_true',
        help='luminosity measure')

    # Delete Profile
    del_parser.add_argument('-n', '--name', required=True, help='profile name')

    # Get Profile
    get_group = get_parser.add_mutually_exclusive_group(required=True)

    get_group.add_argument('-n', '--name', help='profile name')

    get_group.add_argument(
        '-l', '--list', action='store_true',
        help='print profile\'s list JSON representation')

    # Load Profile
    load_parser.add_argument(
        '-f', '--file', dest='path_file', required=True,
        help='profile JSON representation path file')

    return parser


def add_wsn430_profile_parser(api, opts):
    """ Add WSN430 user profile with JSON Encoder serialization object Profile.

    :param api: API Rest api object
    :param opts: command-line parser opts
    :type opts:  Namespace object with opts attribute
    """

    try:
        profile = ProfileWSN430(opts.name, opts.power_mode)
        profile.set_radio(opts.rfreq, opts.rssi)
        profile.set_consumption(opts.cfreq, opts.power, opts.voltage,
                                opts.current)
        profile.set_sensors(opts.sfreq, opts.temperature, opts.luminosity)
    except AssertionError as err:
        raise ValueError(err.message)

    if opts.json:
        return profile
    else:
        return api.add_profile(opts.name, profile)


def add_m3_profile_parser(api, opts):
    """ Add M3 user profile with JSON Encoder serialization object Profile.

    :param api: API Rest api object
    :param opts: command-line parser opts
    :type opts:  Namespace object with opts attribute
    """

    try:
        profile = ProfileM3(opts.name, opts.power_mode)
        profile.set_consumption(opts.period, opts.average,
                                opts.power, opts.voltage, opts.current)
        profile.set_radio('rssi', opts.channels, opts.rperiod,
                          opts.num_per_channel)
    except AssertionError as err:
        raise ValueError(err.message)

    if opts.json:
        return profile
    else:
        return api.add_profile(opts.name, profile)


def load_profile_parser(api, path_file):
    """  Load and add user profile description

    :param api: API Rest api object
    :param path_file: path file profile description
    :type path_file: string
    """
    profile = json.loads(helpers.read_file(path_file))
    if "profilename" not in profile:
        raise ValueError("'profilename' attribute required in JSON file: %r" %
                         path_file)

    return api.add_profile(profile["profilename"], profile)


def del_profile_parser(api, name):
    """ Delete user profile description

    :param name: profile name
    :type name: string
    :param api: API Rest api object
    """
    return api.del_profile(name)


def get_profile_parser(api, opts):
    """ Get user profile description
    _ print JSONObject profile description
    _ print JSONObject profile's list description

    :param opts: command-line parser opts
    :type opts: Namespace object with opts attribute
    :param api: API Rest api object
    """
    if opts.list:
        profile_dict = api.get_profiles()
    elif opts.name is not None:
        profile_dict = api.get_profile(opts.name)
    return profile_dict


def profile_parse_and_run(opts):
    """ Parse namespace 'opts' object and execute requested command """
    user, passwd = auth.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)

    subparser_name = opts.subparser_name
    if subparser_name == 'addwsn430':
        result = add_wsn430_profile_parser(api, opts)
    elif subparser_name == 'addm3':
        result = add_m3_profile_parser(api, opts)
    elif subparser_name == 'load':
        result = load_profile_parser(api, opts.path_file)
    elif subparser_name == 'get':
        result = get_profile_parser(api, opts)
    elif subparser_name == 'del':
        result = del_profile_parser(api, opts.name)

    return result


def main(args=sys.argv[1:]):
    """ Main command-line execution loop.  """
    parser = parse_options()
    common.main_cli(profile_parse_and_run, parser, args)
