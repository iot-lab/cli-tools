# -*- coding: utf-8 -*-

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

""" small test for the new api iotlabclient package"""
from __future__ import print_function
from pprint import pprint

from iotlabcli import auth

from iotlabclient import Configuration, ApiClient, ExperimentsApi
from iotlabclient.rest import ApiException


def test_new_client():
    """ test the new api with iotlabclient, experiments_all_get"""
    configuration = Configuration()
    username, password = auth.get_user_credentials()
    configuration.username = username
    configuration.password = password
    configuration.host = 'https://devwww.iot-lab.info/api'

    # create an instance of the API class
    api_instance = ExperimentsApi(
        ApiClient(configuration))
    state = 'Running,Terminated,Stopped,Waiting'
    limit = 500
    offset = 0

    try:
        # Returns list of testbed experiments
        api_response = api_instance.experiments_all_get(state=state,
                                                        limit=limit,
                                                        offset=offset)
        pprint(api_response)
    except ApiException as exc:
        print("Exception when calling experiments_all_get: %s" % exc)
