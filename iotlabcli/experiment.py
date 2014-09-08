# -*- coding:utf-8 -*-
"""Class python for Experiment serialization JSON"""


def experiment_dict(nodes, firmware_dict=None, profile_name=None):
    """ Create an experiment dict

    :param nodes: a list of nodes url or a AliasNodes object
    :param firmware_dict: Firmware associated, type dict with:
    :type firmware_dict: {'name': firmware_name, 'body': firmware_content}
    :param profile_name: Name of the profile associated

    """

    if isinstance(nodes, AliasNodes):
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


class AliasNodes(object):  # pylint: disable=too-few-public-methods
    """An AliasNodes class"""
    _alias = 0  # static count of current alias number

    def __init__(self, nbnodes, properties):
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
        AliasNodes._alias += 1
        self.alias = str(AliasNodes._alias)
        self.nbnodes = nbnodes
        self.properties = properties


class FirmwareAssociations(object):  # pylint: disable=too-few-public-methods
    """A FirmwareAssociations class

    >>> fw = FirmwareAssociations('name', ['3'])
    >>> fw == FirmwareAssociations('name', ['bla bla bla', 'test test'])
    True
    >>> fw == {'firmwarename': 'name', 'nodes':['3']}
    False
    """
    def __init__(self, firmwarename, nodes):
        self.firmwarename = firmwarename
        self.nodes = nodes

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.firmwarename == other.firmwarename
        else:
            return False


class ProfileAssociations(object):  # pylint: disable=too-few-public-methods
    """A ProfileAssociations class

    # coverage
    >>> pr = ProfileAssociations('name', ['3'])
    >>> pr == ProfileAssociations('name', ['bla bla bla', 'test test'])
    True
    >>> pr == {'profilename': 'name', 'nodes':['3']}
    False

    """
    def __init__(self, profilename, nodes):
        self.profilename = profilename
        self.nodes = nodes

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.profilename == other.profilename
        else:
            return False


class Experiment(object):
    """An Experiment class"""
    def __init__(self, name, duration, reservation):
        self.duration = duration
        self.reservation = reservation
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
            assoc.nodes = sorted(nodes, key=Experiment._node_url_key)

        l_l.append(assoc)
        return l_l

    def add_experiment_dict(self, exp_dict):
        """ Add an 'experiment_dict' to current experiment
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
            firmware = exp_dict['firmware']

            self.set_firmware_associations(firmware['name'], nodes)

    def set_firmware_associations(self, firmware_name, nodes):
        """Set firmware associations list"""
        # use alias number for AliasNodes
        _nodes = [nodes.alias] if self.type == 'alias' else nodes

        assoc = FirmwareAssociations(firmware_name, _nodes)
        assocs = self._assocs_append(self.firmwareassociations, assoc)
        self.firmwareassociations = sorted(
            assocs, key=lambda x: x.firmwarename)

    def set_profile_associations(self, profile_name, nodes):
        """Set profile associations list"""
        if profile_name is None:
            return
        # use alias number for AliasNodes
        _nodes = [nodes.alias] if self.type == 'alias' else nodes

        assoc = ProfileAssociations(profile_name, _nodes)
        assocs = self._assocs_append(self.profileassociations, assoc)
        self.profileassociations = sorted(
            assocs, key=lambda x: x.profilename)

    def set_physical_nodes(self, nodes_list):
        """Set physical nodes list """
        self._set_type('physical')

        self.nodes.extend(nodes_list)
        # Keep unique values and sorted
        self.nodes = sorted(list(set(self.nodes)), key=self._node_url_key)

    @staticmethod
    def _node_url_key(node_url):
        """
        >>> Experiment._node_url_key("m3-2.grenoble.iot-lab.info")
        ('grenoble', 'm3', 2)

        >>> Experiment._node_url_key("3")  # for alias nodes
        3
        """
        if node_url.isdigit():
            return int(node_url)
        _node, site = node_url.split('.')[0:2]
        node_type, num_str = _node.split('-')[0:2]
        return site, node_type, int(num_str)

    def set_alias_nodes(self, alias_nodes):
        """Set alias nodes list """
        self._set_type('alias')
        self.nodes.append(alias_nodes)
