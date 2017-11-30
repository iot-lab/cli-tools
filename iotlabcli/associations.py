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

"""Implement Association, the dict like key->values format for JSON API.

Each association is an association between a key and values in the format:
For association 'type' with resources of 'rvalues':
Dumped JSON format is:

    {
        "typename": "key",
        "rvalues": ["value", "value2"]
    }

"""

import abc
import collections


def _disabled_method(*_):
    """Disabled method."""
    raise AttributeError


def setattrdefault(obj, attribute, default=None):
    """Setdefault for attribute.

    Returns 'attribute' value if defined or set it to default and return it.
    """
    try:
        return getattr(obj, attribute)
    except AttributeError:
        setattr(obj, attribute, default)
        return default


class _Association(collections.MutableMapping, dict):
    """_Association class key->value.

    Inherit from dict to be dumped as a dict by json.
    """
    __metaclass__ = abc.ABCMeta
    KEYFMT = '{}name'
    KEY = None
    VALUE = None
    VALUE_SORT_KEY = None

    def __init__(self, key, value):  # pylint:disable=super-init-not-called
        # Don't call 'dict' init, only used for json dumping
        self._concrete_class()
        self.key = key
        self.value = value

    @property
    def key(self):
        """Return value."""
        return getattr(self, self._keyattr())

    @key.setter
    def key(self, val):
        """Set value."""
        return setattr(self, self._keyattr(), val)

    @property
    def value(self):
        """Return value."""
        value = getattr(self, self._valueattr())
        # Sort now if it has not been sorted before
        self._sort()
        return value

    @value.setter
    def value(self, value):
        """Set value uniq and sorted."""
        setvalue = set(value)  # copy and keep uniq

        # Use given `value` object for 'setdefault'
        value = setattrdefault(self, self._valueattr(), value)
        del value[:]

        value.extend(setvalue)
        self._sort()

    def _value(self):
        """Get value directly, avoid loop when accessing in _sort."""
        return getattr(self, self._valueattr())

    def _sort(self):
        """Sort values with key."""
        self._value().sort(key=self.VALUE_SORT_KEY)

    # Get actual attributes name

    @classmethod
    def _keyattr(cls):
        """Return key attribute name."""
        return cls.KEYFMT.format(cls.KEY)

    @classmethod
    def _valueattr(cls):
        """Return values attribute name."""
        return cls.VALUE

    @classmethod
    def from_dict(cls, assocdict):
        """Init an association from an association dict."""
        return cls(assocdict[cls._keyattr()], assocdict[cls._valueattr()])

    @staticmethod
    def staticclassattribute(function):
        """Return given function as a staticmethod, handle None as None.

        This allows storing the function as a class attribute.
        """
        return staticmethod(function) if function is not None else None

    @classmethod
    def for_key_value(cls, key, value, sortkey=None):
        """Create association class for assoctype."""
        name = '{}{}Association'.format(key.title(), value.title())

        class KeyValuesAssociation(cls):  # pylint:disable=too-many-ancestors
            """KeyValuesAssociation class->Nodes."""
            KEY = key
            VALUE = value
            VALUE_SORT_KEY = cls.staticclassattribute(sortkey)
        KeyValuesAssociation.__name__ = name

        return KeyValuesAssociation

    def __repr__(self):
        """Representation. Ignore 'sortkey'."""
        return '%s(%r, %r)' % (self.__class__.__name__, self.key,
                               getattr(self, 'value', None))

    @classmethod
    def _concrete_class(cls):
        """Verify that class is concrete and not abstract."""
        if cls.KEY is None or cls.VALUE is None:
            raise NotImplementedError(
                "AbstractClass, create real class with 'for_key_value'")

    def dict(self):
        """Dump as a dict."""
        return self.__dict__.copy()

    # MutableMapping required methods

    def __iter__(self):
        """Return __dict__."""
        # If list has been modified directly, json dumps will still be sorted
        self._sort()
        return self.__dict__.__iter__()

    def __len__(self):
        return self.__dict__.__len__()

    def __getitem__(self, key):
        return self.__dict__.__getitem__(key)

    # Delete unwanted 'dict' methods
    clear = property(_disabled_method)
    copy = property(_disabled_method)
    fromkeys = property(_disabled_method)
    get = property(_disabled_method)
    has_key = property(_disabled_method)
    pop = property(_disabled_method)
    popitem = property(_disabled_method)
    setdefault = property(_disabled_method)
    update = property(_disabled_method)
    __add__ = property(_disabled_method)

    # Don't set them as properties, issue with python2.6
    def __delitem__(self, _):  # pragma: no cover
        return _disabled_method(self)

    def __setitem__(self, *_):  # pragma: no cover
        # pylint: disable=arguments-differ
        return _disabled_method(self)


class AssociationsMap(  # pylint:disable=too-many-public-methods
        collections.MutableMapping, list):
    """Sorted Map of Associations objects.

    Inherit list to be json serialized to a list.
    """

    def __init__(self, assoctype, resource, sortkey=None):
        # pylint:disable=super-init-not-called

        list.__init__(self)
        self.assoc_class = _Association.for_key_value(assoctype, resource,
                                                      sortkey)
        self._map = {}

    def __getitem__(self, key):
        return self._map[key].value

    def __delitem__(self, key):
        assoc = self._map.pop(key)
        list.remove(self, assoc)

    def __setitem__(self, key, value):
        try:
            # overide accoc values if present, (no need to update list)
            assoc = self._map[key]
            assoc.value = value
        except KeyError:
            self._add(key, value)

    def extendvalues(self, key, values):
        """Extend values for `key`."""
        self.setdefault(key, []).extend(values)
        return self[key]

    def _add(self, key, value):
        """Add key,value entry.

        Keep list sorted by keys.
        """
        assoc = self.assoc_class(key, value)
        self._map[key] = assoc

        list.append(self, assoc)
        list.sort(self, key=lambda x: x.key)

    @classmethod
    def from_list(cls, assoclist, assoctype, resource, sortkey=None):
        """Create AssociationsMap from assoclist."""
        if assoclist is None:
            return None
        assocs = cls(assoctype, resource, sortkey=sortkey)
        for assoc_d in assoclist:
            assoc = assocs.assoc_class.from_dict(assoc_d)
            assocs[assoc.key] = assoc.value
        return assocs

    def list(self):
        """Dump to a list of dicts."""
        return [assoc.dict() for assoc in self]

    def __len__(self):
        return list.__len__(self)

    def __iter__(self):
        """Only to be used for json.dumps.

        It is not equivalent to 'keys' as it should return the whole value
        for json dumping.
        """
        # not compliant with 'keys' as it should iter on
        return list.__iter__(self)

    def keys(self):
        """Return dict equivalent `keys`."""
        return self._map.keys()

    def items(self):
        """Return dict equivalent `items`."""
        return self._map.items()

    # Delete unwanted 'list' methods
    append = property(_disabled_method)
    extend = property(_disabled_method)
    insert = property(_disabled_method)
    remove = property(_disabled_method)
    reverse = property(_disabled_method)
    sort = property(_disabled_method)
    __delslice__ = property(_disabled_method)
    __setslice__ = property(_disabled_method)


def associationsmapdict_from_dict(assocsdict, resource, sortkey=None):
    """Create a dict of AssociationsMap from `assocsdict` for `resource`."""
    if assocsdict is None:
        return None
    assocs = {}
    for assoctype, assoclist in assocsdict.items():
        assocs[assoctype] = AssociationsMap.from_list(assoclist, assoctype,
                                                      resource, sortkey)
    return assocs
