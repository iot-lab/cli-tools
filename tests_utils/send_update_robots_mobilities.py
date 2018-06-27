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

experiments = get_active_experiments(api)

nodes_list = ['m3-%u.%s.iot-lab.info' % (num, site) for num in [205]]

exp_id = experiments['Running'][0]

iotlabcli.experiment.wait_experiment(api, exp_id)

print('update to %s' % updated_mobility_name)
pprint.pprint(api.method('experiments/{id}/robots/mobility/{site}/{name}'.format(id=exp_id,
                                                                   site=site,
                                                                   name=updated_mobility_name),
                         method='post', json=nodes_list))
