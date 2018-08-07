import json

import time
from urllib2 import HTTPError
from urlparse import urljoin

from iotlabcli.helpers import read_file

from iotlabcli.robot import mobility_command

from iotlabcli.experiment import submit_experiment, wait_experiment, get_active_experiments

import iotlabcli
import pprint
from iotlabcli import Api, experiment

username, password = iotlabcli.auth.get_user_credentials()

api = Api(username, password)
api.url = "https://devwww.iot-lab.info/api/"

site = 'devlille'


print('all models:')
pprint.pprint(api.method('mobilities/models?type=all', method='get'))

print('all models no type parameter:')
pprint.pprint(api.method('mobilities/models', method='get'))

print('userdefined models:')
pprint.pprint(api.method('mobilities/models?type=userdefined', method='get'))

print('predefined models:')
pprint.pprint(api.method('mobilities/models?type=predefined', method='get'))

print('predefined model random:')
pprint.pprint(api.method('mobilities/models/random', method='get'))


def delete_if_exists(model_name):
    try:
        pprint.pprint(api.method('mobilities/models/%s' % model_name, method='delete'))
    except HTTPError:
        print('OK, model already deleted')


print('add my_model user defined model mobility:')
delete_if_exists('my_model')
files = iotlabcli.helpers.FilesDict()
model = read_file('my_model/my_model.json', 'r')
files['mobility'] = read_file('my_model/my_model.json', 'b')
files['extra'] = read_file('my_model/my_model.py', 'b')
pprint.pprint(api.method('mobilities/models', method='post', files=files))


# rename my_circuit
files['mobility']['name'] = 'modified_my_model'

req = api._request(urljoin(api.url, 'mobilities/models/my_model'), method='put', files=files)

print('userdefined model modified_my_model:')
pprint.pprint(api.method('mobilities/models/modified_my_circuit', method='get'))

print('userdefined models:')
pprint.pprint(api.method('mobilities/models?type=userdefined', method='get'))
