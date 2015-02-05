# -*- coding:utf-8 -*-
""" Rest API class

Methods are meant to be used internally.

Users will only instanciate an Api object and pass it as
first parameter to the function.

"""

import requests
from requests.auth import HTTPBasicAuth
from iotlabcli import helpers
# pylint: disable=import-error,no-name-in-module
try:  # pragma: no cover
    from urllib.parse import urljoin
    from urllib.error import HTTPError
except ImportError:  # pragma: no cover
    # pylint: disable=import-error,no-name-in-module
    from urlparse import urljoin
    from urllib2 import HTTPError


# pylint: disable=maybe-no-member,no-member
class Api(object):
    """ IoT-Lab REST API """
    _cache = {}
    url = helpers.read_custom_api_url() or 'https://www.iot-lab.info/rest/'

    def __init__(self, username, password):
        """
        :param username: username for Basic password auth
        :param password: password for Basic auth
        :param url: url of API.
        """
        self.auth = HTTPBasicAuth(username, password)

    def get_resources(self, list_id=False, site=None):
        """ Get testbed resources description

        :param list_id: return result in 'exp_list' format '3-12+35'
        :param site: restrict to site
        """
        url = 'experiments?%s' % ('id' if list_id else 'resources')
        if site is not None:
            url += '&site=%s' % site
        return self.method(url)

    def submit_experiment(self, files):
        """ Submit user experiment

        :param files: experiment description and firmware(s)
        :type files: dictionnary
        :returns JSONObject
        """
        return self.method('experiments', 'post', files=files)

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
            * 'start':     expected start time
        """
        assert option in ('', 'resources', 'id', 'state', 'data', 'start')

        url = 'experiments/%s' % expid
        if option:
            url += '?%s' % option
        return self.method(url, raw=('data' == option))

    def stop_experiment(self, expid):
        """ Stop user experiment.

        :param id: experiment id submission (e.g. OAR scheduler)
        """
        return self.method('experiments/%s' % expid, 'delete')

    # Node commands

    def node_command(self, command, expid, nodes=()):
        """ Lanch 'command' on user experiment list nodes

        :param id: experiment id submission (e.g. OAR scheduler)
        :param nodes: list of nodes, if empty apply on all nodes
        :returns: dict
        """
        return self.method('experiments/%s/nodes?%s' % (expid, command),
                           'post', json=nodes)

    def node_update(self, expid, files):
        """ Launch upadte command (flash firmware) on user
        experiment list nodes

        :param id: experiment id submission (e.g. OAR scheduler)
        :param files: nodes list description and firmware
        :type files: dict
        :returns: dict
        """
        return self.method('experiments/%s/nodes?update' % expid,
                           'post', files=files)

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
        # dict has no __dict__ and load_profile gives a dict
        # requests wants a 'simple' type like dict
        profile = profile if isinstance(profile, dict) else profile.__dict__
        ret = self.method('profiles/%s' % name, 'post', json=profile)
        return ret

    def del_profile(self, name):
        """ Delete user profile

        :param profile_name: name
        :type profile_name: string
        """
        ret = self.method('profiles/%s' % name, 'delete')
        return ret

    def check_credential(self):
        """ Check that the credentials are valid """
        try:
            self.method('users/%s?login' % self.auth.username, raw=True)
            return True
        except HTTPError as err:
            if 401 == err.code:
                return False
            raise  # pragma no cover

    def method(self, url, method='get',  # pylint:disable=too-many-arguments
               json=None, files=None, raw=False):
        """
        Call http `method` on iot-lab-url/'url'

        :param url: url of API.
        :param method: request method
        :param json: send as 'post' json encoded data
        :param files: send as 'post' multipart data
        :param raw: Should data be loaded as json or not
        """
        assert method in ('get', 'post', 'delete')
        assert (method == 'post') or (files is None and json is None)

        _url = urljoin(self.url, url)
        req = requests.request(
            method, _url, auth=self.auth, json=json, files=files)

        if requests.codes.ok == req.status_code:
            return req.content if raw else req.json()

        # Indent req.text to pretty print it later
        msg = '\n' + ''.join(['\t' + l for l in req.text.splitlines(True)])
        raise HTTPError(_url, req.status_code, msg, req.headers, None)

    @classmethod
    def get_sites(cls):
        """ Get testbed sites description
        May be run unauthicated

        :returns JSONObject
        """
        sites = cls._cache.get('sites', None)

        if 'sites' not in cls._cache:
            # unauthenticated request
            api = cls(username=None, password=None)
            sites = api.method('experiments?sites')
            cls._cache['sites'] = sites
        return cls._cache['sites']
