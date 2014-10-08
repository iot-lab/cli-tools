# -*- coding:utf-8 -*-
"""Helpers methods"""

import os
import itertools
DOMAIN_DNS = 'iot-lab.info'


def get_current_experiment(api, experiment_id=None):
    """ Return the given experiment or get the currently running one """
    if experiment_id is not None:
        return experiment_id

    # no experiment given, try to find the currently running one
    exps_dict = api.get_experiments(state='Running')
    exp_id = _check_experiments_running(exps_dict)
    return exp_id


def nodes_list_from_info(site, archi, nodes_str):
    """ Cheks archi, nodes_str format and return nodes list

    >>> nodes_list_from_info('grenoble', 'm3', '1-4+6+7-8')
    ['m3-1.grenoble.iot-lab.info', 'm3-2.grenoble.iot-lab.info', \
'm3-3.grenoble.iot-lab.info', 'm3-4.grenoble.iot-lab.info', \
'm3-6.grenoble.iot-lab.info', 'm3-7.grenoble.iot-lab.info', \
'm3-8.grenoble.iot-lab.info']

    >>> nodes_list_from_info('grenoble', 'm3', '1-4-5')
    Traceback (most recent call last):
    ValueError: Invalid nodes list: 1-4-5 ([0-9+-])

    >>> nodes_list_from_info('grenoble', 'wsn430', 'a-b')
    Traceback (most recent call last):
    ValueError: Invalid nodes list: a-b ([0-9+-])

    >>> nodes_list_from_info('grenoble', 'inval_arch', '1-2')
    Traceback (most recent call last):
    ValueError: Invalid node archi: 'inval_arch' not in ['wsn430', 'm3', 'a8']
    """

    _check_archi(archi)
    nodes_list = _get_nodes_list(site, archi, nodes_str)
    return nodes_list


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


def _check_archi(archi):
    """ Check that archi is valid
    >>> [_check_archi(archi) for archi in ['wsn430', 'm3', 'a8']]
    [None, None, None]

    >>> _check_archi('msp430')
    Traceback (most recent call last):
    ValueError: Invalid node archi: 'msp430' not in ['wsn430', 'm3', 'a8']

    """

    archi_list = ['wsn430', 'm3', 'a8']
    if archi in archi_list:
        return  # valid archi
    raise ValueError("Invalid node archi: %r not in %s" % (archi, archi_list))


def _expand_minus_str(minus_nodes_str):
    """ Expand a '1-5' or '6' string to a list on integer
    :raises: ValueError on invalid values
    """
    minus_node = minus_nodes_str.split('-')
    if len(minus_node) == 1:
        # ['6']
        return [int(minus_node[0])]
    else:
        # ['1', '4'] or ['7', '8']
        first, last = minus_node
        nodes_range = range(int(first), int(last) + 1)
        # first >= last
        if len(nodes_range) <= 1:
            raise ValueError

        # Add nodes range
        return nodes_range


def _expand_short_nodes_list(nodes_str):
    """ Expand short nodes_list '1-5+6+8-12' to a regular nodes list

    >>> _expand_short_nodes_list('1-4+6+7-8')
    [1, 2, 3, 4, 6, 7, 8]

    >>> _expand_short_nodes_list('1-4-5')
    Traceback (most recent call last):
    ValueError: Invalid nodes list: 1-4-5 ([0-9+-])

    >>> _expand_short_nodes_list('3-3')
    Traceback (most recent call last):
    ValueError: Invalid nodes list: 3-3 ([0-9+-])

    >>> _expand_short_nodes_list('3-2')
    Traceback (most recent call last):
    ValueError: Invalid nodes list: 3-2 ([0-9+-])

    >>> _expand_short_nodes_list('a-b')
    Traceback (most recent call last):
    ValueError: Invalid nodes list: a-b ([0-9+-])
    """

    try:
        # '1-4+6+8-8'
        nodes_ll = [_expand_minus_str(minus_nodes_str) for minus_nodes_str in
                    nodes_str.split('+')]
        # [[1, 2, 3], [6], [12]]
        return list(itertools.chain.from_iterable(nodes_ll))  # flatten
    except ValueError:
        # invalid: 6-3 or 6-7-8 or non int values
        raise ValueError('Invalid nodes list: %s ([0-9+-])' % nodes_str)


def _get_nodes_list(site, archi, nodes_list):
    """ Expand short nodes_list 'site', 'archi', '1-5+6+8-12'
    to a regular nodes list
    """

    nodes_num_list = _expand_short_nodes_list(nodes_list)

    node_fmt = '{archi}-%u.{site}.{domain}'.format(
        archi=archi, site=site, domain=DOMAIN_DNS)
    nodes = [node_fmt % num for num in nodes_num_list]

    return nodes
