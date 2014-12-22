# -*- coding:utf-8 -*-
""" Test the iotlabcli.rest module """

# pylint: disable=too-many-public-methods
# pylint: disable=protected-access

import unittest

from iotlabcli import rest
from iotlabcli.helpers import json_dumps
from iotlabcli.tests.my_mock import RequestRet

# pylint: disable=import-error,no-name-in-module
try:  # pragma: no cover
    from mock import patch
except ImportError:  # pragma: no cover
    from unittest.mock import patch
try:  # pragma: no cover
    from urllib2 import HTTPError
except ImportError:  # pragma: no cover
    from urllib.error import HTTPError


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

    def test_method(self):
        """ Test Api.method rest submission """
        ret = {'test': 'val'}
        ret_val = RequestRet(200, content=json_dumps(ret))
        m_req = patch('requests.request', return_value=ret_val).start()

        # pylint:disable=protected-access
        _auth = self.api.auth

        # call get
        ret = self.api.method('page')
        m_req.assert_called_with('get', self._url + 'page',
                                 files=None, json=None, auth=_auth)
        self.assertEquals(ret, ret)
        ret = self.api.method('page?1', 'get')
        m_req.assert_called_with('get', self._url + 'page?1',
                                 files=None, json=None, auth=_auth)
        self.assertEquals(ret, ret)

        # call delete
        ret = self.api.method('deeel', 'delete')
        m_req.assert_called_with('delete', self._url + 'deeel',
                                 files=None, json=None, auth=_auth)
        self.assertEquals(ret, ret)

        # call post
        ret = self.api.method('post_page', 'post', json={})
        m_req.assert_called_with('post', self._url + 'post_page',
                                 files=None, json={}, auth=_auth)
        self.assertEquals(ret, ret)

        # call multipart
        _files = {'entry': '{}'}
        ret = self.api.method('multip', 'post', files=_files)
        m_req.assert_called_with('post', self._url + 'multip',
                                 files=_files, json=None, auth=_auth)
        self.assertEquals(ret, ret)
        patch.stopall()

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

    def test_method_raw(self):
        """ Run as Raw mode """
        ret_val = RequestRet(200, content='text_only')
        with patch('requests.request', return_value=ret_val):
            ret = self.api.method(self._url, raw=True)
            self.assertEquals(ret, 'text_only'.encode('utf-8'))

    def test_method_errors(self):
        """ Test Api.method rest submission error cases """
        # invalid status code
        ret_val = RequestRet(404, content='return_text')
        with patch('requests.request', return_value=ret_val):
            self.assertRaises(HTTPError, self.api.method, self._url)
