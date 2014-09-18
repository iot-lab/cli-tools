# -*- coding:utf-8 -*-
""" Authentication file management """

import os
import getpass
import base64

HOME_DIRECTORY = os.getenv('USERPROFILE') or os.getenv('HOME')
RC_FILE = os.path.join(HOME_DIRECTORY, '.iotlabrc')


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
    with open(RC_FILE, 'wb') as pass_file:
        pass_file.write('%s:%s' % (username, base64.b64encode(password)))


def _read_password_file():
    """ Try to read password file (.iotlabrc) in user home directory when
    command-line option username and password are not used. If password
    file exist whe return username and password for basic auth http
    authentication
    """
    if not os.path.exists(RC_FILE):
        return None, None
    try:
        with open(RC_FILE, 'rb') as password_file:
            user, enc_passwd = password_file.readline().split(':')
            return user, base64.b64decode(enc_passwd)
    except ValueError:
        raise ValueError('Bad password file format: %r' % RC_FILE)
