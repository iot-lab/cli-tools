# -*- coding: utf-8 -*-

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

"""Test the iotlabcli.associations module."""

import json
import unittest

from iotlabcli import associations
from iotlabcli import helpers

# pylint:disable=protected-access
# pylint:disable=invalid-name


class TestAssociationsMap(unittest.TestCase):
    """Test AssociationsMap."""

    def _assert_json_equal(self, assocs, expected):
        """Assert assocs give the expected result when json dumps and load.

        Also do a 'manual' convert to dict/list.
        """
        self.assertEqual(json.loads(helpers.json_dumps(assocs)), expected)
        self.assertEqual([assoc.__dict__ for assoc in assocs], expected)
        self.assertEqual(assocs.list(), expected)

    def test_associations_map(self):
        """Test AssociationsMap."""
        assocs = associations.AssociationsMap('firmware', 'nodes',
                                              helpers.node_url_sort_key)

        # Add 'firmware.elf'
        assoc = assocs.extendvalues('firmware.elf', ['m3-2', 'm3-1', 'm3-10'])
        expected = [{u'firmwarename': u'firmware.elf',
                     u'nodes': [u'm3-1', u'm3-2', u'm3-10']}]
        self._assert_json_equal(assocs, expected)

        # Add nodes
        assocs['firmware.elf'] += ['m3-6']  # also works with '+='
        expected = [{u'firmwarename': u'firmware.elf',
                     u'nodes': [u'm3-1', u'm3-2', u'm3-6', u'm3-10']}]
        self._assert_json_equal(assocs, expected)

        # Add 'a_tutorial.elf'
        assoc = assocs.setdefault('a_tutorial.elf', [])
        assoc.extend(['m3-5', 'm3-4'])  # Use extend, data needs to be sorted
        expected = [{u'firmwarename': u'a_tutorial.elf',
                     u'nodes': [u'm3-4', u'm3-5']},
                    {u'firmwarename': u'firmware.elf',
                     u'nodes': [u'm3-1', u'm3-2', u'm3-6', u'm3-10']}]
        self._assert_json_equal(assocs, expected)

        # remove an entry
        del assocs['firmware.elf']
        expected = [{u'firmwarename': u'a_tutorial.elf',
                     u'nodes': [u'm3-4', u'm3-5']}]
        self._assert_json_equal(assocs, expected)

    def test_associationsmap_from_list(self):
        """Test loading a dict from a list."""
        assocs = associations.AssociationsMap('firmware', 'nodes',
                                              helpers.node_url_sort_key)
        assocs.extendvalues('test.elf', ['m3-1', 'm3-2'])
        assocs.extendvalues('fw.elf', ['m3-20', 'm3-5'])
        assocs_list = assocs.list()

        loaded_assocs = associations.AssociationsMap.from_list(
            assocs_list, 'firmware', 'nodes', helpers.node_url_sort_key)

        self.assertEqual(assocs_list, loaded_assocs.list())
        self.assertEqual(loaded_assocs, assocs)

        # Check keys
        self.assertEqual(sorted(assocs.keys()), ['fw.elf', 'test.elf'])

        # Test loading None
        ret = associations.AssociationsMap.from_list(None, 'script', 'sites')
        self.assertTrue(ret is None)

    def test_association_dict_factory(self):
        """Test associationsmapdict_from_dict."""
        assocsdict = {
            'firmware': [
                {'firmwarename': 'a_tutorial.elf',
                 'nodes': ['m3-4', 'm3-6']},
                {'firmwarename': 'firmware.elf',
                 'nodes': ['m3-1', 'm3-2', 'm3-5', 'm3-10']},
            ],
            'profile': [
                {'profilename': 'consumption',
                 'nodes': ['m3-4']},
                {'profilename': 'radio',
                 'nodes': ['m3-1', 'm3-2']},
            ],
        }

        ret = associations.associationsmapdict_from_dict(assocsdict, 'nodes')
        self.assertEqual(ret['profile']['consumption'], ['m3-4'])
        self.assertEqual(ret['firmware']['a_tutorial.elf'], ['m3-4', 'm3-6'])

        # None case
        ret = associations.associationsmapdict_from_dict(None, 'nodes')
        self.assertTrue(ret is None)


class TestAssociation(unittest.TestCase):
    """Test Association corner cases."""
    def test_repr(self):
        """Test Association 'repr'."""
        assocclass = associations._Association.for_key_value('firmware',
                                                             'nodes')
        assoc = assocclass('test.elf', ['m3-1', 'm3-2', 'm3-3'])

        reprret = 'FirmwareNodesAssociation(%r, %r)'
        ret = reprret % ('test.elf', ['m3-1', 'm3-2', 'm3-3'])
        self.assertEqual(repr(assoc), ret)

        # only repr defined
        self.assertEqual(repr(assoc), str(assoc))

    def test_abstract_class(self):
        """Test error when instanciating abstract class."""
        self.assertRaises(NotImplementedError, associations._Association,
                          'test.elf', ['m3-1', 'm3-2'])

    def test_accessing_removed_method(self):
        """Test could not access dict methods on object."""
        assocclass = associations._Association.for_key_value('firmware',
                                                             'nodes')
        assoc = assocclass('test.elf', ['m3-1', 'm3-2', 'm3-3'])
        with self.assertRaises(AttributeError):
            assoc.update()
