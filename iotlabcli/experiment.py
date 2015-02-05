# -*- coding:utf-8 -*-
""" Implement the 'experiment' requests """

from os.path import basename
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


def exp_resources(nodes, firmware_path=None, profile_name=None):
    """ Create an experiment dict

    :param nodes: a list of nodes url or a AliasNodes object
        * ['m3-1.grenoble.iot-lab.info', 'wsn430-2.strasbourg.iot-lab.info']
        * AliasNodes(5, 'grenoble', 'm3:at86rf321', mobile=False)
    :param firmware_path: Firmware associated
    :param profile_name: Name of the profile associated

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
    Traceback (most recent call last):
    ValueError: 'wsn430:cc1100' not in ['wsn430:cc1101', 'wsn430:cc2420', \
'm3:at86rf231', 'a8:at86rf231']

    """
    _alias = 0  # static count of current alias number
    _archis = ['wsn430:cc1101', 'wsn430:cc2420',
               'm3:at86rf231', 'a8:at86rf231']

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
        if archi not in self._archis:
            raise ValueError("%r not in %r" % (archi, self._archis))
        if _alias is None:
            AliasNodes._alias += 1
            _alias = str(AliasNodes._alias)
        self.alias = _alias
        self.nbnodes = nbnodes
        self.properties = {
            "archi": archi,
            "site": site,
            "mobile": mobile,
        }

    def __repr__(self):  # pragma: no cover
        return 'AliasNodes(%r, %r, %r, %r, _alias=%r)' % (
            self.nbnodes, self.properties['site'], self.properties['archi'],
            self.properties['mobile'], self.alias)

    def __eq__(self, other):  # pragma: no cover
        return self.__dict__ == other.__dict__


#
# Private methods
#


class _FirmwareAssociations(object):  # pylint: disable=too-few-public-methods
    """A _FirmwareAssociations class

    >>> fw = _FirmwareAssociations('name', ['3'])
    >>> fw == _FirmwareAssociations('name', ['bla bla bla', 'test test'])
    True
    >>> fw == {'firmwarename': 'name', 'nodes':['3']}
    False
    """
    def __init__(self, firmwarename, nodes):
        self.firmwarename = firmwarename
        self.nodes = nodes

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.firmwarename == other.firmwarename)


class _ProfileAssociations(object):  # pylint: disable=too-few-public-methods
    """A _ProfileAssociations class

    # coverage
    >>> pr = _ProfileAssociations('name', ['3'])
    >>> pr == _ProfileAssociations('name', ['bla bla bla', 'test test'])
    True
    >>> pr == {'profilename': 'name', 'nodes':['3']}
    False

    """
    def __init__(self, profilename, nodes):
        self.profilename = profilename
        self.nodes = nodes

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.profilename == other.profilename)


class _Experiment(object):
    """ Class describing an experiment """
    def __init__(self, name, duration, start_time=None):
        self.duration = duration
        self.reservation = start_time
        self.name = name

        self.type = None
        self.nodes = []
        self.firmwareassociations = None
        self.profileassociations = None

    def _set_type(self, exp_type):
        """ Set current experiment type.
        If type was already set and is different ValueError is raised
        """
        if self.type is not None and self.type != exp_type:
            raise ValueError(
                "Invalid experiment, should be only physical or only alias")
        self.type = exp_type

    @staticmethod
    def _assocs_append(assoc_list, assoc):
        """ Append an association to the given association list
        If a similar association was already present, add assoc.nodes to it """
        l_l = assoc_list or []

        if assoc in l_l:
            # update assoc with nodes already in list

            cur_assoc = l_l.pop(l_l.index(assoc))
            # Add nodes to the list, uniq
            nodes = list(set(cur_assoc.nodes + assoc.nodes))
            # keep sorted to ease tests and readability
            assoc.nodes = sorted(nodes, key=helpers.node_url_sort_key)

        l_l.append(assoc)
        return l_l

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

        # register profile, may be None
        self.set_profile_associations(exp_dict['profile'], nodes)

        # register firmware
        if exp_dict['firmware'] is not None:
            firmware_name = basename(exp_dict['firmware'])
            self.set_fw_association(firmware_name, nodes)

    def set_fw_association(self, firmware_name, nodes):
        """Set firmware associations list"""
        # use alias number for AliasNodes
        _nodes = [nodes.alias] if self.type == 'alias' else nodes

        assoc = _FirmwareAssociations(firmware_name, _nodes)
        assocs = self._assocs_append(self.firmwareassociations, assoc)
        self.firmwareassociations = sorted(
            assocs, key=lambda x: x.firmwarename)

    def set_profile_associations(self, profile_name, nodes):
        """Set profile associations list"""
        if profile_name is None:
            return
        # use alias number for AliasNodes
        _nodes = [nodes.alias] if self.type == 'alias' else nodes

        assoc = _ProfileAssociations(profile_name, _nodes)
        assocs = self._assocs_append(self.profileassociations, assoc)
        self.profileassociations = sorted(
            assocs, key=lambda x: x.profilename)

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


def _write_experiment_archive(exp_id, data):
    """ Write experiment archive contained in 'data' to 'exp_id.tar.gz' """
    with open('%s.tar.gz' % exp_id, 'wb') as archive:
        archive.write(data)
