# -*- coding:utf-8 -*-
"""Helpers methods"""

import os
import json
from argparse import ArgumentTypeError

from iotlabcli import Error

DOMAIN_DNS = 'iot-lab.info'


def write_experiment_archive(exp_id, data):
    """ Write experiment archive contained in 'data' to 'exp_id.tar.gz' """
    try:
        with open('%s.tar.gz' % exp_id, 'wb') as archive:
            archive.write(json.dumps(data, indent=4, sort_keys=True))
    except IOError as err:
        raise Error(
            "Cannot save experiment archive %s.tar.gz: %s" % (exp_id, err))


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


def check_experiments_running(experiments_dict):
    """ Return currently running experiment from experiment dict.
    If None or more than one are found, raise an Error.
    """
    items = experiments_dict["items"]
    if len(items) == 0:
        raise Error("You don't have an experiment with state Running")

    experiments_id = [exp["id"] for exp in items]
    if len(experiments_id) > 1:
        raise Error(
            "You have several experiments with state Running. "
            "Use option -i|--id and choose experiment id in this list : %s" %
            experiments_id)

    return experiments_id[0]


def nodes_list_from_info(site, archi, nodes_str):
    """ Cheks archi, nodes_str format and return a nodes list """
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
    """ Expand short nodes_list '1-5+6+8-12' to a regular nodes list

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


def read_file(file_path):
    """ Open and read a file """
    with open(os.path.expanduser(file_path), 'r') as _fd:  # expand '~'
        return _fd.read()


def get_current_experiment(api, experiment_id):
    """ Return the given experiment or get the currently running one """
    if experiment_id is not None:
        return experiment_id

    # no experiment given, try to find the currently running one
    exps_dict = api.get_experiments(state='Running')
    exp_id = check_experiments_running(exps_dict)
    return exp_id


class FilesDict(dict):
    """ Dictionary to store experiment files.
    We don't want adding two different values for the same key,
    so __setitem__ is overriden to check that"""
    def __init__(self):
        dict.__init__(self)

    def __setitem__(self, key, val):
        """ Prevent adding a new different value to an existing key """
        if key not in self:
            dict.__setitem__(self, key, val)
        elif self[key] != val:
            raise ValueError('Has different values for same key %r' % key)

    def add_firmware(self, firmware_path):
        """ Add a firmwware to the dictionary. If None, do nothing """
        if firmware_path is None:
            return
        self[os.path.basename(firmware_path)] = read_file(firmware_path)
