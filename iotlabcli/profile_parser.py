# -*- coding:utf-8 -*-
"""Profile parser"""

import json
import sys
import argparse
from argparse import RawTextHelpFormatter

from iotlabcli import helpers, rest, help_parser
from iotlabcli.profile import Profile, Consumption, Radio, Sensor


def parse_options():
    """
    Handle profile-cli command-line options with argparse
    """
    parent_parser = argparse.ArgumentParser(add_help=False)
    # We create top level parser
    parser = argparse.ArgumentParser(
        description=help_parser.PROFILE_PARSER,
        parents=[parent_parser], epilog=help_parser.PARSER_EPILOG
        % {'cli': 'profile', 'option': 'add'},
        formatter_class=RawTextHelpFormatter)

    parser.add_argument('-u', '--user', dest='username')
    parser.add_argument('-p', '--password', dest='password')

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
        type=helpers.check_radio_channels,
        help='List of channels (11 to 26)')

    group_m3_radio.add_argument(
        '-num', dest='num_per_channel',
        type=helpers.check_radio_num_per_channel,
        metavar='{0..255}',
        help='Number of measure by channel')

    group_m3_radio.add_argument(
        '-rperiod', dest='rperiod',
        type=helpers.check_radio_period,
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


def add_wsn430_profile(options, request, parser):
    """ Add WSN430 user profile with JSON Encoder serialization object Profile.

    :param options: command-line parser options
    :type options:  Namespace object with options attribute
    :param request: API Rest request object
    """
    consumption = None
    radio = None
    sensor = None

    if options.current or options.voltage or options.power:
        if options.cfreq is not None:
            consumption = Consumption(current=options.current,
                                      voltage=options.voltage,
                                      power=options.power,
                                      frequency=options.cfreq)
        else:
            parser.error(
                "You must specify a frequency for consumption measure.")

    if options.rssi:
        if options.rfreq is not None:
            radio = Radio(rssi=options.rssi, frequency=options.rfreq)
        else:
            parser.error("You must specify a frequency for radio measure.")

    if options.luminosity or options.temperature:
        if options.sfreq is not None:
            sensor = Sensor(temperature=options.temperature,
                            luminosity=options.luminosity,
                            frequency=options.sfreq)
        else:
            parser.error("You must specify a frequency for sensor measure.")

    profile = Profile(nodearch='wsn430',
                      profilename=options.name,
                      power=options.power_mode,
                      consumption=consumption,
                      radio=radio,
                      sensor=sensor)

    profile_json = json.dumps(profile, cls=rest.Encoder, sort_keys=True,
                              indent=4)

    if options.json:
        print profile_json
    else:
        request.add_profile(options.name, profile_json)


def add_m3_profile(options, request, parser):
    """ Add M3 user profile with JSON Encoder serialization object Profile.

    :param options: command-line parser options
    :type options:  Namespace object with options attribute
    :param request: API Rest request object
    """
    consumption = None
    radio = None

    if options.current or options.voltage or options.cpower:
        if options.period is not None and options.average is not None:
            consumption = Consumption(current=options.current,
                                      voltage=options.voltage,
                                      power=options.cpower,
                                      period=options.period,
                                      average=options.average)
        else:
            parser.error("You must specify values for period/average"
                         " consumption measure.")

    if options.rssi:
        if options.rperiod is not None and options.channels is not None:
            if options.num_per_channel is None and len(options.channels) > 1:
                parser.error("You must specify value for "
                             "number of measure by channel.")
            elif len(options.channels) == 1:
                options.num_per_channel = 0
            radio = Radio(mode="rssi",
                          period=options.rperiod,
                          num_per_channel=options.num_per_channel,
                          channels=options.channels)
        else:
            parser.error(
                ("You must specify values for "
                 "channels/period radio measure."))

    profile = Profile(nodearch='m3',
                      profilename=options.name,
                      power=options.power_mode,
                      consumption=consumption,
                      radio=radio)

    profile_json = json.dumps(profile, cls=rest.Encoder, sort_keys=True,
                              indent=4)

    if options.json:
        print profile_json
    else:
        request.add_profile(options.name, profile_json)


def load_profile(path_file, request, parser):
    """  Load and add user profile description

    :param path_file: path file profile description
    :type path_file: string
    :param request: API Rest request object
    :param parser: command-line parser
    """
    file_data = helpers.open_file(path_file, parser)[1]
    request.add_profile(file_data)


def del_profile(name, request):
    """ Delete user profile description

    :param name: profile name
    :type name: string
    :param request: API Rest request object
    """
    request.del_profile(name)


def get_profile(parser_options, request):
    """ Get user profile description
    _ print JSONObject profile description
    _ print JSONObject profile's list description

    :param parser_options: command-line parser options
    :type parser_options: Namespace object with options attribute
    :param request: API Rest request object
    """
    if parser_options.list:
        profile_json = request.get_profiles()
    elif parser_options.name is not None:
        profile_json = request.get_profile(parser_options.name)
    print json.dumps(json.loads(profile_json), indent=4, sort_keys=True)


def main(args=sys.argv[1:]):
    """
    Main command-line execution loop.
    """
    try:
        parser = parse_options()
        parser_options = parser.parse_args(args)
        request = rest.Api(
            username=parser_options.username,
            password=parser_options.password,
            parser=parser)
        subparser_name = parser_options.subparser_name
        if subparser_name == 'addwsn430':
            add_wsn430_profile(parser_options, request, parser)
        elif subparser_name == 'addm3':
            add_m3_profile(parser_options, request, parser)
        elif subparser_name == 'load':
            load_profile(parser_options.path_file, request, parser)
        elif subparser_name == 'get':
            get_profile(parser_options, request)
        elif subparser_name == 'del':
            del_profile(parser_options.name, request)
    except KeyboardInterrupt:
        print >> sys.stderr, "\nStopped."
        sys.exit()
