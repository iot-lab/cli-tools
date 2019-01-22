import json

from urllib2 import HTTPError


import iotlabcli
import pprint
from iotlabcli import Api

username, password = iotlabcli.auth.get_user_credentials()

api = Api(username, password)
api.url = "https://devwww.iot-lab.info/api/"

print('all models no type parameter:')
pprint.pprint(api.method('mobilities/models', method='get'))

print('all models:')
pprint.pprint(api.method('mobilities/models?type=ALL', method='get'))

print('userdefined models:')
pprint.pprint(api.method('mobilities/models?type=USERDEFINED', method='get'))

print('predefined models:')
pprint.pprint(api.method('mobilities/models?type=PREDEFINED', method='get'))

print('predefined model random:')
pprint.pprint(api.method('mobilities/models/random', method='get'))


def delete_if_exists(model_name):
    try:
        pprint.pprint(api.method('mobilities/models/%s' % model_name, method='delete'))
    except HTTPError, ex:
        print('OK, model already deleted')


print('add my_model user defined model mobility:')
delete_if_exists('my_model')
delete_if_exists('modified_my_model')

files = iotlabcli.helpers.FilesDict()
model = json.load(open('my_model/my_model.json', 'r'))
files.add_file('my_model/my_model.json')
files.add_file('my_model/my_model.py')
pprint.pprint(api.method('mobilities/models', method='post', files=files))

print('userdefined models:')
pprint.pprint(api.method('mobilities/models?type=USERDEFINED', method='get'))

print("my_model file")
pprint.pprint(api.method('mobilities/models/my_model/file', method='get', raw=True))

print("rename my_model to modified_my_model")
files = iotlabcli.helpers.FilesDict()
model['name'] = 'modified_my_model'
files['mobility'] = json.dumps(model)
files.add_file('my_model/my_model.py')
pprint.pprint(api.method('mobilities/models/my_model', method='put', files=files))

print('userdefined model modified_my_model:')
pprint.pprint(api.method('mobilities/models/modified_my_model', method='get'))

print('userdefined models:')
pprint.pprint(api.method('mobilities/models?type=USERDEFINED', method='get'))

print('modify the modified_my_model script extra file')
files = iotlabcli.helpers.FilesDict()
files['mobility'] = json.dumps(model)
files.add_file('my_model/modified_my_model.py')
pprint.pprint(api.method('mobilities/models/modified_my_model', method='put', files=files))

print("modified_my_model file")
pprint.pprint(api.method('mobilities/models/modified_my_model/file', method='get', raw=True))
