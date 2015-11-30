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

""" Implement the 'experiment' requests """

from os.path import basename
import re
import json
import time
from iotlabcli import helpers

# static name for experiment file : rename by server-rest
EXP_FILENAME = 'new_exp.json'


def submit_experiment(api, name, duration,  # pylint:disable=too-many-arguments
                      resources, start_time=None, print_json=False):
    """ Submit user experiment with JSON Encoder serialization object
    Experiment and firmware(s). If submission is accepted by scheduler OAR
    we print JSONObject response with id submission.

    :param api: API Rest api object
    :param name: experiment name
    :param duration: experiment duration in seconds
    :param resources: list of 'exp_resources' which
    :param print_json: select if experiment should be printed as json instead
        of submitted
    """

    assert resources, 'Empty resources: %r' % resources
    experiment = _Experiment(name, duration, start_time)

    exp_files = helpers.FilesDict()
    for res_dict in resources:
        experiment.add_exp_resources(res_dict)
        exp_files.add_firmware(res_dict.get('firmware', None))  # firmware

    if print_json:  # output experiment description
        return experiment
    # submit experiment
    exp_files[EXP_FILENAME] = helpers.json_dumps(experiment)  # exp description
    return api.submit_experiment(exp_files)


def stop_experiment(api, exp_id):
    """ Stop user experiment submission.

    :param api: API Rest api object
    :param exp_id: scheduler OAR id submission
    """
    return api.stop_experiment(exp_id)


def get_experiments_list(api, state, limit, offset):
    """ Get the experiment list with the specific restriction:
    :param state: State of the experiment
    :param limit: maximum number of outputs
    :param offset: offset of experiments to start at
    """
    state = helpers.check_experiment_state(state)
    return api.get_experiments(state, limit, offset)


def get_experiment(api, exp_id, option=''):
    """ Get user experiment's description :

    :param api: API Rest api object
    :param exp_id: experiment id
    :param option: Restrict to some values
            * '':          experiment submission
            * 'resources': resources list
            * 'id':        resources id list: (1-34+72 format)
            * 'state':     experiment state
            * 'data':      experiment tar.gz with description and firmwares
            * 'start':     expected start time
    """
    result = api.get_experiment_info(exp_id, option)
    if option == 'data':
        _write_experiment_archive(exp_id, result)
        result = 'Written'

    return result


def load_experiment(api, exp_desc_path, firmware_list=()):
    """ Load and submit user experiment description with firmware(s)

    Firmwares required for experiment will be loaded from current directory,
    except if their path is given in firmware_list

    :param api: API Rest api object
    :param exp_desc_path: path to experiment json description file
    :param firmware_list: list of firmware path
    """

    # 1. load experiment description
    exp_dict = json.loads(helpers.read_file(exp_desc_path))
    exp_files = helpers.FilesDict()
    # 2. Add experiment description
    exp_files[EXP_FILENAME] = helpers.json_dumps(exp_dict)

    # 3. Add firmwares files to the experiment files using
    #    firmware_list and experiment firmwareassociations

    # extract firmwares names
    _fw_association = exp_dict['firmwareassociations'] or []
    firmwares = set([assoc['firmwarename'] for assoc in _fw_association])

    try:
        # replace firwmare name by firmware_path from firmware_list
        for _fw_path in firmware_list:
            firmwares.remove(basename(_fw_path))
            firmwares.add(_fw_path)
    except KeyError as err:
        raise ValueError("Firmware {!s} is not in experiment: {}".format(
            err, exp_desc_path))
    else:
        # Add all firmwares to the experiment files
        for _fw_path in firmwares:
            exp_files.add_firmware(_fw_path)
    return api.submit_experiment(exp_files)


def info_experiment(api, list_id=False, site=None):
    """ Print testbed information for user experiment submission:
    * resources description
    * resources description in short mode

    :param api: API Rest api object
    :param list_id: By default, return full nodes list, if list_id
        return output in exp_list format '3-12+42'
    :param site: Restrict informations collection on site
    """
    return api.get_resources(list_id, site)


def wait_experiment(api, exp_id, states='Running',
                    step=5, timeout=float('+inf')):
    """ Wait for the experiment to be in `states`
    and also Terminated or Error

    :param api: API Rest api object
    :param exp_id: scheduler OAR id submission
    :param states: Comma separated string of states to wait for
    :param step: time to wait between each server check
    :param timeout: timeout if wait takes too long

    """

    start_time = time.time()
    end_time = start_time + timeout

    full_states = helpers.check_experiment_state(states + ',Terminated,Error')

    while time.time() < end_time:  # timeout
        state = get_experiment(api, exp_id, 'state')['state']
        if state not in full_states:
            time.sleep(step)
            continue
        if state in states:  # state was awaited
            return state
        # non wanted state, usually 'Terminated or Error'
        raise RuntimeError(
            "Experiment {0} already in state {1!r}".format(exp_id, str(state)))

    raise RuntimeError("Timeout reached")


def exp_resources(nodes, firmware_path=None, profile_name=None,
                  **associations):
    """Create an experiment resources dict.

    :param nodes: a list of nodes url or a AliasNodes object
        * ['m3-1.grenoble.iot-lab.info', 'wsn430-2.strasbourg.iot-lab.info']
        * AliasNodes(5, 'grenoble', 'm3:at86rf321', mobile=False)
    :param firmware_path: Firmware association
    :param profile_name: Profile association
    :param **associations: Other name associations
    """

    if isinstance(nodes, AliasNodes):
        exp_type = 'alias'
    else:
        exp_type = 'physical'

    exp_dict = {
        'type': exp_type,
        'nodes': nodes,
        'firmware': firmware_path,
        'profile': profile_name,
        'associations': associations,
    }

    return exp_dict


class AliasNodes(object):  # pylint: disable=too-few-public-methods
    """An AliasNodes class

    >>> AliasNodes(5, 'grenoble', 'm3:at86rf231', False)
    AliasNodes(5, 'grenoble', 'm3:at86rf231', False, _alias='1')
    >>> save = AliasNodes(2, 'strasbourg', 'wsn430:cc1101', True)
    >>> save
    AliasNodes(2, 'strasbourg', 'wsn430:cc1101', True, _alias='2')

    >>> save == AliasNodes(2, 'strasbourg', 'wsn430:cc1101', True, _alias='2')
    True

    >>> AliasNodes(2, 'strasbourg', 'wsn430:cc1100', True)
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ValueError: 'wsn430:cc1100' not in [...]

    """
    _alias = 0  # static count of current alias number
    ARCHIS = ['wsn430:cc1101', 'wsn430:cc2420',
              'm3:at86rf231', 'a8:at86rf231',
              'des:wifi-cc1100', 'custom:.*']
    ARCHI_RE = re.compile(r'|'.join(('(%s)' % archi for archi in ARCHIS)))

    def __init__(self, nbnodes, site, archi, mobile=False, _alias=None):
        """
        {
            "alias":"1",
            "nbnodes":1,
            "properties":{
                "archi":"wsn430:cc2420",
                "site":"devlille",
                "mobile":False
            }
        }
        """
        if not self._valid_archi(archi):
            raise ValueError("%r not in %r" % (archi, self.ARCHIS))

        self.alias = self._alias_uid(_alias)
        self.nbnodes = nbnodes
        self.properties = {
            "archi": archi,
            "site": site,
            "mobile": mobile,
        }

    @classmethod
    def _alias_uid(cls, alias=None):
        """Return an unique uid string.

        if alias is given, return it as a String
        """
        if alias is None:
            cls._alias += 1
            alias = cls._alias
        return str(alias)

    @classmethod
    def _valid_archi(cls, archi):
        """Tests if archi is valid.

        >>> AliasNodes._valid_archi('wsn430:cc1101')
        True

        >>> AliasNodes._valid_archi('des:wifi-cc1100')
        True

        >>> AliasNodes._valid_archi('custom:m3:cc1101')
        True

        >>> AliasNodes._valid_archi('custom:leonardo:')
        True

        >>> AliasNodes._valid_archi('wsn430:cc1100')
        False

        >>> AliasNodes._valid_archi('des')
        False
        """
        return bool(cls.ARCHI_RE.match(archi))

    def __repr__(self):  # pragma: no cover
        return 'AliasNodes(%r, %r, %r, %r, _alias=%r)' % (
            self.nbnodes, self.properties['site'], self.properties['archi'],
            self.properties['mobile'], self.alias)

    def __eq__(self, other):  # pragma: no cover
        return self.__dict__ == other.__dict__


# # # # # # # # # #
# Private methods #
# # # # # # # # # #


class Association(object):
    """Association class value->Nodes.

    >>> first = Association.for_type('test')('name', ['m3-1'])
    >>> second = Association.for_type('test')('name', ['m3-2', 'm3-3'])

    # Comparing only names to detect in a list
    >>> first == second
    True
    >>> second.extend(first)
    >>> print(second.nodes)
    ['m3-1', 'm3-2', 'm3-3']

    # Verify type when comparing
    >>> first == {'name': 'name', 'nodes':['m3-1']}
    False
    """
    ASSOCTYPE = ''
    NODES_KEY = staticmethod(helpers.node_url_sort_key)

    def __init__(self, value, nodes):
        assert self.ASSOCTYPE, "VirtualClass, create real with 'for_type'"
        setattr(self, self.valuename(), value)
        self.nodes = sorted(nodes, key=self.NODES_KEY)

    @classmethod
    def valuename(cls):
        """Return value attribute name."""
        return '{0}name'.format(cls.ASSOCTYPE)

    @property
    def value(self):
        """Return value."""
        return getattr(self, self.valuename())

    def extend(self, association):
        """Add nodes to the association.

        Remove duplicates and sort them for readability and testability.
        """
        # Same assoctype and name
        assert self == association
        self.nodes = sorted(list(set(self.nodes + association.nodes)),
                            key=self.NODES_KEY)

    def __eq__(self, other):
        return (isinstance(other, Association) and
                self.ASSOCTYPE == other.ASSOCTYPE and
                self.value == other.value)

    def add_to_list_sorted(self, assoc_list):
        """Add current nodes association to assoclist.

        If the association already exist, update with current nodes.
        Else insert current association in assoclist.
        """
        # Add association in place
        try:
            # Append to existing one
            # get same class object
            existing = assoc_list[assoc_list.index(self)]
            existing.extend(self)
        except ValueError:  # Not present
            # Insert new one sorted
            assoc_list.append(self)
            assoc_list.sort(key=lambda x: x.value)

    @classmethod
    def for_type(cls, assoctype):
        """Create association class for assoctype."""
        class _NamedAssociation(cls):
            """NamedAssociations class->Nodes."""
            ASSOCTYPE = assoctype  # overrides
            __name__ = '{0}Association'.format(ASSOCTYPE.title())
        return _NamedAssociation


class _Experiment(object):  # pylint:disable=too-many-instance-attributes
    """ Class describing an experiment """

    ASSOCATTR_FMT = '{0}associations'

    def __init__(self, name, duration, start_time=None):
        self.duration = duration
        self.reservation = start_time
        self.name = name

        self.type = None
        self.nodes = []
        self.firmwareassociations = None
        self.profileassociations = None
        self.associations = None

    def _set_type(self, exp_type):
        """ Set current experiment type.
        If type was already set and is different ValueError is raised
        """
        if self.type is not None and self.type != exp_type:
            raise ValueError(
                "Invalid experiment, should be only physical or only alias")
        self.type = exp_type

    def add_exp_resources(self, exp_dict):
        """ Add 'exp_resources' to current experiment
        It will update node type, nodes, firmware and profile associations
        """

        # register nodes in experiment
        nodes = exp_dict['nodes']
        {
            'physical': self.set_physical_nodes,
            'alias': self.set_alias_nodes,
        }[exp_dict['type']](nodes)

        # register firmware
        if exp_dict['firmware'] is not None:
            firmware_name = basename(exp_dict['firmware'])
            self.add_association('firmware', firmware_name, nodes)

        # register profile, may be None
        self.add_association('profile', exp_dict['profile'], nodes)

        # Add other associations
        associations = exp_dict.get('associations', {})
        for assoctype, assoc in associations.items():
            self.add_association(assoctype, assoc, nodes, optional=True)

    def set_physical_nodes(self, nodes_list):
        """Set physical nodes list """
        self._set_type('physical')

        # Check that nodes are not already present
        _intersect = list(set(self.nodes) & set(nodes_list))
        if _intersect:
            raise ValueError("Nodes specified multiple times {0}".format(
                _intersect))

        self.nodes.extend(nodes_list)
        # Keep unique values and sorted
        self.nodes = sorted(list(set(self.nodes)),
                            key=helpers.node_url_sort_key)

    def set_alias_nodes(self, alias_nodes):
        """Set alias nodes list """
        self._set_type('alias')
        self.nodes.append(alias_nodes)

    def add_association(self, assoctype, name, nodes, optional=False):
        """Add association."""
        if name is None:
            return

        # use alias number for AliasNodes
        assoc_nodes = [nodes.alias] if self.type == 'alias' else nodes

        # Create association
        assoc = Association.for_type(assoctype)(name, assoc_nodes)

        # Add association to assocs_list
        assocs_list = self._association_list(assoctype, optional)
        assoc.add_to_list_sorted(assocs_list)

    def _association_list(self, assoctype, optional=False):
        """Set and return association list for `assoctype`.

        If not optional, set list as attribute 'self.{assoctype}association'
        else set list in 'self.associations[assoctype]'
        """

        if not optional:
            # Store list as attribute '{assoctype}association'
            assocattr = self.ASSOCATTR_FMT.format(assoctype)
            associations_list = self.setattr_if_none(assocattr, [])
        else:
            # Store list in 'associations[assoctype]' dict
            associations_dict = self.setattr_if_none('associations', {})
            associations_list = associations_dict.setdefault(assoctype, [])

        return associations_list

    def setattr_if_none(self, name, default):
        """Set attribute as `default` if None

        :returns: attribute value after update
        """
        # Set default if None
        if getattr(self, name) is None:
            setattr(self, name, default)

        return getattr(self, name)


def _write_experiment_archive(exp_id, data):
    """ Write experiment archive contained in 'data' to 'exp_id.tar.gz' """
    with open('%s.tar.gz' % exp_id, 'wb') as archive:
        archive.write(data)
