# -*- coding:utf-8 -*-
""" Authentication file management """

import os
import getpass
from base64 import b64encode, b64decode
from iotlabcli.rest import Api

HOME_DIRECTORY = os.getenv('USERPROFILE') or os.getenv('HOME')
RC_FILE = (os.getenv('IOTLAB_PASSWORD_FILE') or
           os.path.join(HOME_DIRECTORY, '.iotlabrc'))


def get_user_credentials(username=None, password=None):
    """ Return user credentials.
    If provided in arguments return them, if password missing, ask on console,
    or try to read them from password file """

    if (password is not None) and (username is not None):
        pass
    elif (password is None) and (username is not None):
        password = getpass.getpass()
    else:
        username, password = _read_password_file()
    return username, password


def check_user_credentials(username, password):
    """ Check that the given credentials are valid """
    api = Api(username, password)
    return api.check_credential()


def write_password_file(username, password):
    """ Create a password file for basic authentication http when
    command-line option username and password are used We write .iotlabrc
    file in user home directory with format username:base64(password)

    :param username: basic http auth username
    :type username: string
    :param password: basic http auth password
    :type password: string
    """
    assert (username is not None) and (password is not None)
    with open(RC_FILE, 'w') as pass_file:
        # encode/decode for python3
        enc_password = b64encode(password.encode('utf-8')).decode('utf-8')
        pass_file.write('{user}:{passwd}'.format(user=username,
                                                 passwd=enc_password))


def _read_password_file():
    """ Try to read password file (.iotlabrc) in user home directory when
    command-line option username and password are not used. If password
    file exist whe return username and password for basic auth http
    authentication
    """
    if not os.path.exists(RC_FILE):
        return None, None
    try:
        with open(RC_FILE, 'r') as password_file:
            username, enc_password = password_file.readline().split(':')
            # encode/decode for python3
            password = b64decode(enc_password.encode('utf-8')).decode('utf-8')
            return username, password
    except ValueError:
        raise ValueError('Bad password file format: %r' % RC_FILE)
