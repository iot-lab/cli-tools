import argparse
import helpers
import json
import sys
from profile import *
import rest
from help_parser import *
from argparse import RawTextHelpFormatter

def parse_options():
    """
    Handle profile-cli command-line options with argparse
    """
    parent_parser = argparse.ArgumentParser(add_help=False)
    # We create top level parser
    parser = argparse.ArgumentParser(description=PROFILE_PARSER, parents=[parent_parser], epilog=PARSER_EPILOG % {'cli' : 'profile', 'option' : 'add' },
       formatter_class=RawTextHelpFormatter)
    parser.add_argument('-u','--user',dest='username')
    parser.add_argument('-p','--password',dest='password')

    subparsers = parser.add_subparsers(dest='subparser_name')

    add_profile = subparsers.add_parser('add', help='add user profile', epilog=ADD_EPILOG,
        formatter_class=RawTextHelpFormatter)
    del_profile = subparsers.add_parser('del', help='delete user profile')
    get_profile = subparsers.add_parser('get', help='get user\'s profile')
    load_profile = subparsers.add_parser('load', help='load user profile')

    add_profile.add_argument('-n', '--name', dest='name', required=True, help='profile name')
    add_profile.add_argument('-p', '--power', dest='power_mode', default='dc', help='power mode (dc by default)', choices=['dc','battery'])
    add_profile.add_argument('-j', '--json', dest='json', action='store_true', help='print profile JSON representation without add it')
    group_consumption = add_profile.add_argument_group('consumption measure')
    group_consumption.add_argument('-current', action='store_true', help='current measure')
    group_consumption.add_argument('-voltage', action='store_true', help='voltage measure')
    group_consumption.add_argument('-power', action='store_true', help='power measure')
    group_consumption.add_argument('-cfreq', dest='cfreq',
        help='frequency measure (ms)', type=int, choices=[5000,1000,500,100,70], default=5000)
    group_radio = add_profile.add_argument_group('radio measure')
    group_radio.add_argument('-rssi', action='store_true', help='RSSI measure')
    group_radio.add_argument('-rfreq', dest='rfreq',
        help='frequency measure (ms)', type=int, choices=[5000,1000,500], default=5000)
    group_sensor = add_profile.add_argument_group('sensor measure')
    group_sensor.add_argument('-temperature', action='store_true', help='temperature measure')
    group_sensor.add_argument('-luminosity', action='store_true', help='luminosity measure')
    group_sensor.add_argument('-sfreq', dest='sfreq',
        help='frequency measure (ms)', type=int, choices=[30000,10000,5000,1000], default=30000)

    del_profile.add_argument('-n', '--name', dest='name', required=True, help='profile name')

    get_group = get_profile.add_mutually_exclusive_group(required=True)
    get_group.add_argument('-n', '--name', dest='name', help='profile name')
    get_group.add_argument('-l', '--list', action='store_true', dest='list', help='print profile\'s list JSON representation')

    load_profile.add_argument('-f', '--file', dest='path_file', required=True, help='profile JSON representation path file')

    return parser

def add_profile(parser_options, request):
    """ Add user profile with JSON Encoder serialization object Profile.

    :param parser_options: command-line parser options
    :type parser_options: Namespace object with options attribute
    :param request: API Rest request object
    """
    profile=Profile(parser_options.name,parser_options.power_mode)
    if (parser_options.current or parser_options.voltage or parser_options.power):
       consumption = Consumption(parser_options.current,parser_options.voltage,
              parser_options.power,parser_options.cfreq)
       profile.consumption = consumption
    if (parser_options.rssi):
       radio = Radio(parser_options.rssi,parser_options.rfreq)
       profile.radio = radio
    if (parser_options.luminosity or parser_options.temperature):
       sensor = Sensor(parser_options.temperature,parser_options.luminosity,parser_options.sfreq)
       profile.sensor = sensor
    profile_json = json.dumps(profile,cls=rest.Encoder,sort_keys=True, indent=4)
    if (parser_options.json):
       print profile_json
    else:
       request.add_profile(profile_json)

def load_profile(path_file, request, parser):
    """  Load and add user profile description

    :param path_file: path file profile description
    :type path_file: string
    :param request: API Rest request object
    :param parser: command-line parser
    """
    profile_file_name, profile_file_data = helpers.open_json_file(path_file, parser)
    request.add_profile(profile_file_data)

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
    if (parser_options.list):
       profile_json = request.get_profiles()
    elif (parser_options.name is not None):
       profile_json = request.get_profile(parser_options.name)
    print(json.dumps(json.loads(profile_json), indent=4, sort_keys=True))

def main():
    """
    Main command-line execution loop.
    """
    try:
       parser = parse_options()
       parser_options = parser.parse_args()
       request = rest.Api(username=parser_options.username, password=parser_options.password,
           parser=parser)
       subparser_name = parser_options.subparser_name
       if (subparser_name == 'add'):
          add_profile(parser_options, request)
       elif (subparser_name == 'load'):
          load_profile(parser_options.path_file, request, parser)
       elif (subparser_name == 'get'):
          get_profile(parser_options, request)
       elif (subparser_name == 'del'):
          del_profile(parser_options.name, request)
    except KeyboardInterrupt:
        print >> sys.stderr, "\nStopped."
        sys.exit()
