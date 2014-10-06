# -*- coding:utf-8 -*-
""" Test the iotlabcli.rest module """

# pylint: disable=too-many-public-methods
# pylint: disable=protected-access

import unittest
try:
    # pylint: disable=import-error,no-name-in-module
    from mock import patch, Mock
except ImportError:  # pragma: no cover
    # pylint: disable=import-error,no-name-in-module
    from unittest.mock import patch, Mock
from iotlabcli import rest, json_dumps
from iotlabcli.tests.my_mock import RequestRet


class TestRest(unittest.TestCase):
    """ Test the iotlabcli.rest module
    As the interface itself cannot really be unit-tested against the remote
    REST server, I only test the internal functionnalities.

    Also, most of the internal code execution has been done by the upper layers
    So I don't re-check every method that just does formatting.
    """
    _url = 'http://url.test.org/rest/method/query'

    def test__method(self):
        """ Test Api._method rest submission """
        ret = {'test': 'val'}
        ret_val = RequestRet(content=json_dumps(ret), status_code=200)
        post = patch('requests.post', return_value=ret_val).start()
        delete = patch('requests.delete', return_value=ret_val).start()
        get = patch('requests.get', return_value=ret_val).start()

        # pylint:disable=protected-access
        _auth = Mock()

        # call get
        ret = rest.Api._method(self._url)
        get.assert_called_with(self._url, auth=None, verify=False)
        self.assertEquals(ret, ret)
        ret = rest.Api._method(self._url, method='GET', auth=_auth)
        get.assert_called_with(self._url, auth=_auth, verify=False)
        self.assertEquals(ret, ret)

        # call delete
        ret = rest.Api._method(self._url, method='DELETE')
        delete.assert_called_with(self._url, auth=None, verify=False)
        self.assertEquals(ret, ret)

        # call post
        ret = rest.Api._method(self._url, method='POST', data={})
        post.assert_called_with(
            self._url, data='{}', headers={'content-type': 'application/json'},
            auth=None, verify=False)
        self.assertEquals(ret, ret)

        # call multipart
        _files = {'entry': '{}'}
        ret = rest.Api._method(self._url, method='MULTIPART', data=_files)
        post.assert_called_with(self._url, files=_files, auth=None,
                                verify=False)
        self.assertEquals(ret, ret)
        patch.stopall()

    def test__method_raw(self):
        """ Run as Raw mode """
        ret_val = RequestRet(content='text_only', status_code=200)
        with patch('requests.get', return_value=ret_val):
            ret = rest.Api._method(self._url, raw=True)
            self.assertEquals(ret, 'text_only')

    def test__method_errors(self):
        """ Test Api._method rest submission error cases """

        # invalid status code
        ret_val = RequestRet(content='return_text', status_code=404)
        with patch('requests.get', return_value=ret_val):
            self.assertRaisesRegexp(
                RuntimeError, "HTTP error: 404\nreturn_text",
                rest.Api._method, self._url)
