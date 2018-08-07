from iotlabcli.experiment import submit_experiment, get_active_experiments

import iotlabcli
import pprint
from iotlabcli import Api

username, password = iotlabcli.auth.get_user_credentials()

api = Api(username, password)
api.url = "https://devwww.iot-lab.info/api/"

site = 'devlille'

# update to this circuit
updated_circuit_name = 'my_circuit'

experiments = get_active_experiments(api)

nodes_list = ['m3-%u.%s.iot-lab.info' % (num, site) for num in [202]]

exp_id = experiments['Running'][0]

iotlabcli.experiment.wait_experiment(api, exp_id)

print('update to %s' % updated_circuit_name)
pprint.pprint(api.method('experiments/{id}/robots/mobility/{name}'.format(id=exp_id,
                                                                   site=site,
                                                                   name=updated_circuit_name),
                         method='post', json=nodes_list))
