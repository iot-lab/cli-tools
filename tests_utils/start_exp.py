from iotlabcli.experiment import submit_experiment, get_active_experiments

import iotlabcli
import pprint
from iotlabcli import Api

username, password = iotlabcli.auth.get_user_credentials()

api = Api(username, password)
api.url = "https://devwww.iot-lab.info/api/"

site = 'devlille'

circuit_name = 'my_circuit'

experiments = get_active_experiments(api)

nodes_list = ['m3-%u.%s.iot-lab.info' % (num, site) for num in [202]]


exp_d = [iotlabcli.experiment.exp_resources(nodes_list, mobility=circuit_name)]
submitted = submit_experiment(api, 'test-robot-mobilities', 60, resources=exp_d)
