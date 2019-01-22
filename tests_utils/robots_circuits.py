import json
from urllib2 import HTTPError

import iotlabcli
import pprint
from iotlabcli import Api
from iotlabcli.helpers import read_file

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

print('all circuits (no param):')
pprint.pprint(api.method('mobilities/circuits', method='get'))

print('all circuits:')
pprint.pprint(api.method('mobilities/circuits?type=ALL', method='get'))

print('userdefined circuits:')
pprint.pprint(api.method('mobilities/circuits?type=USERDEFINED', method='get'))

print('predefined circuits:')
pprint.pprint(api.method('mobilities/circuits?type=PREDEFINED', method='get'))

print('predefined circuits:')
pprint.pprint(api.method('mobilities/circuits?type=PREDEFINED&site=%s' % site, method='get'))

print('predefined circuit square1:')
pprint.pprint(api.method('mobilities/circuits/square1', method='get'))

print('add my_circuit user defined circuit:')
delete_if_exists('my_circuit')
delete_if_exists('modified_my_circuit')
circuit = json.load(open('my_circuit.json', 'r'))

pprint.pprint(api.method('mobilities/circuits', method='post', json=circuit))

# POST with the same circuit should fail
try:
    result = api.method('mobilities/circuits', method='post', json=circuit)
except HTTPError, ex:
    assert ex.code == 500

print('remove point B in my_circuit')

del circuit["coordinates"]['B']
circuit['points'].remove('B')

print('userdefined circuit my_circuit on devlille:')
pprint.pprint(api.method('mobilities/circuits/my_circuit', method='get'))

try:
    api.method('mobilities/circuits/my_circuit', method='put', json=circuit)
except HTTPError, ex:
    assert ex.code == 204

print('userdefined circuit my_circuit on devlille:')
pprint.pprint(api.method('mobilities/circuits/my_circuit', method='get'))

# rename my_circuit
circuit['name'] = 'modified_my_circuit'

try:
    api.method('mobilities/circuits/my_circuit', method='put', json=circuit)
except HTTPError, ex:
    assert ex.code == 204

print('userdefined circuit modified_my_circuit:')
pprint.pprint(api.method('mobilities/circuits/modified_my_circuit', method='get'))

print('userdefined circuits (only modified_my_circuit):')
pprint.pprint(api.method('mobilities/circuits?type=USERDEFINED', method='get'))

print('userdefined circuits on devstrasbourg:')
pprint.pprint(api.method('mobilities/circuits?site=devstrasbourg&type=USERDEFINED', method='get'))

print('predefined circuits on devstrasbourg:')
pprint.pprint(api.method('mobilities/circuits?site=devstrasbourg&type=PREDEFINED', method='get'))

print('get map config:')
pprint.pprint(api.method('robots/%s/map/config' % site, method='get'))

print('get dock config:')
pprint.pprint(api.method('robots/%s/dock/config' % site, method='get'))

print('reachable:')
pprint.pprint(api.method('robots/%s/coordinates/isreachable' % site,
                         json={'A':{'x': 20, 'y': 4}},
                         method='post'))


print('original_coordinates:')
original_coordinates = {'x': 20, 'y': 4, }
pprint.pprint(original_coordinates)

print('to_map_coordinates:')
to_map_coordinates = api.method('robots/%s/coordinates/map' % site,
                                json=original_coordinates,
                                method='post')
pprint.pprint(to_map_coordinates)

print('back to_ros_coordinates:')
pprint.pprint(api.method('robots/%s/coordinates/ros' % site,
                         json=to_map_coordinates,
                         method='post'))