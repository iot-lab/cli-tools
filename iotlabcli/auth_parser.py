
# -*- coding:utf-8 -*-
"""Authentication parser"""

import argparse
import sys
from argparse import RawTextHelpFormatter

from iotlabcli import parser_common
import iotlabcli.helpers
import iotlabcli.help_parser


def parse_options():
    """
    Handle profile-cli command-line options with argparse
    """
    parent_parser = parser_common.base_parser(user_required=True)
    # We create top level parser
    parser = argparse.ArgumentParser(
        parents=[parent_parser], formatter_class=RawTextHelpFormatter,
        description=iotlabcli.help_parser.AUTH_PARSER)

    return parser


def store_credentials(username, password=None):
    """ Store authentication credentials

    :param username: username to store
    :param password: password to store. If None, request it on command line.
    """
    if password is None:
        password = iotlabcli.helpers.password_prompt()
    iotlabcli.helpers.create_password_file(username, password)
    return 'Written'


def auth_parse_and_run(opts):
    """ Parse namespace 'opts' object and execute requested command
    :returns: result object
    """
    return store_credentials(opts.username, opts.password)


def main(args=sys.argv[1:]):
    """ Main command-line execution loop." """
    parser = parse_options()
    parser_common.main_cli(auth_parse_and_run, parser, args)
