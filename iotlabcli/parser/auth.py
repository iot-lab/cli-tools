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

"""Authentication parser"""

from __future__ import print_function
import sys
import getpass
import argparse
from argparse import RawTextHelpFormatter

from iotlabcli.parser import common
import iotlabcli.auth

AUTH_PARSER = """

auth-cli command-line store your credentials.
It creates a file .iotlabrc in your home directory
with username and password.

"""


def parse_options():
    """ Handle profile-cli command-line options with argparse """
    parent_parser = common.base_parser(user_required=True)
    # We create top level parser
    parser = argparse.ArgumentParser(
        parents=[parent_parser], formatter_class=RawTextHelpFormatter,
        description=AUTH_PARSER)

    return parser


def auth_parse_and_run(opts):
    """ Parse namespace 'opts' object and execute requested command
    :returns: result object
    """
    password = opts.password or getpass.getpass()
    if iotlabcli.auth.check_user_credentials(opts.username, password):
        iotlabcli.auth.write_password_file(opts.username, password)
        return 'Written'
    else:
        raise RuntimeError('Wrong login:password')


def main(args=None):
    """ Main command-line execution loop." """
    args = args or sys.argv[1:]
    parser = parse_options()
    common.main_cli(auth_parse_and_run, parser, args)
