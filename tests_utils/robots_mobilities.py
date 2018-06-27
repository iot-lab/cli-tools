import json

import time
from urllib2 import HTTPError

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

mobility_name = 'random'
# mobility_name = 'manhattan'
# mobility_name = 'controlled'

# update to this mobility after 30s
updated_mobility_name = 'my_circuit'

# get all mobilities
print('site mobilities:')
# site_mobilities = api.method('robots/mobility', method='get')[site]
pprint.pprint(api.method('mobilities', method='get'))

# get mobility with random script
print('random mobility:')
pprint.pprint(api.method('mobilities/%s/%s' % (site, mobility_name), method='get'))

print('get map config:')
pprint.pprint(api.method('mobilities/%s/map/config' % site, method='get'))


def delete_if_exists(mob_name):
    try:
        pprint.pprint(api.method('mobilities/%s' % mob_name, method='delete'))
    except HTTPError:
        print('OK, mobility already deleted')


print('add my_circuit user defined circuit mobility:')
delete_if_exists('my_circuit')
files = iotlabcli.helpers.FilesDict()
files['mobility'] = read_file('my_circuit.json', 'b')
pprint.pprint(api.method('mobilities/', method='post', files=files))

print('add my_model user defined model mobility:')
delete_if_exists('my_model')
files = iotlabcli.helpers.FilesDict()
files['mobility'] = read_file('my_model/my_model.json','b')
files['mobility_script'] = read_file('my_model/my_model.py','b')
pprint.pprint(api.method('mobilities/', method='post', files=files))

experiments = get_active_experiments(api)

nodes_list = ['m3-%u.%s.iot-lab.info' % (num, site) for num in [205]]

if 'Running' in experiments:
    exp_id = experiments['Running'][0]
else:
    print('use mobility %s ' % mobility_name)
    exp_d = [experiment.exp_resources(nodes_list, mobility=mobility_name)]
    submitted = submit_experiment(api, 'test-robot-mobilities', 5, resources=exp_d)
    pprint.pprint(submitted)

    exp_id = submitted['id']

    print('wait experiment in Running...')
    wait_experiment(api, exp_id)

    # 30 s of the circuit
    print('30 s of mobility %s' % mobility_name)
    time.sleep(30)

iotlabcli.experiment.wait_experiment(api, exp_id)

print('update to %s' % updated_mobility_name)
pprint.pprint(api.method('experiments/{id}/robots/mobility/{site}/{name}'.format(id=exp_id,
                                                                   site=site,
                                                                   name=updated_mobility_name),
                         method='post', json=nodes_list))
