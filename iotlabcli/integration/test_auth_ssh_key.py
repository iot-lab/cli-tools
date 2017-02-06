import pytest

import shlex
import subprocess


def test_add_user_key():
    run("auth-cli -k")
    run("auth-cli --user-key")

def test_add_key_from_path():
    run("auth-cli --key ~/.ssh/id_rsa.pub")

def test_missing_keyfile_arg():
    with pytest.raises(Exception):
        run("auth-cli --key")

def test_keyfile_not_found():
    with pytest.raises(Exception):
        run("auth-cli --key /ssh/key/file/not/found")


def run(cmd):
    cmd = shlex.split(cmd)
    ret = subprocess.check_output(cmd)
    return ret
