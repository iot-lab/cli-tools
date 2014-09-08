# -*- coding:utf-8 -*-
"""Profile parser"""

import json
import sys
import argparse
from argparse import RawTextHelpFormatter

from iotlabcli import Error
from iotlabcli import helpers, rest, help_parser
from iotlabcli.profile import Profile, Consumption, Radio, Sensor
from iotlabcli import parser_common


def parse_options():
    """
    Handle profile-cli command-line opts with argparse
    """
    parent_parser = parser_common.base_parser()
    # We create top level parser
    parser = argparse.ArgumentParser(
        description=help_parser.PROFILE_PARSER,
        parents=[parent_parser], epilog=help_parser.PARSER_EPILOG
        % {'cli': 'profile', 'option': 'add'},
        formatter_class=RawTextHelpFormatter)

    subparsers = parser.add_subparsers(dest='subparser_name')

    add_wsn430_parser = subparsers.add_parser(
        'addwsn430', help='add wsn430 user profile',
        epilog=help_parser.ADD_EPILOG,
        formatter_class=RawTextHelpFormatter)

    add_m3_parser = subparsers.add_parser(
        'addm3', help='add m3 user profile',
        epilog=help_parser.ADD_EPILOG,
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
        choices=['dc', 'battery'])

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
        '-cpower', action='store_true',
        help='power measure')

    group_m3_consumption.add_argument(
        '-period', dest='period', type=int,
        choices=[140, 204, 332, 588, 1100, 2116, 4156, 8244],
        help='period measure (us)')

    group_m3_consumption.add_argument(
        '-avg', dest='average', type=int,
        choices=[1, 4, 16, 64, 128, 256, 512, 1024],
        help='average measure')

    group_m3_radio = add_m3_parser.add_argument_group(
        'M3 radio measure')

    group_m3_radio.add_argument(
        '-rssi', action='store_true',
        help='RSSI measure')

    group_m3_radio.add_argument(
        '-channels', dest='channels', nargs='+',
        type=int, choices=range(11, 27),
        metavar='{11..26}',
        help='List of channels (11 to 26)')

    group_m3_radio.add_argument(
        '-num', dest='num_per_channel',
        type=int, choices=range(1, 256),
        metavar='{0..255}',
        help='Number of measure by channel')

    group_m3_radio.add_argument(
        '-rperiod', dest='rperiod',
        type=int, choices=range(1, 2**16),
        metavar='{1..65535}',
        help='period measure')

    add_wsn430_parser.add_argument(
        '-n', '--name', dest='name', required=True,
        help='profile name')

    add_wsn430_parser.add_argument(
        '-p', '--power',
        dest='power_mode', default='dc',
        help='power mode (dc by default)', choices=['dc', 'battery'])

    add_wsn430_parser.add_argument(
        '-j', '--json',
        dest='json', action='store_true',
        help='print profile JSON representation without add it')

    group_wsn430_consumption = add_wsn430_parser.add_argument_group(
        'WSN430 consumption measure')

    group_wsn430_consumption.add_argument(
        '-current', action='store_true',
        help='current measure')

    group_wsn430_consumption.add_argument(
        '-voltage', action='store_true',
        help='voltage measure')

    group_wsn430_consumption.add_argument(
        '-power', action='store_true',
        help='power measure')

    group_wsn430_consumption.add_argument(
        '-cfreq', dest='cfreq', type=int,
        choices=[5000, 1000, 500, 100, 70],
        help='frequency measure (ms)')

    group_wsn430_radio = add_wsn430_parser.add_argument_group(
        'WSN430 radio measure')

    group_wsn430_radio.add_argument(
        '-rssi', action='store_true',
        help='RSSI measure')

    group_wsn430_radio.add_argument(
        '-rfreq', dest='rfreq', type=int,
        choices=[5000, 1000, 500],
        help='frequency measure (ms)')

    group_wsn430_sensor = add_wsn430_parser.add_argument_group(
        'WSN430 sensor measure')

    group_wsn430_sensor.add_argument(
        '-temperature', action='store_true',
        help='temperature measure')

    group_wsn430_sensor.add_argument(
        '-luminosity', action='store_true',
        help='luminosity measure')

    group_wsn430_sensor.add_argument(
        '-sfreq', dest='sfreq', type=int,
        choices=[30000, 10000, 5000, 1000],
        help='frequency measure (ms)')

    del_parser.add_argument(
        '-n', '--name', dest='name', required=True,
        help='profile name')

    get_group = get_parser.add_mutually_exclusive_group(required=True)

    get_group.add_argument(
        '-n', '--name',
        dest='name', help='profile name')

    get_group.add_argument(
        '-l', '--list', action='store_true', dest='list',
        help='print profile\'s list JSON representation')

    load_parser.add_argument(
        '-f', '--file', dest='path_file', required=True,
        help='profile JSON representation path file')

    return parser


def add_wsn430_profile(api, opts):
    """ Add WSN430 user profile with JSON Encoder serialization object Profile.

    :param opts: command-line parser opts
    :type opts:  Namespace object with opts attribute
    :param api: API Rest api object
    """
    consumption = None
    radio = None
    sensor = None

    if opts.current or opts.voltage or opts.power:
        if opts.cfreq is None:
            raise Error(
                "You must specify a frequency for consumption measure.")
        consumption = Consumption(current=opts.current,
                                  voltage=opts.voltage,
                                  power=opts.power,
                                  frequency=opts.cfreq)

    if opts.rssi:
        if opts.rfreq is None:
            raise Error("You must specify a frequency for radio measure.")
        radio = Radio(rssi=opts.rssi, frequency=opts.rfreq)

    if opts.luminosity or opts.temperature:
        if opts.sfreq is None:
            raise Error("You must specify a frequency for sensor measure.")
        sensor = Sensor(temperature=opts.temperature,
                        luminosity=opts.luminosity,
                        frequency=opts.sfreq)

    profile = Profile(nodearch='wsn430',
                      profilename=opts.name,
                      power=opts.power_mode,
                      consumption=consumption,
                      radio=radio,
                      sensor=sensor)

    if opts.json:
        return profile
    else:
        return api.add_profile(opts.name, profile)


def add_m3_profile(api, opts):
    """ Add M3 user profile with JSON Encoder serialization object Profile.

    :param opts: command-line parser opts
    :type opts:  Namespace object with opts attribute
    :param api: API Rest api object
    """
    consumption = None
    radio = None

    if opts.current or opts.voltage or opts.cpower:
        if opts.period is not None and opts.average is not None:
            consumption = Consumption(current=opts.current,
                                      voltage=opts.voltage,
                                      power=opts.cpower,
                                      period=opts.period,
                                      average=opts.average)
        else:
            raise Error("You must specify values for period/average"
                        " consumption measure.")

    if opts.rssi:
        if opts.rperiod is None or opts.channels is None:
            raise Error("You must specify values for "
                        "channels/period radio measure.")

        if opts.num_per_channel is None and len(opts.channels) > 1:
            raise Error("You must specify value for "
                        "number of measure by channel.")
        elif len(opts.channels) == 1:
            opts.num_per_channel = 0

        radio = Radio(mode="rssi",
                      period=opts.rperiod,
                      num_per_channel=opts.num_per_channel,
                      channels=opts.channels)

    profile = Profile(nodearch='m3',
                      profilename=opts.name,
                      power=opts.power_mode,
                      consumption=consumption,
                      radio=radio)

    if opts.json:
        return profile
    else:
        return api.add_profile(opts.name, profile)


def load_profile(api, path_file):
    """  Load and add user profile description

    :param path_file: path file profile description
    :type path_file: string
    :param api: API Rest api object
    """
    file_data = helpers.open_file(path_file)[1]
    profile = json.loads(file_data)
    if "profilename" not in profile:
        raise Error("You must have a profilename attribute in your JSON file")
    return api.add_profile(profile["profilename"], profile)


def del_profile(api, name):
    """ Delete user profile description

    :param name: profile name
    :type name: string
    :param api: API Rest api object
    """
    return api.del_profile(name)


def get_profile(api, opts):
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
    username, password = helpers.get_user_credentials(
        opts.username, opts.password)

    api = rest.Api(username, password)
    subparser_name = opts.subparser_name
    if subparser_name == 'addwsn430':
        result = add_wsn430_profile(api, opts)
    elif subparser_name == 'addm3':
        result = add_m3_profile(api, opts)
    elif subparser_name == 'load':
        result = load_profile(api, opts.path_file)
    elif subparser_name == 'get':
        result = get_profile(api, opts)
    elif subparser_name == 'del':
        result = del_profile(api, opts.name)

    return result


def main(args=sys.argv[1:]):
    """ Main command-line execution loop.  """
    parser = parse_options()
    parser_common.main_cli(profile_parse_and_run, parser, args)
