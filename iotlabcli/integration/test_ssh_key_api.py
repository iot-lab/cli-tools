import pytest

from iotlabcli import rest
from iotlabcli import auth

pytestmark = pytest.mark.usefixtures("save_orig_keys")


def test_get_ssh_keys(api):
    api.get_ssh_keys()

def test_set_ssh_keys(api):
    keys_json = api.get_ssh_keys()
    api.set_ssh_keys(keys_json)
    new_keys = api.get_ssh_keys()
    assert new_keys == keys_json

def test_clear_ssh_keys(api):
    no_keys = {"sshkeys": []}
    api.set_ssh_keys(no_keys)
    res = api.get_ssh_keys()
    res = res["sshkeys"]
    assert res[0] == ""

def test_max_ssh_keys(api):
    max_5_keys = fake_ssh_keys(5)
    api.set_ssh_keys(max_5_keys)
    res = api.get_ssh_keys()
    assert res == max_5_keys

def test_ssh_keys_overflow(api):
    max_5_keys = fake_ssh_keys(6)
    api.set_ssh_keys(max_5_keys)
    res = api.get_ssh_keys()
    max_5_keys["sshkeys"].pop()
    assert res == max_5_keys

def test_install_key_user_key(api, user_key):
    clear_keys(api)
    api.install_ssh_key()
    res = api.get_ssh_keys()
    res = res["sshkeys"]
    assert res[0] == user_key

def test_install_key_user_key_again(api, user_key):
    clear_keys(api)
    api.install_ssh_key()
    api.install_ssh_key()
    res = api.get_ssh_keys()
    res = res["sshkeys"]
    assert res[0] == user_key
    assert len(res) == 1

def test_install_key_from_file(api, user_key):
    clear_keys(api)
    api.install_ssh_key("~/.ssh/id_rsa.pub")
    res = api.get_ssh_keys()
    res = res["sshkeys"]
    assert res[0] == user_key

def test_install_key_round_robin(api, user_key):
    max_5_keys = fake_ssh_keys(5)
    api.set_ssh_keys(max_5_keys)

    api.install_ssh_key()
    res = api.get_ssh_keys()
    res = res["sshkeys"]
    assert res[4] == user_key
    assert res[3] == "key-4"


@pytest.fixture(scope="module")
def api():
    user, password = auth.get_user_credentials()
    return rest.Api(user, password)

@pytest.fixture(scope="module")
def save_orig_keys(api):
    orig_keys = api.get_ssh_keys()
    yield orig_keys
    api.set_ssh_keys(orig_keys)

@pytest.fixture
def clear_keys(api):
    no_keys = {"sshkeys": []}
    api.set_ssh_keys(no_keys)

@pytest.fixture
def user_key():
    return open(rest.ssh_key.KEY_FILE).read()

def fake_ssh_keys(nb):
    return {"sshkeys": [ "key-"+str(i) for i in range(nb) ]}
