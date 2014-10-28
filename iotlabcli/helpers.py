# -*- coding:utf-8 -*-
"""Helpers methods"""

import os
import json


def get_current_experiment(api, experiment_id=None):
    """ Return the given experiment or get the currently running one """
    if experiment_id is not None:
        return experiment_id

    # no experiment given, try to find the currently running one
    exps_dict = api.get_experiments(state='Running')
    exp_id = _check_experiments_running(exps_dict)
    return exp_id


def node_url_sort_key(node_url):
    """
    >>> node_url_sort_key("m3-2.grenoble.iot-lab.info")
    ('grenoble', 'm3', 2)

    >>> node_url_sort_key("3")  # for alias nodes
    3
    """
    if node_url.isdigit():
        return int(node_url)
    _node, site = node_url.split('.')[0:2]
    node_type, num_str = _node.split('-')[0:2]
    return site, node_type, int(num_str)


class FilesDict(dict):
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
     * environment variable IOTLAB_API_URL
     * config file in <HOME_DIR>/.iotlab.api-url
    """
    # try getting url from environment variable
    api_url = os.getenv('IOTLAB_API_URL')
    if api_url is not None:
        return api_url

    # try getting url from config file
    try:
        return read_file('~/.iotlab.api-url').strip()
    except IOError:
        return None


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
    >>> check_experiment_state('')
    'Waiting,Launching,Running,Finishing,Terminated,Error'

    >>> check_experiment_state('invalid,Terminated')
    Traceback (most recent call last):
    ValueError: Invalid experiment states: ['invalid'] should be in \
['Waiting', 'Launching', 'Running', 'Finishing', 'Terminated', 'Error'].
    """
    oar_states = [
        "Waiting", "Launching", "Running", "Finishing", "Terminated", "Error"]
    state_str = state_str or ','.join(oar_states)  # default to all states

    # Check states are all in oar_states
    invalid = set(state_str.split(',')) - set(oar_states)
    if invalid:
        raise ValueError(
            'Invalid experiment states: {state} should be in {states}.'.format(
                state=sorted(list(invalid)), states=oar_states))

    return state_str


def _check_experiments_running(experiments_dict):
    """ Return currently running experiment from experiment dict.
    If None or more than one are found, raise an Error.
    """

    items = experiments_dict["items"]
    if len(items) == 0:
        raise RuntimeError("You don't have any `Running` experiment")

    experiments_id = [exp["id"] for exp in items]
    if len(experiments_id) > 1:
        raise RuntimeError(
            "You have several experiments with state Running. "
            "Use option -i|--id and choose experiment id in this list : %s" %
            experiments_id)

    return experiments_id[0]


def json_dumps(obj):
    """ Dumps data to json """
    class _Encoder(json.JSONEncoder):
        """ Encoder for serialization object python to JSON format """
        def default(self, obj):  # pylint: disable=method-hidden
            return obj.__dict__
    return json.dumps(obj, cls=_Encoder, sort_keys=True, indent=4)
