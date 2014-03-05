# -*- coding:utf-8 -*-
"""Class python for Experiment serialization JSON"""


class Properties(object):
    """A properties (e.g : archi, site) class"""
    def __init__(self, prop_dict):
        self.__dict__.update(prop_dict)


class AliasNodes(object):
    """An AliasNodes class"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class FirmwareAssociations(object):
    """A FirmwareAssociations class"""
    def __init__(self, firmwarename=None, nodes=None):
        self.firmwarename = firmwarename
        self.nodes = nodes

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.firmwarename == other.firmwarename
        else:
            return False


class ProfileAssociations(object):
    """A ProfileAssociations class"""
    def __init__(self, profilename=None, nodes=None):
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
        self.nodes = None
        self.firmwareassociations = None
        self.profileassociations = None

    def set_firmware_associations(self, firmware_name, nodes):
        """Set firmware associations list"""
        association = FirmwareAssociations(firmware_name, nodes)
        if self.firmwareassociations is None:
            self.firmwareassociations = [association]
        else:
            if association in self.firmwareassociations:
                index = self.firmwareassociations.index(association)
                # Union of two lists (set for unique value)
                self.firmwareassociations[index].nodes = \
                    list(set(self.firmwareassociations[index].nodes + nodes))
            else:
                self.firmwareassociations.append(association)

    def set_profile_associations(self, profile_name, nodes):
        """Set profile associations list"""
        association = ProfileAssociations(profile_name, nodes)
        if self.profileassociations is None:
            self.profileassociations = [association]
        else:
            if association in self.profileassociations:
                index = self.profileassociations.index(association)
                # Union of two lists (set for unique value)
                self.profileassociations[index].nodes =  \
                    list(set(self.profileassociations[index].nodes + nodes))
            else:
                self.profileassociations.append(association)

    def set_physical_nodes(self, nodes):
        """Set physical nodes list
        """
        if self.nodes is None:
            self.nodes = nodes
        else:
            # Union of two lists (set for unique values)
            self.nodes = list(set(self.nodes + nodes))

    def set_alias_nodes(self, alias, nbnodes, dict_properties):
        """Set alias nodes list
        "nodes": [
            {
                "alias":"1",
                "nbnodes":1,
                "properties":{
                    "archi":"wsn430:cc2420",
                    "site":"devlille"
                }
            }
        ],
        """
        properties = Properties(dict_properties)
        nodes = AliasNodes(alias=alias,
                           nbnodes=nbnodes,
                           properties=properties)
        if self.nodes is None:
            self.nodes = [nodes]
        else:
            self.nodes.append(nodes)
