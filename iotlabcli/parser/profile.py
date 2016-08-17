# -*- coding:utf-8 -*-

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
from iotlabcli.profile import ProfileWSN430, ProfileM3, ProfileA8
from iotlabcli.profile import ProfileCustom

PROFILE_PARSER = """

profile-cli command-line manage profiles experimentation :
store you favourite resources configuration with combination
of a power supply mode and an automatic measure configuration
(e.g. consumption, radio, ...)

"""


def parse_options():
    """ Handle profile-cli command-line opts with argparse """
    parent_parser = common.base_parser()
    # We create top level parser
    parser = argparse.ArgumentParser(
        description=PROFILE_PARSER,
        parents=[parent_parser], epilog=help_msgs.PARSER_EPILOG.format(
            cli='profile', option='add'),
        formatter_class=RawTextHelpFormatter)

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True  # not required by default in Python3

    add_wsn430_parser = subparsers.add_parser(
        'addwsn430', help='add wsn430 user profile',
        epilog=help_msgs.ADD_EPILOG_WSN430,
        formatter_class=RawTextHelpFormatter)

    #
    # m3 profile
    #
    add_m3_parser = subparsers.add_parser(
        'addm3', help='add m3 user profile',
        epilog=help_msgs.ADD_EPILOG_M3_A8.format(cmd='addm3', archi='m3'),
        formatter_class=RawTextHelpFormatter)
    add_m3_a8_parser('M3', add_m3_parser)

    #
    # a8 profile
    #
    add_a8_parser = subparsers.add_parser(
        'adda8', help='add a8 user profile',
        epilog=help_msgs.ADD_EPILOG_M3_A8.format(cmd='adda8', archi='a8'),
        formatter_class=RawTextHelpFormatter)
    add_m3_a8_parser('A8', add_a8_parser)

    add_custom_parser = subparsers.add_parser(
        'addcustom', help='add custom user profile',
        epilog=help_msgs.ADD_EPILOG_M3_A8.format(cmd='addcustom',
                                                 archi='custom'),
        formatter_class=RawTextHelpFormatter)
    add_m3_a8_parser('CUSTOM', add_custom_parser)

    del_parser = subparsers.add_parser('del', help='delete user profile')
    get_parser = subparsers.add_parser('get', help='get user\'s profile')
    load_parser = subparsers.add_parser('load', help='load user profile')

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
        'Consumption measure')

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
        'Radio measure')
    group_wsn430_radio.add_argument(
        '-rfreq', dest='rfreq', type=int,
        choices=ProfileWSN430.choices['radio']['frequency'],
        help='frequency measure (ms)')

    # WSN430 Sensor
    group_wsn430_sensor = add_wsn430_parser.add_argument_group(
        'Sensor measure')
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


def add_m3_a8_parser(node_type, subparser):
    """ Add options for m3 and a8 parsers as they are the same """
    node_class = {
        'M3': ProfileM3, 'A8': ProfileA8, 'CUSTOM': ProfileCustom
    }[node_type]

    subparser.add_argument('-n', '--name', dest='name', required=True,
                           help='profile name')

    subparser.add_argument('-p', '--power', dest='power_mode', default='dc',
                           help='power mode (dc by default)',
                           choices=node_class.choices['power_mode'])

    subparser.add_argument(
        '-j', '--json', dest='json',
        action='store_true',
        help='print profile JSON representation without add it')

    # Radio configuration
    consumption = subparser.add_argument_group('Consumption measure')

    consumption.add_argument(
        '-current', action='store_true', help='current measure')

    consumption.add_argument(
        '-voltage', action='store_true', help='voltage measure')

    consumption.add_argument(
        '-power', action='store_true', help='power measure')

    consumption.add_argument(
        '-period', dest='period', type=int,
        choices=node_class.choices['consumption']['period'],
        help='period measure (us)')

    consumption.add_argument(
        '-avg', dest='average', type=int,
        choices=node_class.choices['consumption']['average'],
        help='average measure')

    # Radio configuration
    radio = subparser.add_argument_group('Radio measure mode')

    radio.add_argument(
        '-rssi', dest='mode', action='store_const', const='rssi',
        help='RSSI measure. Configure with `channels`, `num` and `rperiod`')

    radio.add_argument(
        '-sniffer', dest='mode', action='store_const', const='sniffer',
        help='Radio Sniffer. Configure one channel with `channels`.')

    radio_cfg = subparser.add_argument_group('Radio measure config')

    radio_cfg.add_argument(
        '-channels', dest='channels', nargs='+',
        type=int, choices=node_class.choices['radio']['channels'],
        metavar='{11..26}', help='List of channels (11 to 26)')

    radio_cfg.add_argument(
        '-num', dest='num_per_channel', type=int, metavar='{0..255}',
        choices=node_class.choices['radio']['num_per_channel'],
        help='Number of measure by channel, if multiple channels supplied')

    radio_cfg.add_argument(
        '-rperiod', dest='rperiod', type=int,
        choices=node_class.choices['radio']['period'],
        metavar='{1..65535}', help='period measure')


def _wsn430_profile(opts):
    """ Create a wsn430 profile from namespace object """
    profile = ProfileWSN430(profilename=opts.name, power=opts.power_mode)
    profile.set_consumption(frequency=opts.cfreq, power=opts.power,
                            voltage=opts.voltage, current=opts.current)
    profile.set_radio(frequency=opts.rfreq)
    profile.set_sensors(frequency=opts.sfreq, temperature=opts.temperature,
                        luminosity=opts.luminosity)
    return profile


def _m3_a8_profile(opts, node_class):
    """ Create a node_class profile from namespace object """
    profile = node_class(profilename=opts.name, power=opts.power_mode)
    profile.set_consumption(period=opts.period, average=opts.average,
                            power=opts.power, voltage=opts.voltage,
                            current=opts.current)
    profile.set_radio(mode=opts.mode, channels=opts.channels,
                      period=opts.rperiod,
                      num_per_channel=opts.num_per_channel)
    return profile


def _m3_profile(opts):
    """ Create a m3 profile from namespace object """
    return _m3_a8_profile(opts, ProfileM3)


def _a8_profile(opts):
    """ Create a a8 profile from namespace object """
    return _m3_a8_profile(opts, ProfileA8)


def _custom_profile(opts):
    """ Create a a8 profile from namespace object """
    return _m3_a8_profile(opts, ProfileCustom)


def _add_profile(api, name, profile, json_out=False):
    """ Add user profile. if json, dump json dict to stdout """
    if json_out:
        return profile
    else:
        return api.add_profile(name, profile)


def add_profile_parser(api, opts):
    """ Add user profile with JSON Encoder serialization object Profile.

    :param api: API Rest api object
    :param opts: command-line parser opts
    :type opts:  Namespace object with opts attribute
    """
    profile_func_d = {
        'addwsn430': _wsn430_profile,
        'addm3': _m3_profile,
        'adda8': _a8_profile,
        'addcustom': _custom_profile
    }

    try:
        profile = profile_func_d[opts.command](opts)
        return _add_profile(api, opts.name, profile, opts.json)
    except AssertionError as err:   # pragma: no cover
        raise ValueError(str(err))


def load_profile_parser(api, opts):
    """  Load and add user profile description

    :param api: API Rest api object
    :param opts: command-line parser opts
    :type opts: Namespace object with opts attribute
    """
    try:
        profile = json.loads(helpers.read_file(opts.path_file))
        return _add_profile(api, profile['profilename'], profile)
    except KeyError:  # pragma: no cover
        raise ValueError(
            "'profilename' required in profile JSON file: %r" % opts.path_file)


def del_profile_parser(api, opts):
    """ Delete user profile description

    :param api: API Rest api object
    :param opts: command-line parser opts
    :type opts: Namespace object with opts attribute
    """
    return api.del_profile(opts.name)


def get_profile_parser(api, opts):
    """ Get user profile description
    _ print JSONObject profile description
    _ print JSONObject profile's list description

    :param api: API Rest api object
    :param opts: command-line parser opts
    :type opts: Namespace object with opts attribute
    """
    assert opts.list or opts.name is not None

    if opts.list:
        profile_dict = api.get_profiles()
    else:
        profile_dict = api.get_profile(opts.name)

    return profile_dict


def profile_parse_and_run(opts):
    """ Parse namespace 'opts' object and execute requested command """
    user, passwd = auth.get_user_credentials(opts.username, opts.password)
    api = rest.Api(user, passwd)

    fct_parser = {
        'addwsn430': add_profile_parser,
        'addm3': add_profile_parser,
        'adda8': add_profile_parser,
        'addcustom': add_profile_parser,
        'load': load_profile_parser,
        'get': get_profile_parser,
        'del': del_profile_parser,
    }[opts.command]

    return fct_parser(api, opts)


def main(args=None):
    """ Main command-line execution loop." """
    args = args or sys.argv[1:]
    parser = parse_options()
    common.main_cli(profile_parse_and_run, parser, args)
