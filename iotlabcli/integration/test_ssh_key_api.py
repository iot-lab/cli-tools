import pytest

from iotlabcli import rest
from iotlabcli import auth


def test_get_ssh_keys(api):
    api.get_ssh_keys()

def test_set_ssh_keys(api):
    keys_json = api.get_ssh_keys()
    api.set_ssh_keys(keys_json)


@pytest.fixture
def api():
    user, password = auth.get_user_credentials()
    return rest.Api(user, password)
