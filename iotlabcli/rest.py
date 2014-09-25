# -*- coding:utf-8 -*-
""" Rest API class """

import os
import requests
import json
from requests.auth import HTTPBasicAuth
try:
    # pylint: disable=import-error,no-name-in-module
    from urllib.parse import urljoin
except ImportError:  # pragma: no cover
    # pylint: disable=import-error,no-name-in-module
    from urlparse import urljoin
from iotlabcli import json_dumps
import iotlabcli
from iotlabcli.helpers import read_file


def read_custom_api_url():
    """ Return the customized api url from:
     * environment variable IOTLAB_API_URL
     * config file in <HOME_DIR>/.iotlab.api-url
    """
    # try getting url from environment variable
    api_url = os.getenv('IOTLAB_API_URL')
    if api_url is not None:
        return api_url

    # try getting url from config file
    try:
        return read_file('~/.iotlab.api-url').strip()
    except IOError:
        return None

API_URL = read_custom_api_url() or 'https://www.iot-lab.info/rest/'


# pylint: disable=maybe-no-member,no-member
class Api(object):
    """ REST API """
    _cache = {}

    def __init__(self, username, password, url=API_URL):
        """
        :param url: url of API.
        :param username: username for Basic password auth
        :param password: password for Basic auth
        """

        self.url = url
        self.auth = HTTPBasicAuth(username, password)

    def method(self, url, method='GET', data=None):
        """
        :param url: url of API.
        :param method: request method
        :param data: request data
        """
        method_url = urljoin(self.url, url)

        return self._method(method_url, method, self.auth, data)

    @staticmethod
    def _method(url, method='GET', auth=None, data=None):
        """
        :param url: url to request.
        :param method: request method
        :param auth: HTTPBasicAuth object
        :param data: request data
        """
        if method == 'POST':
            headers = {'content-type': 'application/json'}
            req = requests.post(url, auth=auth, data=json_dumps(data),
                                headers=headers, verify=False)
        elif method == 'MULTIPART':
            req = requests.post(url, auth=auth, files=data, verify=False)
        elif method == 'DELETE':
            req = requests.delete(url, auth=auth, verify=False)
        else:
            req = requests.get(url, auth=auth, verify=False)

        if req.status_code != requests.codes.ok:
            # we have HTTP error (code != 200)
            raise iotlabcli.Error("HTTP error code: {code}\n{text}".format(
                code=req.status_code, text=req.text))

        # request OK, return result object or direct answer
        try:
            result = json.loads(req.text)
        except ValueError:
            result = req.text
        return result

    @staticmethod
    def get_sites():
        """ Get testbed sites description
        May be run unauthicated

        :returns JSONObject
        """
        sites = Api._cache.get('sites', None)

        if 'sites' not in Api._cache:
            # unauthenticated request
            sites = Api._method(urljoin(API_URL, 'experiments?sites'))
            Api._cache['sites'] = sites
        return Api._cache['sites']

    def get_resources(self, list_id=False, site=None):
        """ Get testbed resources description

        :param list_id: return result in 'exp_list' format '3-12+35'
        :param site: restrict to site
        """
        query = 'experiments?%s' % ('id' if list_id else 'resources')
        if site is not None:
            query += '&site=%s' % site
        return self.method(query)

    def get_profile(self, name):
        """ Get user profile description.

        :param name: profile name
        :type name: string
        :returns JSONObject
        """
        return self.method('profiles/%s' % name)

    def get_profiles(self):
        """ Get user's list profile description

        :returns JSONObject
        """
        return self.method('profiles')

    def add_profile(self, name, profile):
        """ Add user profile

        :param profile: profile description
        :type profile: JSONObject.
        """
        return self.method('profiles/%s' % name, method='POST', data=profile)

    def del_profile(self, name):
        """ Delete user profile

        :param profile_name: name
        :type profile_name: string
        """
        return self.method('profiles/%s' % name, method='DELETE')

    def submit_experiment(self, files):
        """ Submit user experiment

        :param files: experiment description and firmware(s)
        :type files: dictionnary
        :returns JSONObject
        """
        return self.method('experiments', method='MULTIPART', data=files)

    def get_experiments(self, state='Running', limit=0, offset=0):
        """ Get user's experiment
        :returns JSONObject
        """
        queryset = 'state=%s&limit=%u&offset=%u' % (state, limit, offset)
        return self.method('experiments?%s' % queryset)

    def get_experiment_info(self, expid, option=''):
        """ Get user experiment description.
        :param expid: experiment id submission (e.g. OAR scheduler)
        :param option: Restrict to some values:
            * '':          experiment submission
            * 'resources': resources list
            * 'id':        resources id list: (1-34+72 format)
            * 'state':     experiment state
            * 'data':      experiment tar.gz with description and firmwares
        """
        assert option in ('', 'resources', 'id', 'state', 'data')

        query = 'experiments/%s' % expid
        if option:
            query += '?%s' % option
        return self.method(query)

    def stop_experiment(self, expid):
        """ Stop user experiment.

        :param id: experiment id submission (e.g. OAR scheduler)
        """
        return self.method('experiments/%s' % expid, method='DELETE')

    def node_command(self, command, expid, nodes=()):
        """ Lanch 'command' on user experiment list nodes

        :param id: experiment id submission (e.g. OAR scheduler)
        :param nodes: list of nodes, if empty apply on all nodes
        :returns: dict
        """
        return self.method('experiments/%s/nodes?%s' % (expid, command),
                           method='POST', data=nodes)

    def node_update(self, expid, files):
        """ Launch upadte command (flash firmware) on user
        experiment list nodes

        :param id: experiment id submission (e.g. OAR scheduler)
        :param files: nodes list description and firmware
        :type files: dict
        :returns: dict
        """
        return self.method('experiments/%s/nodes?update' % expid,
                           method='MULTIPART', data=files)
