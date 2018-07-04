import json
from urllib2 import HTTPError

import iotlabcli
import pprint
from iotlabcli import Api

username, password = iotlabcli.auth.get_user_credentials()

api = Api(username, password)
api.url = "https://devwww.iot-lab.info/api/"

site = 'devlille'


def delete_if_exists(circuit_name):
    try:
        pprint.pprint(api.method('mobilities/circuits/%s' % circuit_name, method='delete'))
    except HTTPError:
        print('OK, circuit already deleted')


# get all circuits
print('all circuits:')
pprint.pprint(api.method('mobilities/circuits', method='get', params={'filter': 'all'}))
print('userdefined circuits:')
pprint.pprint(api.method('mobilities/circuits', method='get', params={'filter': 'userdefined'}))
print('predefined circuits:')
pprint.pprint(api.method('mobilities/circuits', method='get', params={'filter': 'predefined'}))

print('add my_circuit user defined circuit:')
delete_if_exists('my_circuit')
circuit = json.load(open('my_circuit.json', 'r'))
pprint.pprint(api.method('mobilities/circuits', method='post', json=circuit))

print('userdefined circuits:')
pprint.pprint(api.method('mobilities/circuits', method='get', params={'filter': 'userdefined'}))

print('get map config:')
pprint.pprint(api.method('robots/%s/map/config' % site, method='get'))

print('get dock config:')
pprint.pprint(api.method('robots/%s/dock/config' % site, method='get'))

print('is_reachable:')
pprint.pprint(api.method('robots/%s/is_reachable' % site,
                         json={'x': 20, 'y': 4},
                         method='post'))
print('are_reachable:')
pprint.pprint(api.method('robots/%s/are_reachable' % site,
                         json=[{'x': 20, 'y': 4}, {'x': 20, 'y': 5}],
                         method='post'))

print('original_coordinates:')
original_coordinates = {'x': 20, 'y': 4, }
pprint.pprint(original_coordinates)

print('to_map_coordinates:')
to_map_coordinates = api.method('robots/%s/coordinates/to_map_coordinates' % site,
                                json=original_coordinates,
                                method='post')
pprint.pprint(to_map_coordinates)

print('back to_ros_coordinates:')
pprint.pprint(api.method('robots/%s/coordinates/to_ros_coordinates' % site,
                         json=to_map_coordinates,
                         method='post'))
