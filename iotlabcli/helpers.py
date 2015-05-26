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

"""Helpers methods"""

import sys
import os
import json

OAR_STATES = ["Waiting", "toLaunch", "Launching",
              "Running",
              "Finishing",
              "Terminated", "Error"]
ACTIVE_STATES = OAR_STATES[OAR_STATES.index('Running')::-1]


def get_current_experiment(api, experiment_id=None, running_only=True):
    """ Return the given experiment or get the currently running one.
    If running_only is false, try to return the experiment the most advanced
    Waiting < toLaunch < Launching < Running """
    if experiment_id is not None:
        return experiment_id

    if running_only:
        # no experiment given, try to find the currently running one
        states = ['Running']
    else:
        # or experiment that are starting (from waiting to Running')
        states = ACTIVE_STATES

    exp_by_states = exps_by_states_dict(api, states)

    exp_id = get_current_exp(exp_by_states, states)

    return exp_id


def exps_by_states_dict(api, states):
    """ Return current experiment in `states` as a per state dict """

    # exps == [{'state': 'Waiting', 'id': 10134, ...},
    #          {'state': 'Waiting', 'id': 10135, ...},
    #          {'state': 'Running', 'id': 10130, ...}]
    exps = api.get_experiments(state=','.join(states))['items']

    exp_states_d = {}
    for exp in exps:
        exp_states_d.setdefault(str(exp['state']), []).append(exp['id'])

    return exp_states_d  # {'Waiting': [10134, 10135], 'Running': [10130]}


def get_current_exp(exp_by_states, states):
    """ Current experiment is the first state in `states` where there is only
    one experiment in `exp_by_states`.
    :raises: ValueError if there is no experiment or if there are multiple
             experiments of the same state

    >>> get_current_exp({'Running': [123]}, ['Running'])
    123

    >>> get_current_exp(\
        {'Waiting': [10134, 10135], 'Launching': [10130]}, ACTIVE_STATES)
    10130

    >>> get_current_exp({'Running': [123, 234]}, ['Running'])
    Traceback (most recent call last):
    ValueError: You have several experiments with state 'Running'
    Use option -i|--id and choose experiment id in: {'Running': [123, 234]}

    >>> get_current_exp({'Waiting': [123], 'Launching': [121, 122]}, \
        ACTIVE_STATES)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ValueError: You have several experiments with state 'Running, ..., Waiting'
    Use option -i|--id and choose experiment id in: {...}

    >>> get_current_exp({}, ACTIVE_STATES)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ValueError: You have no 'Running, ..., Waiting' experiment

    """
    states_str = ', '.join(states)

    for state in states:  # keep order of states
        exps = exp_by_states.get(state, [])
        if len(exps) == 1:
            return exps[0]
        elif len(exps) == 0:
            continue
        raise ValueError(
            "You have several experiments with state {0!r}\n"
            "Use option -i|--id and choose experiment id in: {1}".format(
                states_str, exp_by_states))
    raise ValueError("You have no {0!r} experiment".format(states_str))


def node_url_sort_key(node_url):
    """
    >>> node_url_sort_key("m3-2.grenoble.iot-lab.info")
    ('grenoble', 'm3', 2)

    >>> node_url_sort_key("3")  # for alias nodes
    3

    >>> node_url_sort_key("a8-2.grenoble.iot-lab.info")
    ('grenoble', 'a8', 2)
    >>> node_url_sort_key("node-a8-2.grenoble.iot-lab.info")
    ('grenoble', 'node-a8', 2)

    # Also support incomplete urls
    >>> node_url_sort_key("m3-2")
    ('', 'm3', 2)
    >>> node_url_sort_key("node-a8-2")
    ('', 'node-a8', 2)

    """
    if node_url.isdigit():
        return int(node_url)
    _node, _, domain = node_url.partition('.')
    site = domain.split('.')[0]

    node_type, num_str = _node.rsplit('-', 1)
    return site, node_type, int(num_str)


class FilesDict(dict):  # pylint: disable=too-few-public-methods
    """ Dictionary to store experiment files.
    We don't want adding two different values for the same key,
    so __setitem__ is overriden to check that

    >>> file_dict = FilesDict()

    # can re-add same value
    >>> file_dict['test'] = 'value'
    >>> file_dict['test'] = 'value'

    >>> file_dict['test2'] = 'value'
    >>> file_dict['test3'] = 'value3'
    >>> file_dict == {'test': 'value', 'test3': 'value3', 'test2': 'value'}
    True

    # cannot add a new value to an existing key

    >>> file_dict['test'] = 'a_new_value'
    Traceback (most recent call last):
    ValueError: Has different values for same key 'test'
    """
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
        self[os.path.basename(firmware_path)] = read_file(firmware_path, 'b')


def read_custom_api_url():
    """ Return the customized api url from:
     * config file in <HOME_DIR>/.iotlab.api-url
     * or environment variable IOTLAB_API_URL
    """
    try:
        # try getting url from config file
        api_url = read_file('~/.iotlab.api-url').strip()
    except IOError:
        # try getting url from environment variable, None if undefined
        api_url = os.getenv('IOTLAB_API_URL')

    if api_url:
        sys.stderr.write("Using custom api_url: {0}\n".format(api_url))
    return api_url


def read_file(file_path, opt=''):
    """ Open and read a file """
    with open(os.path.expanduser(file_path), 'r' + opt) as _fd:  # expand '~'
        return _fd.read()


def check_experiment_state(state_str=None):
    """ Check that given states are valid if None given, return all states

    >>> check_experiment_state('Running')
    'Running'
    >>> check_experiment_state('Terminated,Running')
    'Terminated,Running'
    >>> check_experiment_state('')  # doctest: +ELLIPSIS
    'Waiting,...,Error'

    >>> check_experiment_state('invalid,Terminated')  # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ValueError: Invalid experiment states: ['invalid'] should be in [...].
    """
    state_str = state_str or ','.join(OAR_STATES)  # default to all states

    # Check states are all in OAR_STATES
    invalid = set(state_str.split(',')) - set(OAR_STATES)
    if invalid:
        raise ValueError(
            'Invalid experiment states: {state} should be in {states}.'.format(
                state=sorted(list(invalid)), states=OAR_STATES))

    return state_str


def json_dumps(obj):
    """ Dumps data to json """
    class _Encoder(json.JSONEncoder):  # pylint: disable=too-few-public-methods
        """ Encoder for serialization object python to JSON format """
        def default(self, obj):  # pylint: disable=method-hidden
            return obj.__dict__
    return json.dumps(obj, cls=_Encoder, sort_keys=True, indent=4)
