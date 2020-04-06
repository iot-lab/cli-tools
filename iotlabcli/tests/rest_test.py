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

""" Test the iotlabcli.rest module """

# pylint: disable=too-many-public-methods
# pylint: disable=protected-access
import json
import unittest

from iotlabcli import rest
from iotlabcli.helpers import json_dumps
from iotlabcli.tests.my_mock import RequestRet

from .c23 import HTTPError, patch


class TestRest(unittest.TestCase):
    """ Test the iotlabcli.rest module
    As the interface itself cannot really be unit-tested against the remote
    REST server, I only test the internal functionnalities.

    Also, most of the internal code execution has been done by the upper layers
    So I don't re-check every method that just does formatting.
    """
    _url = 'http://url.test.org/rest/'

    def setUp(self):
        self.api = rest.Api('user', 'password')
        self.api.url = self._url

    def test_method_no_content(self):
        """ Test Api.method rest code 204 """
        ret_val = RequestRet(204, content='')
        m_req = patch('requests.request', return_value=ret_val).start()
        _auth = self.api.auth

        ret = self.api.method('resources/123', 'delete')
        m_req.assert_called_with('delete', self._url + 'resources/123',
                                 files=None, json=None, auth=_auth)
        self.assertIsNone(ret)

    def test_method(self):
        """ Test Api.method rest submission """
        ret_expected = {'test': 'val'}
        ret_val = RequestRet(200, content=json_dumps(ret_expected))
        m_req = patch('requests.request', return_value=ret_val).start()

        # pylint:disable=protected-access
        _auth = self.api.auth

        # call get
        ret = self.api.method('page')
        m_req.assert_called_with('get', self._url + 'page',
                                 files=None, json=None, auth=_auth)
        self.assertEqual(ret_expected, ret)
        ret = self.api.method('page?1', 'get')
        m_req.assert_called_with('get', self._url + 'page?1',
                                 files=None, json=None, auth=_auth)
        self.assertEqual(ret_expected, ret)

        # call delete
        ret = self.api.method('deeel', 'delete')
        m_req.assert_called_with('delete', self._url + 'deeel',
                                 files=None, json=None, auth=_auth)
        self.assertEqual(ret_expected, ret)

        # call post
        ret = self.api.method('post_page', 'post', json={})
        m_req.assert_called_with('post', self._url + 'post_page',
                                 files=None, json={}, auth=_auth)
        self.assertEqual(ret_expected, ret)

        # call multipart
        _files = {'entry': '{}'}
        ret = self.api.method('multip', 'post', files=_files)
        m_req.assert_called_with('post', self._url + 'multip',
                                 files=_files, json=None, auth=_auth)
        self.assertEqual(ret_expected, ret)
        patch.stopall()

    @patch('iotlabcli.rest.Api.method')
    def test__get_with_cache(self, api_method):
        """ Test Api._get_with_cache """
        ret = {'ret': 'my_url'}
        api_method.return_value = ret

        self.assertEqual(ret, rest.Api._get_with_cache('my_url'))
        self.assertEqual(ret, rest.Api._get_with_cache('my_url'))
        self.assertEqual(ret, rest.Api._get_with_cache('my_url'))
        self.assertEqual(ret, rest.Api._get_with_cache('my_url'))
        self.assertEqual(ret, rest.Api._get_with_cache('my_url'))
        self.assertEqual(1, api_method.call_count)

        ret = {'ret': 'my_url_2'}
        api_method.return_value = ret
        self.assertEqual(ret, rest.Api._get_with_cache('my_url_2'))
        self.assertEqual(ret, rest.Api._get_with_cache('my_url_2'))
        self.assertEqual(ret, rest.Api._get_with_cache('my_url_2'))
        self.assertEqual(2, api_method.call_count)

    def test_check_credentials(self):
        """ Test Api.method rest submission """
        ret_val = RequestRet(200, content='"OK"')
        patch('requests.request', return_value=ret_val).start()

        ret_val.status_code = 200
        self.assertTrue(self.api.check_credential())

        ret_val.status_code = 401
        self.assertFalse(self.api.check_credential())

        ret_val.status_code = 500
        self.assertRaises(HTTPError, self.api.check_credential)

        patch.stopall()

    def test_ssh_key(self):
        """ Test ssh keys get/set """
        test_ssh_keys = '{"sshkey": ["test"]}'
        test_ssh_keys_json = json.loads(test_ssh_keys)
        ret_val = RequestRet(200, content=test_ssh_keys)
        patch('requests.request', return_value=ret_val).start()
        assert self.api.get_ssh_keys() == test_ssh_keys_json
        assert self.api.set_ssh_keys(test_ssh_keys_json) is None
        patch.stopall()

    def test_method_raw(self):
        """ Run as Raw mode """
        ret_val = RequestRet(200, content='text_only')
        with patch('requests.request', return_value=ret_val):
            ret = self.api.method(self._url, raw=True)
            self.assertEqual(ret, 'text_only'.encode('utf-8'))

    def test_method_errors(self):
        """ Test Api.method rest submission error cases """
        # invalid status code
        ret_val = RequestRet(404, content='return_text')
        with patch('requests.request', return_value=ret_val):
            self.assertRaises(HTTPError, self.api.method, self._url)

        # using older requests version fail because of json argument
        with patch('requests.request', side_effect=TypeError()):
            self.assertRaises(RuntimeError, self.api.method, self._url)


class TestGetNodesSelection(unittest.TestCase):
    """Test get_nodes selection."""
    # pylint:disable=no-self-use

    @patch('iotlabcli.rest.Api.method')
    def test_get_nodes_selection(self, _method):
        """Test get_nodes selection."""
        _method.return_value = {'state': 'Running'}
        api = rest.Api(None, None)

        api.get_nodes(False, 'grenoble', archi='m3', state='Alive')
        _method.assert_called_with('nodes'
                                   '?archi=m3&site=grenoble&state=Alive')

        api.get_nodes(True, archi='a8', state='Busy', site='lille')
        _method.assert_called_with('nodes/ids'
                                   '?archi=a8&site=lille&state=Busy')


class TestGetCircuitsSelection(unittest.TestCase):
    """Test get_circuits selection."""
    # pylint:disable=no-self-use

    @patch('iotlabcli.rest.Api.method')
    def test_get_circuits_selection(self, _method):
        """Test get_circuits selection."""
        _method.return_value = {'circuit': 'test'}
        api = rest.Api(None, None)

        api.get_circuits(site='grenoble', type='predefined')
        _method.assert_called_with('mobilities/circuits'
                                   '?site=grenoble&type=predefined')
