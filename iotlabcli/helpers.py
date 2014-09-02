# -*- coding:utf-8 -*-
"""Helpers methods"""

import getpass
import os
import base64
import json
from argparse import ArgumentTypeError

from iotlabcli import Error
from iotlabcli import parser_common

DOMAIN_DNS = 'iot-lab.info'


def password_prompt():
    """ password prompt when command-line option username (e.g. -u or --user)
    is used without password

    :returns password
    """
    pprompt = lambda: (getpass.getpass(),
                       getpass.getpass('Retype password: '))
    prompt1, prompt2 = pprompt()
    while prompt1 != prompt2:
        print 'Passwords do not match. Try again'
        prompt1, prompt2 = pprompt()
    return prompt1


def create_password_file(username, password):
    """ Create a password file for basic authentication http when
    command-line option username and password are used We write .iotlabrc
    file in user home directory with format username:base64(password)

    :param username: basic http auth username
    :type username: string
    :param password: basic http auth password
    :type password: string
    """
    if username is None or password is None:
        raise Error("No username or password provided: %s:%s",
                    username, password)
    home_directory = os.getenv('USERPROFILE') or os.getenv('HOME')
    try:
        password_file = open('%s/%s' % (home_directory, '.iotlabrc'), 'wb')
    except IOError:
        raise Error("Cannot create password file in home directory: %s"
                    % home_directory)
    else:
        password_file.write('%s:%s' % (username, base64.b64encode(password)))
        password_file.close()


def read_password_file():
    """ Try to read password file (.iotlabrc) in user home directory when
    command-line option username and password are not used. If password
    file exist whe return username and password for basic auth http
    authentication

    """

    home_directory = os.getenv('USERPROFILE') or os.getenv('HOME')
    path_file = '%s/%s' % (home_directory, '.iotlabrc')
    if os.path.exists(path_file):
        try:
            password_file = open(path_file, 'r')
        except IOError:
            raise Error("Cannot open password file in home directory: "
                        "%s." % home_directory)
        else:
            field = (password_file.readline()).split(':')
            if not len(field) == 2:
                raise Error("Bad password file format in home directory: "
                            "%s." % home_directory)
            password_file.close()
            return field[0], base64.b64decode(field[1])
    else:
        return None, None


def read_json_file(json_file_name, json_file_data):
    try:
        json_data = json.loads(json_file_data)
        return json_data
    except ValueError:
        raise Error("Unable to read JSON description file: %s." %
                    json_file_name)


def write_experiment_archive(experiment_id, data):
    try:
        archive_file = open('%s.tar.gz' % experiment_id, 'wb')
    except IOError:
        raise Error("Unable to save experiment archive file: \
            %s.tar.gz." % experiment_id)
    else:
        archive_file.write(data)
        archive_file.close()


def get_user_credentials(username, password):
    if (password is None) and (username is not None):
        password = getpass.getpass()
    elif (password is not None) and (username is not None):
        pass
    else:
        username, password = read_password_file()
    return username, password


def check_radio_period(period):
    value = int(period)
    if value not in range(1, 65536):
        raise ArgumentTypeError(
            "invalid period choice : %s (choose from 1 .. 65535)" % (value,))
    return value


def check_radio_num_per_channel(num):
    value = int(num)
    if value not in range(1, 256):
        raise ArgumentTypeError(
            "invalid period choice : %s (choose from 1 .. 255)" % (value,))
    return value


def check_radio_channels(channel):
    value = int(channel)
    if value not in range(11, 27):
        raise ArgumentTypeError(
            "invalid channel choice : %s (choose from 11 .. 26)" % (value,))
    return value


def check_experiment_state(state):
    oar_state = ["Terminated", "Waiting", "Launching", "Finishing",
                 "Running", "Error"]

    if state is None:
        return ','.join(oar_state)

    for state in state.split(','):
        if state not in oar_state:
            raise Error('The experiment filter state %s is invalid.' % state)
    return state


def check_site(site_name, sites_list):
    """ Check if the given site exists

    >>> sites = ["strasbourg", "grenoble"]
    >>> check_site("grenoble", sites)
    >>> check_site("unknown", sites)
    Traceback (most recent call last):
    ArgumentTypeError: The site name 'unknown' doesn't exist
    """
    if site_name in sites_list:
        return  # site_name is valid
    raise ArgumentTypeError("The site name %r doesn't exist" % site_name)


def check_experiments_running(experiments_json):
    items = experiments_json["items"]
    if len(items) == 0:
        raise Error("You don't have an experiment with state Running")

    experiments_id = [exp["id"] for exp in items]
    if len(experiments_id) > 1:
        raise Error(
            "You have several experiments with state Running. "
            "Use option -i|--id and choose experiment id in this list : %s" %
            experiments_id)
    else:
        return experiments_id[0]


def get_command_list(nodes_list):
    """
    >>> get_command_list('grenoble,m3,0-5+6+8')
    ['grenoble', 'm3', '0-5+6+8']

    >>> get_command_list('grenoble,m3')
    Traceback (most recent call last):
    ArgumentTypeError: Invalid number of argument in nodes list: 'grenoble,m3'

    """
    param_list = nodes_list.split(',')
    if len(param_list) == 3:
        return param_list
    raise ArgumentTypeError(
        'Invalid number of argument in nodes list: %r' % nodes_list)


def check_experiment_list(exp_list):
    param_list = exp_list.split(',')
    valid_list = True
    if param_list[0].isdigit():
        if len(param_list) < 2 or len(param_list) > 4:
            valid_list = False
        experiment_type = 'alias'
    else:
        if len(param_list) < 3 or len(param_list) > 5:
            valid_list = False
        experiment_type = 'physical'

    if not valid_list:
        raise Error(
            'The number of argument in experiment %s list %s is not valid.'
            % (experiment_type, exp_list))
    return experiment_type, param_list


def nodes_list_from_str(nodes_list_str):
    """
    nodes_list_str format: site_name,archi,nodeid_list

    ex: nodes_list_str == 'grenoble,m3,1-34+72'
    """
    sites_list = parser_common.Platform().sites()

    # 'grenoble,m3,1-34+72' -> ['grenoble', 'm3', '1-34+72']
    site, archi, nodes_str = get_command_list(nodes_list_str)
    check_site(site, sites_list)
    check_archi(archi)

    nodes_list = get_nodes_list(site, archi, nodes_str)
    return nodes_list


def check_archi(archi):
    """ Check that archi is valid
    >>> [check_archi(archi) for archi in ['wsn430', 'm3', 'a8']]
    [None, None, None]

    >>> check_archi('msp430')
    Traceback (most recent call last):
    Error: "Invalid not architecture: 'msp430' not in ['wsn430', 'm3', 'a8']"
    """

    archi_list = ['wsn430', 'm3', 'a8']
    if archi in archi_list:
        return  # valid archi
    raise Error("Invalid not architecture: %r not in %s" % (archi, archi_list))


def get_nodes_list(site, archi, nodes_list):
    """

    >>> get_nodes_list('grenoble', 'm3', '1-4+6+7-8')
    ['m3-1.grenoble.iot-lab.info', 'm3-2.grenoble.iot-lab.info', \
'm3-3.grenoble.iot-lab.info', 'm3-4.grenoble.iot-lab.info', \
'm3-6.grenoble.iot-lab.info', 'm3-7.grenoble.iot-lab.info', \
'm3-8.grenoble.iot-lab.info']

    >>> get_nodes_list('grenoble', 'm3', '1-4-5')
    Traceback (most recent call last):
    ArgumentTypeError: Invalid nodes list: 1-4-5 ([0-9+-])

    >>> get_nodes_list('grenoble', 'm3', '3-3')
    Traceback (most recent call last):
    ArgumentTypeError: Invalid nodes list: 3-3 ([0-9+-])

    >>> get_nodes_list('grenoble', 'm3', '3-2')
    Traceback (most recent call last):
    ArgumentTypeError: Invalid nodes list: 3-2 ([0-9+-])

    >>> get_nodes_list('grenoble', 'm3', 'a-b')
    Traceback (most recent call last):
    ArgumentTypeError: Invalid nodes list: a-b ([0-9+-])

    """

    node_fmt = '{archi}-%u.{site}.{domain}'.format(
        archi=archi, site=site, domain=DOMAIN_DNS)

    nodes = []
    try:
        # '1-4+6+8-8'
        for plus_nodes in nodes_list.split('+'):
            # ['1-4', '6', '7-8']

            minus_node = plus_nodes.split('-')
            if len(minus_node) == 1:
                # ['6']
                nodes.append(node_fmt % int(minus_node[0]))
            else:
                # ['1', '4'] or ['7', '8']
                first, last = minus_node
                nodes_range = range(int(first), int(last) + 1)

                # first >= last
                if len(nodes_range) <= 1:
                    raise ValueError

                # Add nodes range
                nodes.extend([node_fmt % num for num in nodes_range])

    except ValueError:
        # invalid: 6-3 or 6-7-8 or non int values
        raise ArgumentTypeError('Invalid nodes list: %s ([0-9+-])' %
                                nodes_list)
    else:
        return nodes


def check_properties(properties_list, sites_list):
    properties = properties_list.split('+')
    if len(properties) > 3:
        raise Error('You must specify a valid list with "archi", '
                    '"site" and "mobile" properties : '
                    '%s.' % properties_list)
    archi = [prop for prop in properties if prop.startswith('archi=')]
    site = [prop for prop in properties if prop.startswith('site=')]
    mobile = [prop for prop in properties if prop.startswith('mobile=')]

    if len(archi) == 0 or len(site) == 0:
        raise Error('Properties "archi" and "site" are mandatory.')

    archi_prop = archi[0].split('=')[1]
    site_prop = site[0].split('=')[1]
    check_site(site_prop, sites_list)

    properties_dict = {'site': site_prop, 'archi': archi_prop}
    if len(mobile) == 0:
        properties_dict['mobile'] = False
    else:
        mobile_prop = mobile[0].split('=')[1]
        properties_dict['mobile'] = mobile_prop
    return properties_dict


def open_file(file_path):
    """ Open and read a file
    """
    try:
        # exanduser replace '~' with the correct path
        file_d = open(os.path.expanduser(file_path), 'r')
    except IOError as err:
        raise Error(err)
    else:
        file_name = os.path.basename(file_d.name)
        file_data = file_d.read()
        file_d.close()
    return file_name, file_data


def get_current_experiment(api, experiment_id=None):
    """ Return the given experiment or get the currently running one """
    if experiment_id is not None:
        return experiment_id

    # no experiment given, try to find the currently running one
    exps_dict = api.get_running_experiments()
    exp_id = check_experiments_running(exps_dict)
    return exp_id


def check_experiment_firmwares(firmware_path, firmwares):
    """ Check a firmware in experiment list :
        _ try to open/read firmware file
        _ verify that firmwares file cannot have the same name with
        different path

    :param firmware_path: path of firmware file
    :type firmware_path: string
    :param firmwares: experiment firmwares (name and path)
    :type firmwares: dictionnary
    """
    name, body = open_file(firmware_path)

    if firmwares.get(name, firmware_path) != firmware_path:
        raise Error('A firmware with same name %s and different path already '
                    'present' % firmware_path)

    firmwares[name] = firmware_path
    return name, body, firmwares
