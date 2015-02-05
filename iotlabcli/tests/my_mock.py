# -*- coding: utf-8 -*-
""" common TestCase class  for testing commands """

import sys
import unittest
from iotlabcli import experiment
from iotlabcli.rest import Api
from iotlabcli.helpers import json_dumps
# pylint: disable=import-error,no-name-in-module
try:
    from mock import patch, Mock
except ImportError:  # pragma: no cover
    from unittest.mock import patch, Mock


API_RET = {"result": "test"}


class RequestRet(object):  # pylint:disable=too-few-public-methods
    """ Mock of Request return value """

    def __init__(self, status_code, content, headers=None):
        self.status_code = status_code
        self.content = content.encode('utf-8')
        self.headers = headers
        self.text = self.content.decode('utf-8')

    def json(self):
        """ Load output as JSON """
        import json
        return json.loads(self.text)


def api_mock(ret=None):
    """ Return a mock of an api object
    returned value for api methods will be 'ret' parameter or API_RET
    """
    ret = ret or API_RET
    ret_val = RequestRet(content=json_dumps(ret), status_code=200)  # HTTP OK
    patch('requests.request', return_value=ret_val).start()
    api_class = patch('iotlabcli.rest.Api').start()
    api_class.return_value = Mock(wraps=Api('user', 'password'))
    return api_class.return_value


def api_mock_stop():
    """ Stop all patches started by api_mock.
    Actually it stops everything but not a problem """
    patch.stopall()


# pylint: disable=too-many-public-methods
class CommandMock(unittest.TestCase):
    """ Common mock needed for testing commands """
    def setUp(self):
        self.api = api_mock()
        experiment.AliasNodes._alias = 0  # pylint:disable=protected-access

    def tearDown(self):
        api_mock_stop()
        patch.stopall()


class MainMock(unittest.TestCase):
    """ Common mock needed for testing main function of parsers """
    def setUp(self):
        self.api = api_mock()

        patch('sys.stderr', sys.stdout).start()
        patch('iotlabcli.parser.common.sites_list', Mock(
            return_value=['grenoble', 'strasbourg', 'euratech'])).start()

        patch('iotlabcli.auth.get_user_credentials',
              Mock(return_value=('username', 'password'))).start()

        get_exp = (lambda a, x, running_only=True:
                   x if x is not None else (123 if running_only else 234))
        patch('iotlabcli.helpers.get_current_experiment', get_exp).start()

    def tearDown(self):
        api_mock_stop()
        patch.stopall()
