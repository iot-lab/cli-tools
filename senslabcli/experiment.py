# Class python for Experiment serialization JSON

class Properties:
    def __init__(self,dict):
        self.__dict__.update(dict)

class AliasNodes:
    def __init__(self, alias=None , nbnodes=None, properties=None):
        self.alias = alias
        self.nbnodes = nbnodes
        self.properties = properties

class FirmwareAssociations:
    def __init__(self, firmwarename=None, nodes=None):
        self.firmwarename = firmwarename
        self.nodes = nodes

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.firmwarename == other.firmwarename
        else:
            return False

class ProfileAssociations:
    def __init__(self, profilename=None, nodes=None):
        self.profilename = profilename
        self.nodes = nodes

    def __eq__(self,other):
        if isinstance(other, self.__class__):
            return self.profilename == other.profilename
        else:
            return False

class Experiment:
    def __init__(self, type=None, name=None, duration=None, reservation=None, nodes=None,
        firmwareassociations=None ,profileassociations=None):
        self.type = type
        self.duration = duration
        self.reservation = reservation
        self.name = name
        self.nodes = nodes
        self.firmwareassociations = firmwareassociations
        self.profileassociations = profileassociations

    def set_firmware_associations(self,firmware_name,nodes):
        fa = FirmwareAssociations(firmware_name,nodes)
        if (self.firmwareassociations is None):
           self.firmwareassociations = [fa]
        else:
           if (fa in self.firmwareassociations):
              index = self.firmwareassociations.index(fa)
              self.firmwareassociations[index].nodes = self.firmwareassociations[index].nodes + nodes
           else:
              self.firmwareassociations.append(fa)


    def set_profile_associations(self,profile_name,nodes):
        pa = ProfileAssociations(profile_name,nodes)
        if (self.profileassociations is None):
           self.profileassociations = [pa]
        else:
           if (pa in self.profileassociations):
              index = self.profileassociations.index(pa)
              self.profileassociations[index].nodes = self.profileassociations[index].nodes + nodes
           else:
              self.profileassociations.append(pa)

    def set_physical_nodes(self,nodes):
        if (self.nodes is None):
           self.nodes = nodes
        else:
           #self.nodes += nodes
           self.nodes = self.nodes + nodes

    def set_alias_nodes(self, alias_number, nb_nodes, properties):
        an = AliasNodes(alias_number, nb_nodes, Properties(properties))
        if (self.nodes is None):
           self.nodes = [an]
        else:
           self.nodes.append(an)





