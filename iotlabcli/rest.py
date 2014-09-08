# -*- coding:utf-8 -*-
""" Rest API class """

import os
import requests
import json
import sys
from requests.auth import HTTPBasicAuth
from urlparse import urljoin


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
    home_directory = os.getenv('USERPROFILE') or os.getenv('HOME')
    api_url_filename = os.path.join(home_directory, ".iotlab.api-url")
    try:
        return open(api_url_filename).readline().strip()
    except IOError:
        return None

API_URL = read_custom_api_url() or 'https://www.iot-lab.info/rest/'

# pylint: disable=maybe-no-member,no-member


class Encoder(json.JSONEncoder):
    """ Encoder for serialization object python to JSON format """
    def default(self, obj):  # pylint: disable=method-hidden
        try:
            return obj.serialize()
        except AttributeError:
            return obj.__dict__


class Api(object):
    """ REST API """

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
            req = requests.post(url, auth=auth, data=data, headers=headers)
        elif method == 'MULTIPART':
            req = requests.post(url, auth=auth, files=data)
        elif method == 'DELETE':
            req = requests.delete(url, auth=auth)
        else:
            req = requests.get(url, auth=auth)

        if req.status_code != requests.codes.ok:
            # we have HTTP error (code != 200)
            print "HTTP error code : %s \n%s" % (req.status_code, req.text)
            sys.exit()
        # request OK, return result
        # TODO json.loads
        return req.text

    @staticmethod
    def get_sites():
        """ Get testbed sites description

        :returns JSONObject
        """
        # unauthenticated request
        url = urljoin(API_URL, 'experiments?sites')
        return json.loads(Api._method(url))

    def get_resources(self, site=None):
        """ Get testbed resources description

        :returns JSONObject
        """
        query = 'experiments?resources'
        if site is not None:
            query += '&site=%s' % site
        return json.loads(self.method(query))

    def get_resources_id(self, site=None):
        """ Get testbed resources state description

        :returns JSONObject
        """
        query = 'experiments?id'
        if site is not None:
            query += '&site=%s' % site
        return json.loads(self.method(query))

    def get_profile(self, name):
        """ Get user profile description.

        :param name: profile name
        :type name: string
        :returns JSONObject
        """
        # TODO json.loads
        return self.method('profiles/%s' % name)

    def get_profiles(self):
        """ Get user's list profile description

        :returns JSONObject
        """
        # TODO json.loads
        return self.method('profiles')

    def add_profile(self, name, profile):
        """ Add user profile

        :param profile: profile description
        :type profile: JSONObject.
        """
        # TODO json.loads
        # TODO json.dumps on data, handle it on it's cli file
        self.method('profiles/%s' % name, method='POST', data=profile)

    def del_profile(self, name):
        """ Delete user profile

        :param profile_name: name
        :type profile_name: string
        """
        # TODO json.loads
        self.method('profiles/%s' % name, method='DELETE')

    def submit_experiment(self, files):
        """ Submit user experiment

        :param files: experiment description and firmware(s)
        :type files: dictionnary
        :returns JSONObject
        """
        return json.loads(self.method('experiments', method='MULTIPART',
                                      data=files))

    def get_experiments(self, state='Running', limit=0, offset=0):
        """ Get user's experiment
        :returns JSONObject
        """
        queryset = 'state=%s&limit=%u&offset=%u' % (state, limit, offset)
        return json.loads(self.method('experiments?%s' % queryset))

    def get_experiment(self, expid):
        """ Get user experiment description.

        :param id: experiment id submission (e.g. OAR scheduler)
        :returns JSONObject
        """
        return json.loads(self.method('experiments/%s' % expid))

    def get_experiment_resources(self, expid):
        """ Get user experiment resources list description.

        :param id: experiment id submission (e.g. OAR scheduler)
        :returns JSONObject
        """
        return json.loads(self.method('experiments/%s?resources' % expid))

    def get_experiment_resources_id(self, expid):
        """ Get user experiment resources list description.

        :param id: experiment id submission (e.g. OAR scheduler)
        :returns JSONObject
        """
        return json.loads(self.method('experiments/%s?id' % expid))

    def get_experiment_state(self, expid):
        """ Get user experiment state.

        :param id: experiment id submission (e.g. OAR scheduler)
        :returns JSONObject
        """
        return json.loads(self.method('experiments/%s?state' % expid))

    def get_experiment_archive(self, expid):
        """ Get user experiment archive (tar.gz) with description
        and firmware(s).

        :param id: experiment id submission (e.g. OAR scheduler)
        :returns File
        """
        return json.loads(self.method('experiments/%s?data' % expid))

    def stop_experiment(self, expid):
        """ Stop user experiment.

        :param id: experiment id submission (e.g. OAR scheduler)
        """
        return json.loads(self.method('experiments/%s' % expid),
                          method='DELETE')

    def node_command(self, command, expid, nodes=()):
        """ Lanch 'command' on user experiment list nodes

        :param id: experiment id submission (e.g. OAR scheduler)
        :param nodes: list of nodes, if empty apply on all nodes
        :returns: dict
        """
        return json.loads(self.method(
            'experiments/%s/nodes?%s' % (expid, command),
            method='POST', data=json.dumps(nodes)))

    def node_update(self, expid, files):
        """ Launch upadte command (flash firmware) on user
        experiment list nodes

        :param id: experiment id submission (e.g. OAR scheduler)
        :param files: nodes list description and firmware
        :type files: dict
        :returns: dict
        """
        return json.loads(self.method('experiments/%s/nodes?update' % expid,
                                      method='MULTIPART', data=files))
