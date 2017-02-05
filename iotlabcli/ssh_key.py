import os
import requests


def install_ssh_key(api, key_file):
    """Install ssh key into user's iot-lab account on www.iot-lab.info"""

    keys_json = api.get_ssh_keys()
    the_key = open(key_file).read()

    ssh_keys = keys_json["sshkeys"]
    if the_key in ssh_keys:
        print("key already registered, not re-registering.")
        return keys_json

    ssh_keys.append(the_key)
    fixup_ssh_keys(ssh_keys)

    api.set_ssh_keys(keys_json)
    return keys_json


def fixup_ssh_keys(ssh_keys):
    if "" in ssh_keys : # handle server peculiarity
        ssh_keys.remove("")

    if len(ssh_keys) > 6: # round-robin on last 3 keys
        ssh_keys.remove(ssh_keys[3])


def get_local_public_key():
    key_files = os.environ["HOME"] + "/.ssh/id_{key_type}.pub"
    for key_type in [ "rsa", "dsa" ]:
        fname = key_files.format(key_type=key_type)
        if os.path.exists(fname):
            return fname

KEY_FILE = get_local_public_key()

URL = "https://www.iot-lab.info/rest/users/{login}/sshkeys"

class Api():

    def __init__(self, user, password):
        self.url = URL.format(login=user)
        self.auth = (user, password)

    def get_ssh_keys(self):
        res = requests.get(self.url, auth=self.auth)
        res.raise_for_status()
        return res.json()
    
    def set_ssh_keys(self, keys_json):
        res = requests.put(self.url, auth=self.auth,
             headers={"content-type": "application/json"},
             json=keys_json, 
        )
        res.raise_for_status()
