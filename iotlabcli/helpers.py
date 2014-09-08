# -*- coding:utf-8 -*-
"""Helpers methods"""

import getpass
import os
import base64
import json
from argparse import ArgumentTypeError

from iotlabcli import Error
from iotlabcli import experiment
from iotlabcli import parser_common

DOMAIN_DNS = 'iot-lab.info'


def password_prompt():
    """ password prompt when command-line option username (e.g. -u or --user)
    is used without password

    :returns password
    """
    pprompt = lambda: (getpass.getpass(), getpass.getpass('Retype password: '))
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
        raise Error("username:password required: %s:%s" % username, password)

    home_directory = os.getenv('USERPROFILE') or os.getenv('HOME')
    try:
        with open('%s/%s' % (home_directory, '.iotlabrc'), 'wb') as pass_file:
            pass_file.write('%s:%s' % (username, base64.b64encode(password)))
    except IOError as err:
        raise Error("Cannot create password file in home directory: %s" % err)


def read_password_file():
    """ Try to read password file (.iotlabrc) in user home directory when
    command-line option username and password are not used. If password
    file exist whe return username and password for basic auth http
    authentication

    """
    home_directory = os.getenv('USERPROFILE') or os.getenv('HOME')
    path_file = '%s/%s' % (home_directory, '.iotlabrc')

    if not os.path.exists(path_file):
        return None, None
    try:
        with open(path_file, 'rb') as password_file:
            try:
                user, enc_passwd = (password_file.readline()).split(':')
            except ValueError:
                raise Error('Bad password file format: %r' % path_file)
            return user, base64.b64decode(enc_passwd)
    except IOError as err:
        raise Error('Cannot open password file in home directory: %s' % err)


def write_experiment_archive(experiment_id, data):
    try:
        archive_file = open('%s.tar.gz' % experiment_id, 'wb')
    except IOError:
        raise Error("Unable to save experiment archive file: \
            %s.tar.gz." % experiment_id)
    else:
        archive_file.write(json.dumps(data, indent=4, sort_keys=True))
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


def check_experiment_state(state_str=None):
    """ Check that given states are valid if None given, return all states

    >>> check_experiment_state('Running')
    'Running'
    >>> check_experiment_state('Terminated,Running')
    'Terminated,Running'
    >>> check_experiment_state(None)
    'Terminated,Waiting,Launching,Finishing,Running,Error'

    >>> check_experiment_state('Invalid')
    Traceback (most recent call last):
    Error: "The experiment filter state 'Invalid' is invalid."
    """
    oar_state = ["Terminated", "Waiting", "Launching", "Finishing",
                 "Running", "Error"]

    if state_str is None:
        return ','.join(oar_state)

    for state in state_str.split(','):
        if state not in oar_state:
            raise Error('The experiment filter state %r is invalid.' % state)
    return state_str


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


def extract_firmware_nodes_list(param_list):

    # list in experiment-cli (alias or physical)

    if param_list[0].isdigit():  # alias selection
        # extract parameters
        nb_nodes, properties_str = param_list[0:2]
        del param_list[0:2]

        # parse parameters
        properties = get_properties(properties_str)
        nodes = experiment.AliasNodes(int(nb_nodes), properties)
    else:  # physical selection
        # extract parameters
        site, archi, nodes_str = param_list[0:3]
        del param_list[0:3]

        # parse parameters
        nodes = nodes_list_from_info(site, archi, nodes_str)
    return nodes


def extract_non_empty_val(param_list):
    """ Safe extract value from param_list.
    It removes item from param_list.

    :returns: value or None if value was '' or not present

    >>> param = ['value', '', 'other_stuff']
    >>> extract_non_empty_val(param)  # valid value
    'value'
    >>> extract_non_empty_val(param)  # empty string
    >>> extract_non_empty_val([])     # empty list

    >>> print param  # values have been removed
    ['other_stuff']
    """
    if param_list:
        value = param_list.pop(0)
        if value != '':
            return value
    return None


def firmwares_from_string(firmware_str):
    """
    Open firmwares given in parameter string

    :param firmware_str: firmware_1_path,../firmware_2_path,~/firmware_3_path
    :returns: A list of firmware dict where firmware dict has 'name' and 'body'
    """
    return [open_firmware(path) for path in firmware_str.split(',')]


def add_to_dict_uniq(val_dict, key, value):
    """ Add (key, val) to _dict files
        * verify that file cannot have the same name with different content
    :param val_dict: dict where to add key, value
    :param key: key to use
    :param value: value to use
    """
    if key not in val_dict:
        val_dict[key] = value

    elif val_dict[key] != value:
        # same key, but different value => ERROR
        raise Error('Found two different files with same key' % key)


def open_firmware(firmware_path):
    if firmware_path is None:
        return None
    name, body = open_file(firmware_path)
    return {'name': name, 'body': body}


def experiment_dict(nodes, firmware_dict=None, profile_name=None):

    if isinstance(nodes, experiment.AliasNodes):
        exp_type = 'alias'
    else:
        exp_type = 'physical'

    exp_dict = {
        'type': exp_type,
        'nodes': nodes,
        'firmware': firmware_dict,
        'profile': profile_name,
    }
    return exp_dict


def experiment_dict_from_str(exp_str):
    try:
        param_list = exp_str.split(',')
        nodes = extract_firmware_nodes_list(param_list)
        firmware = extract_non_empty_val(param_list)
        profile_name = extract_non_empty_val(param_list)
        if param_list:
            raise ValueError  # two many values in list
        firmware_dict = open_firmware(firmware)

        return experiment_dict(nodes, firmware_dict, profile_name)
    except ValueError:
        pass
    raise Error('Invalid argument number in experiment list %s' % exp_str)


def nodes_list_from_str(nodes_list_str):
    """
    nodes_list_str format: site_name,archi,nodeid_list

    ex: nodes_list_str == 'grenoble,m3,1-34+72'
    """
    # 'grenoble,m3,1-34+72' -> ['grenoble', 'm3', '1-34+72']
    site, archi, nodes_str = get_command_list(nodes_list_str)
    return nodes_list_from_info(site, archi, nodes_str)


def nodes_list_from_info(site, archi, nodes_str):
    """ Return nodes list from site, archi, nodes_str where nodes_str format is
    1-34+72+12-14
    """
    sites_list = parser_common.Singleton().sites()
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


def get_property(properties, key):
    """
    >>> get_property(['archi=val_1', 'site=grenoble', 'archi=val_2'], 'site')
    'grenoble'

    >>> get_property(['archi=val_1'], 'site')  # None when absent

    # value should appear only once
    >>> get_property(['archi=1', 'archi=2'], 'archi')
    Traceback (most recent call last):
    ValueError: Property 'archi' should appear only once in \
['archi=1', 'archi=2']

    >>> get_property(['archi='], 'archi')  # There should be a value
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


def get_properties(properties_list):

    properties = properties_list.split('+')
    try:
        archi = get_property(properties, 'archi')
        site = get_property(properties, 'site')
        mobile = get_property(properties, 'mobile')
    except ValueError as err:
        raise ArgumentTypeError(err)

    # check extracted values
    if archi is None or site is None:
        raise ArgumentTypeError('Properties "archi" and "site" are mandatory.')

    if len(properties) > (2 if mobile is None else 3):
        # Refuse unkown properties
        raise ArgumentTypeError(
            "Invalid property in %r " % properties_list +
            "Allowed values are ['archi', 'site', 'mobile']")

    sites_list = parser_common.Singleton().sites()
    check_site(site, sites_list)

    properties_dict = {
        'site': site,
        'archi': archi,
        'mobile': mobile or False,  # False if None
    }
    return properties_dict


def open_file(file_path):
    """ Open and read a file """
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
    exps_dict = api.get_experiments(state='Running')
    exp_id = check_experiments_running(exps_dict)
    return exp_id
