from iotlabcli import auth

from iotlabclient import Configuration
import iotlabclient
from iotlabclient.rest import ApiException
from pprint import pprint


def test_new_client():
    configuration = Configuration()
    configuration.username, configuration.password = \
        auth.get_user_credentials()
    configuration.auth_settings()
    configuration.host = 'https://devwww.iot-lab.info/api'

    # create an instance of the API class
    api_instance = iotlabclient.DefaultApi(
        iotlabclient.ApiClient(configuration))
    state = 'Running,Terminated,Stopped,Waiting'
    limit = 500
    offset = 0

    try:
        # Returns list of testbed experiments
        api_response = api_instance.experiments_all_get(state=state,
                                                        limit=limit,
                                                        offset=offset)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->experiments_all_get: %s" % e)
