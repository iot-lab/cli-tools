# -*- coding:utf-8 -*-
""" Test the iotlabcli.rest module """

# pylint: disable=too-many-public-methods

import unittest
try:
    # pylint: disable=import-error,no-name-in-module
    from mock import patch, Mock
except ImportError:  # pragma: no cover
    # pylint: disable=import-error,no-name-in-module
    from unittest.mock import patch, Mock
import iotlabcli
from iotlabcli import rest, json_dumps
from iotlabcli.tests.my_mock import RequestRet


class TestRest(unittest.TestCase):
    """ Test the iotlabcli.rest module
    As the interface itself cannot really be unit-tested against the remote
    REST server, I only test the internal functionnalities.

    Also, most of the internal code execution has been done by the upper layers
    So I don't re-check every method that just does formatting.
    """

    def test__method(self):
        """ Test Api._method rest submission """
        ret = {'test': 'val'}
        ret_val = RequestRet(text=json_dumps(ret), status_code=200)
        post = patch('requests.post', return_value=ret_val).start()
        delete = patch('requests.delete', return_value=ret_val).start()
        get = patch('requests.get', return_value=ret_val).start()

        # pylint:disable=protected-access
        _auth = Mock()
        _url = 'http://url.test.org/rest/method/query'

        # call get
        ret = rest.Api._method(_url)
        get.assert_called_with(_url, auth=None, verify=False)
        self.assertEquals(ret, ret)
        ret = rest.Api._method(_url, method='GET', auth=_auth)
        get.assert_called_with(_url, auth=_auth, verify=False)
        self.assertEquals(ret, ret)

        # call delete
        ret = rest.Api._method(_url, method='DELETE')
        delete.assert_called_with(_url, auth=None, verify=False)
        self.assertEquals(ret, ret)

        # call post
        ret = rest.Api._method(_url, method='POST', data={})
        post.assert_called_with(
            _url, data='{}', headers={'content-type': 'application/json'},
            auth=None, verify=False)
        self.assertEquals(ret, ret)

        # call multipart
        _files = {'entry': '{}'}
        ret = rest.Api._method(_url, method='MULTIPART', data=_files)
        post.assert_called_with(_url, files=_files, auth=None, verify=False)
        self.assertEquals(ret, ret)
        patch.stopall()

    def test__method_errors(self):
        """ Test Api._method rest submission error cases """
        # pylint:disable=protected-access
        _url = 'http://url.test.org/rest/method/query'

        # invalid status code
        ret_val = RequestRet(text='return_text', status_code=404)
        with patch('requests.get', return_value=ret_val):
            try:
                rest.Api._method(_url)
                self.fail("iotlabcli.Error not raised")
            except iotlabcli.Error as err:
                self.assertEquals("HTTP error code: 404\nreturn_text",
                                  str(err))

        # Non JSON output, mainly when returning simple text
        ret_val = RequestRet(text='text_only', status_code=200)
        with patch('requests.get', return_value=ret_val):
            ret = rest.Api._method(_url)
            self.assertEquals(ret, 'text_only')

    @patch('iotlabcli.rest.read_file')
    def test_read_custom_api_url(self, read_file_mock):
        """ Test API URL reading """
        read_file_mock.side_effect = IOError()

        self.assertTrue(rest.read_custom_api_url() is None)

        read_file_mock.side_effect = None
        read_file_mock.return_value = 'API_URL_CUSTOM'
        self.assertEquals('API_URL_CUSTOM', rest.read_custom_api_url())

        with patch('os.getenv', return_value='API_URL_2'):
            self.assertEquals('API_URL_2', rest.read_custom_api_url())
