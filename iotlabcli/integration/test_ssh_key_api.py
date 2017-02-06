import pytest

from iotlabcli import rest
from iotlabcli import auth


def test_get_ssh_keys(api):
    api.get_ssh_keys()

def test_set_ssh_keys(api):
    keys_json = api.get_ssh_keys()
    api.set_ssh_keys(keys_json)
    new_keys = api.get_ssh_keys()
    assert new_keys == keys_json

def test_clear_ssh_keys(api, save_orig_keys):
    no_keys = {"sshkeys": []}
    api.set_ssh_keys(no_keys)
    res = api.get_ssh_keys()
    res = res["sshkeys"]
    assert res[0] == ""


@pytest.fixture
def api():
    user, password = auth.get_user_credentials()
    return rest.Api(user, password)

@pytest.fixture
def save_orig_keys(api):
    orig_keys = api.get_ssh_keys()
    yield orig_keys
    api.set_ssh_keys(orig_keys)
