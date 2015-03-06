# -*- coding:utf-8 -*-
"""Authentication parser"""

from __future__ import print_function
import argparse
import sys
import getpass
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
