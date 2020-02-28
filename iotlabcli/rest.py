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

""" Rest API class

Methods are meant to be used internally.

Users will only instanciate an Api object and pass it as
first parameter to the function.

"""

import sys
import requests
from requests.auth import HTTPBasicAuth
from iotlabcli import helpers
# pylint: disable=import-error,no-name-in-module
# pylint: disable=wrong-import-order
try:  # pragma: no cover
    from urllib.parse import urljoin, urlencode
    from urllib.error import HTTPError
except ImportError:  # pragma: no cover
    # pylint: disable=import-error,no-name-in-module,ungrouped-imports
    from urlparse import urljoin
    from urllib import urlencode
    from urllib2 import HTTPError


try:  # pragma: no cover

    # With newer versions of requests, old python version may
    # raise an InsecurePlatformWarning
    #   https://urllib3.readthedocs.org/en/latest/\
    #       security.html#insecureplatformwarning

    # It can be fixed by installing pyopenssl support as described here
    #   https://urllib3.readthedocs.org/en/latest/\
    #       security.html#openssl-pyopenssl
    #
    # Dependencies can be installed with
    #     pip install iotlabcli[secure]

    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
    pass


# pylint: disable=maybe-no-member,no-member
class Api():  # pylint:disable=too-many-public-methods
    """ IoT-Lab REST API """
    _cache = {}
    url = helpers.read_custom_api_url() or 'https://www.iot-lab.info/api/'

    def __init__(self, username, password):
        """
        :param username: username for Basic password auth
        :param password: password for Basic auth
        :param url: url of API.
        """
        self.auth = HTTPBasicAuth(username, password)

    def get_sites_details(self):
        """ Get testbed sites details """
        return self.method('sites/details')

    def get_nodes(self, list_id=False, site=None, **selections):
        """ Get testbed nodes description

        :param list_id: return result in 'exp_list' format '3-12+35'
        :param site: restrict to site
        :param **selections: other selections than site
        """
        if site:
            selections['site'] = site

        url = 'nodes%s' % ("/ids" if list_id else '')
        if selections:
            # the order of parameters in the encoded string
            # will match the order of tuples list
            url += '?' + urlencode(sorted(list(selections.items())))
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

    def get_running_experiments(self):
        """ Get testbed running experiments """
        return self.method('experiments/running')

    def get_experiment_info(self, expid, option=''):
        """ Get user experiment description.
        :param expid: experiment id submission (e.g. OAR scheduler)
        :param option: Restrict to some values:
            * '':            experiment submission
            * 'nodes':       nodes list
            * 'nodes_ids':   nodes id list: (1-34+72 format)
            * 'data':        experiment tar.gz with description and firmwares
            * 'deployment':  deployment info
        """
        assert option in ('', 'nodes', 'nodes_ids', 'data', 'deployment')

        url = 'experiments/%s' % expid
        if option:
            url += '/%s' % option
        return self.method(url, raw=(option == 'data'))

    def stop_experiment(self, expid):
        """ Stop user experiment.

        :param id: experiment id submission (e.g. OAR scheduler)
        """
        return self.method('experiments/%s' % expid, 'delete')

    def reload_experiment(self, expid, exp_json=None):
        """Reload user experiment.

        :param expid: experiment id submission (e.g. OAR scheduler)
        :param exp_json: experiment duration and reservation configuration
        :returns JSONObject
        """
        url = 'experiments/%d/reload' % expid
        return self.method(url, 'post', json=exp_json)

    # Node commands

    def node_command(self, command, expid, nodes=(), option=None):
        """ Lanch 'command' on user experiment list nodes

        :param id: experiment id submission (e.g. OAR scheduler)
        :param nodes: list of nodes, if empty apply on all nodes
        :param opt: additional string to pass as option in the url
        :returns: dict
        """
        url = 'experiments/%s/nodes/%s' % (expid, command)
        if option:
            url += '/%s' % option
        return self.method(url, 'post', json=nodes)

    def node_update(self, expid, files, binary=False):
        """ Launch update command (flash firmware) on user
        experiment list nodes

        :param id: experiment id submission (e.g. OAR scheduler)
        :param files: nodes list description and firmware
        :type files: dict
        :returns: dict
        """
        url = 'experiments/{}/nodes/flash'.format(expid)
        if binary:
            url += '/binary'
        return self.method(url, 'post', files=files)

    def node_profile_load(self, expid, files):
        """Update profile with profile json on user
        experiment list nodes

        :param id: experiment id submission (e.g. OAR scheduler)
        :param files: nodes list description and firmware
        :type files: dict
        :returns: dict
        """
        return self.method('experiments/%s/nodes/monitoring' % expid,
                           'post', files=files)

    # script
    def script_command(self, expid, command, files=None, json=None):
        """Execute scripts on sites.

        :param expid: experiment id submission (e.g. OAR scheduler)
        :param command: in ('run', 'kill', 'status')
        :param files: 'run' only: script-site association and scripts content
        :param json: 'kill/status' only: sites list, may be empty for all sites
        """
        # Only json or files and for the correct command (inverted checks)
        assert json is not None or command in ('run',)
        assert files is not None or command in ('kill', 'status',)

        url = 'experiments/%s/scripts/%s' % (expid, command)
        return self.method(url, 'post', files=files, json=json)

    # Profile methods

    def get_profiles(self, archi=None):
        """ Get user's list profile description

        :returns JSONObject
        """
        url = 'monitoring'
        if archi is not None:
            url += '?archi={}'.format(archi)
        return self.method(url)

    def get_profile(self, name):
        """ Get user profile description.

        :param name: profile name
        :type name: string
        :returns JSONObject
        """
        return self.method('monitoring/%s' % name)

    def add_profile(self, profile):
        """ Add user profile

        :param profile: profile description
        :type profile: JSONObject.
        """
        # dict has no __dict__ and load_profile gives a dict
        # requests wants a 'simple' type like dict
        profile = profile if isinstance(profile, dict) else profile.__dict__
        ret = self.method('monitoring', 'post', json=profile)
        return ret

    def del_profile(self, name):
        """ Delete user profile

        :param profile_name: name
        :type profile_name: string
        """
        ret = self.method('monitoring/%s' % name, 'delete')
        return ret

    def check_credential(self):
        """ Check that the credentials are valid """
        try:
            self.method('user')
            return True
        except HTTPError as err:
            if err.code == 401:
                return False
            raise  # pragma no cover

# robot

    def robot_command(self, command, expid, nodes=()):
        """Run 'status' on user experiment robot list nodes.

        :param id: experiment id submission (e.g. OAR scheduler)
        :param nodes: list of nodes, if empty apply on all nodes
        """
        assert command in ('status',)
        return self.method('experiments/%s/robots/%s' % (expid, command),
                           'post', json=nodes)

    def robot_update_mobility(self, expid, name, nodes=()):
        """Update mobility on user experiment robot list nodes.

        :param id: experiment id submission (e.g. OAR scheduler)
        :param nodes: list of nodes, if empty apply on all nodes
        """
        url = 'experiments/%s/robots/mobility/%s' % (expid, name)
        return self.method(url, 'post', json=nodes)

    @classmethod
    def get_robot_mapfile(cls, site, mapfile):
        """ Download robot mapfile.

        :params site: Map info for site
        :params mapfile: select type in ('mapconfig', 'mapimage', 'dockconfig')
        :returns: Image content or json loaded structure
        """
        assert mapfile in ('map/config', 'map/image', 'dock/config')
        raw = mapfile in ('map/image',)

        api = cls(None, None)
        url = 'robots/%s/%s' % (site, mapfile)
        return api.method(url, raw=raw)

    def get_circuits(self, **selections):
        """List circuits mobilities."""
        url = 'mobilities/circuits'
        if selections:
            # the order of parameters in the encoded string
            # will match the order of tuples list
            url += '?' + urlencode(sorted(list(selections.items())))
        return self.method(url)

    def get_circuit(self, name):
        """Get user mobilities."""
        return self.method('mobilities/circuits/%s' % name)

    def method(self, url, method='get',  # pylint:disable=too-many-arguments
               json=None, files=None, raw=False):
        """Call http `method` on iot-lab-url/'url'.

        :param url: url of API.
        :param method: request method
        :param json: send as 'post' json encoded data
        :param files: send as 'post' multipart data
        :param raw: Should data be loaded as json or not
        """
        assert method in ('get', 'post', 'delete')
        assert (method == 'post') or (files is None and json is None)

        _url = urljoin(self.url, url)

        req = self._request(_url, method, auth=self.auth,
                            json=json, files=files)
        if requests.codes.ok == req.status_code:
            return req.content if raw else req.json()
        if requests.codes.no_content == req.status_code:
            return None
        return self._raise_http_error(_url, req)

    @staticmethod
    def _request(url, method, **kwargs):
        """ Call http `method` on 'url'

        :param url: url of API.
        :param method: request method
        :param **kwargs: requests.request additional arguments """
        try:
            return requests.request(method, url, **kwargs)
        except Exception:  # show issue with old requests versions
            raise RuntimeError(sys.exc_info())

    @staticmethod
    def _raise_http_error(url, req):
        """ Raises HTTP error for 'url' and 'req' """
        # Indent req.text to pretty print it later
        indented_lines = ['\t' + l for l in req.text.splitlines(True)]
        msg = '\n' + ''.join(indented_lines)
        raise HTTPError(url, req.status_code, msg, req.headers, None)

    @classmethod
    def get_sites(cls):
        """ Get testbed sites description
        May be run unauthicated

        :returns JSONObject
        """
        return cls._get_with_cache('sites')

    @classmethod
    def _get_with_cache(cls, url):
        """ Get resource from either cache or rest
        :returns JSONObject
        """
        try:
            return cls._cache[url]
        except KeyError:
            api = cls(None, None)  # unauthenticated request
            return cls._cache.setdefault(url, api.method(url))
