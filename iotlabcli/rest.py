# -*- coding:utf-8 -*-
"""Rest API class"""

import requests
import json
import sys
from requests.auth import HTTPBasicAuth
from urlparse import urljoin

from iotlabcli import helpers

API_URL = helpers.read_api_url_file() or 'https://www.iot-lab.info/rest/'


class Encoder(json.JSONEncoder):
    """ Encoder for serialization object python to JSON format """
    def default(self, obj):
        return obj.__dict__


class Api(object):
    """
    REST API
    """
    def __init__(self, url=API_URL, username=None, password=None, parser=None):
        """
        :param url: url of API.
        :param username: username for Basic password auth
        :param password: password for Basic auth
        :param parser: command-line parser
        """

        self.url = url
        username, password = helpers.get_user_credentials(username,
                                                          password, parser)
        self.auth = HTTPBasicAuth(username, password)

    def method(self, url, method='GET', data=None):
        """
        :param url: url of API.
        :param method: request method
        :param data: request data
        """
        method_url = urljoin(self.url, url)
        if method == 'POST':
            headers = {'content-type': 'application/json'}
            req = requests.post(method_url, data=data, headers=headers,
                                auth=self.auth)
        elif method == 'MULTIPART':
            req = requests.post(method_url, files=data, auth=self.auth)
        elif method == 'DELETE':
            req = requests.delete(method_url, auth=self.auth)
        else:
            req = requests.get(method_url, auth=self.auth)

        if req.status_code != requests.codes.ok:
            # we have HTTP error (code != 200)
            print "HTTP error code : %s \n%s" % (req.status_code, req.text)
            sys.exit()

        return req.content  # .content to handle file return values

    def get_sites(self):
        """ Get testbed sites description

        :returns JSONObject
        """
        return self.method('experiments?sites')

    def get_resources(self, site=None):
        """ Get testbed resources description

        :returns JSONObject
        """
        if site is not None:
            return self.method('experiments?resources&site=%s' % site)
        else:
            return self.method('experiments?resources')

    def get_resources_id(self, site=None):
        """ Get testbed resources state description

        :returns JSONObject
        """
        if site is not None:
            return self.method('experiments?id&site=%s' % site)
        else:
            return self.method('experiments?id')

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
        self.method('profiles/%s' % name, method='POST', data=profile)

    def del_profile(self, name):
        """ Delete user profile

        :param profile_name: name
        :type profile_name: string
        """
        self.method('profiles/%s' % name, method='DELETE')

    def submit_experiment(self, files):
        """ Submit user experiment

        :param files: experiment description and firmware(s)
        :type files: dictionnary
        :returns JSONObject
        """
        return self.method('experiments', method='MULTIPART', data=files)

    def get_experiments(self, queryset):
        """ Get user's experiment
        :param queryset: queryset with state, limit and offset attribute
        :type queryset: string
        :returns JSONObject
        """
        return self.method('experiments?%s' % queryset)

    def get_experiments_total(self):
        """ Get the number of past, running and upcoming user's experiment.

        :returns JSONObject
        """
        return self.method('experiments?total')

    def get_experiment(self, expid):
        """ Get user experiment description.

        :param id: experiment id submission (e.g. OAR scheduler)
        :type id: string
        :returns JSONObject
        """
        return self.method('experiments/%s' % expid)

    def get_experiment_resources(self, expid):
        """ Get user experiment resources list description.

        :param id: experiment id submission (e.g. OAR scheduler)
        :type id: string
        :returns JSONObject
        """
        return self.method('experiments/%s?resources' % expid)

    def get_experiment_resources_id(self, expid):
        """ Get user experiment resources list description.

        :param id: experiment id submission (e.g. OAR scheduler)
        :type id: string
        :returns JSONObject
        """
        return self.method('experiments/%s?id' % expid)

    def get_experiment_state(self, expid):
        """ Get user experiment state.

        :param id: experiment id submission (e.g. OAR scheduler)
        :type id: string
        :returns JSONObject
        """
        return self.method('experiments/%s?state' % expid)

    def get_experiment_archive(self, expid):
        """ Get user experiment archive (tar.gz) with description
        and firmware(s).

        :param id: experiment id submission (e.g. OAR scheduler)
        :type id: string
        :returns File
        """
        return self.method('experiments/%s?data' % expid)

    def stop_experiment(self, expid):
        """ Stop user experiment.

        :param id: experiment id submission (e.g. OAR scheduler)
        :type id: string
        """
        self.method('experiments/%s' % expid, method='DELETE')

    def start_command(self, expid, nodes):
        """ Launch start command on user experiment list nodes

        :param id: experiment id submission (e.g. OAR scheduler)
        :type id: string
        :param nodes: list of nodes
        :type nodes: JSONArray
        :returns JSONObject
        """
        return self.method('experiments/%s/nodes?start' % expid,
                           method='POST', data=nodes)

    def stop_command(self, expid, nodes):
        """ Launch stop command on user experiment list nodes

        :param id: experiment id submission (e.g. OAR scheduler)
        :type id: string
        :param nodes: list of nodes
        :type nodes: JSONArray
        :returns JSONObject
        """
        return self.method('experiments/%s/nodes?stop' % expid,
                           method='POST', data=nodes)

    def reset_command(self, expid, nodes):
        """ Launch reset command on user experiment list nodes

        :param id: experiment id submission (e.g. OAR scheduler)
        :type id: string
        :param nodes: list of nodes
        :type nodes: JSONArray
        :returns JSONObject
        """
        return self.method('experiments/%s/nodes?reset' % expid,
                          method='POST', data=nodes)

    def update_command(self, expid, files):
        """ Launch upadte command (flash firmware) on user
        experiment list nodes

        :param id: experiment id submission (e.g. OAR scheduler)
        :type id: string
        :param files: nodes list description and firmware
        :type files: dictionnary
        :returns JSONObject
        """
        return self.method('experiments/%s/nodes?update' % expid,
                          method='MULTIPART', data=files)
