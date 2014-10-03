# -*- coding:utf-8 -*-
""" Rest API class

Methods are meant to be used internally.

Users will only instanciate an Api object and pass it as
first parameter to the function.

"""

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
from iotlabcli import helpers


API_URL = helpers.read_custom_api_url() or 'https://www.iot-lab.info/rest/'


# pylint: disable=maybe-no-member,no-member
class Api(object):
    """ IoT-Lab REST API """
    _cache = {}

    def __init__(self, username, password, url=API_URL):
        """
        :param username: username for Basic password auth
        :param password: password for Basic auth
        :param url: url of API.
        """
        self.url = url
        self.auth = HTTPBasicAuth(username, password)

    def get_resources(self, list_id=False, site=None):
        """ Get testbed resources description

        :param list_id: return result in 'exp_list' format '3-12+35'
        :param site: restrict to site
        """
        query = 'experiments?%s' % ('id' if list_id else 'resources')
        if site is not None:
            query += '&site=%s' % site
        return self.method(query)

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
        return self.method(query, raw=('data' == option))

    def stop_experiment(self, expid):
        """ Stop user experiment.

        :param id: experiment id submission (e.g. OAR scheduler)
        """
        return self.method('experiments/%s' % expid, method='DELETE')

    # Node commands

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

    # Profile methods

    def get_profiles(self):
        """ Get user's list profile description

        :returns JSONObject
        """
        return self.method('profiles')

    def get_profile(self, name):
        """ Get user profile description.

        :param name: profile name
        :type name: string
        :returns JSONObject
        """
        return self.method('profiles/%s' % name)

    def add_profile(self, name, profile):
        """ Add user profile

        :param profile: profile description
        :type profile: JSONObject.
        """
        return self.method('profiles/%s' % name, method='POST',
                           data=profile, raw=True)

    def del_profile(self, name):
        """ Delete user profile

        :param profile_name: name
        :type profile_name: string
        """
        return self.method('profiles/%s' % name,
                           method='DELETE', raw=True)

    # Common methods

    def method(self, url, method='GET', data=None, raw=False):
        """
        :param url: url of API.
        :param method: request method
        :param data: request data
        """
        method_url = urljoin(self.url, url)

        return self._method(method_url, method, self.auth, data, raw)

    @staticmethod
    def _method(url, method='GET', auth=None, data=None, raw=False):
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
            raise RuntimeError("HTTP error code: {code}\n{text}".format(
                code=req.status_code, text=req.content))

        # request OK, return result object or direct answer
        if raw:
            result = req.content   # when getting archive or profile name
        else:
            result = json.loads(req.content)
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
