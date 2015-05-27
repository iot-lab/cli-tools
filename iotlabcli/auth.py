# -*- coding:utf-8 -*-

# This file is a part of IoT-LAB cli-tools
# Copyright (C) 2015 INRIA (Contact: admin@iot-lab.info)
# Contributor(s) : see AUTHORS file
#
# This software is governed by the CeCILL license under French law
# and abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# http://www.cecill.info.
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

""" Authentication file management """

import os
import os.path
import getpass
from base64 import b64encode, b64decode
from iotlabcli.rest import Api

RC_FILE = (os.getenv('IOTLAB_PASSWORD_FILE') or
           os.path.expanduser('~/.iotlabrc'))


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
