# -*- coding:utf-8 -*-
"""Helpers methods"""

import getpass
import os
import base64
import json
import argparse

from iotlabcli import Error

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


def read_api_url_file():
    home_directory = os.getenv('USERPROFILE') or os.getenv('HOME')
    api_url_filename = os.path.join(home_directory, ".iotlab.api-url")
    try:
        return open(api_url_filename).readline().strip()
    except IOError:
        return None


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
        raise argparse.ArgumentTypeError(
            "invalid period choice : %s (choose from 1 .. 65535)" % (value,))
    return value


def check_radio_num_per_channel(num):
    value = int(num)
    if value not in range(1, 256):
        raise argparse.ArgumentTypeError(
            "invalid period choice : %s (choose from 1 .. 255)" % (value,))
    return value


def check_radio_channels(channel):
    value = int(channel)
    if value not in range(11, 27):
        raise argparse.ArgumentTypeError(
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


def check_site(site_name, sites_json):
    for site in sites_json["items"]:
        if site["site"] == site_name:
            return site_name
    raise Error("The site name %s doesn't exist" % site_name)


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


def check_command_list(nodes_list):
    """
    >>> check_command_list('grenoble,m3,0-5+6+8')
    ['grenoble', 'm3', '0-5+6+8']

    >>> check_command_list('grenoble,m3')
    Traceback (most recent call last):
    Error: "Invalid number of argument in nodes list: 'grenoble,m3'"

    """
    param_list = nodes_list.split(',')
    if len(param_list) == 3:
        return param_list
    raise Error('Invalid number of argument in nodes list: %r' % nodes_list)


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


def check_archi(archi):
    """
    >>> [check_archi(archi) for archi in ['wsn430', 'm3', 'a8']]
    ['wsn430', 'm3', 'a8']

    >>> check_archi('msp430')
    Traceback (most recent call last):
    Error: "Invalid not architecture: 'msp430' not in ['wsn430', 'm3', 'a8']"

    """
    archi_list = ['wsn430', 'm3', 'a8']
    if archi in archi_list:
        return archi
    raise Error("Invalid not architecture: %r not in %s" % (archi, archi_list))


def check_nodes_list(site, archi, nodes_list):
    physical_nodes = []
    for nodes in nodes_list.split('+'):
        node = nodes.split('-')
        if len(node) == 1 and node[0].isdigit():
            # 42
            physical_node = "%s-%s.%s.%s" % (archi,
                                             node[0],
                                             site,
                                             DOMAIN_DNS)
            physical_nodes.append(physical_node)
        elif (len(node) == 2 and (node[0].isdigit() and node[1].isdigit())
              and (int(node[0]) < int(node[1]))):
            # 42-69
            first = int(node[0])
            last = int(node[1])
            for node_id in range(first, last + 1):
                physical_node = "%s-%s.%s.%s" % (archi,
                                                 node_id,
                                                 site,
                                                 DOMAIN_DNS)
                physical_nodes.append(physical_node)
        else:
            # invalid: 6-3 or 6-7-8
            raise Error('Invalid nodes list: %s ([0-9+-])' % nodes_list)
    return physical_nodes


def check_properties(properties_list, sites_json):
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
    check_site(site_prop, sites_json)

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
