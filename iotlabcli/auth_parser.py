
# -*- coding:utf-8 -*-
"""Authentication parser"""

import argparse
import sys
from argparse import RawTextHelpFormatter

from iotlabcli import Error
from iotlabcli import helpers, help_parser, parser_common


def parse_options():
    """
    Handle profile-cli command-line options with argparse
    """
    parent_parser = parser_common.base_parser(user_required=True)
    # We create top level parser
    parser = argparse.ArgumentParser(description=help_parser.AUTH_PARSER,
                                     parents=[parent_parser],
                                     formatter_class=RawTextHelpFormatter)

    return parser


def store_credentials(username, password=None):
    """ Store authentication credentials

    :param username: username to store
    :param password: password to store. If None, request it on command line.
    """
    if password is None:
        password = helpers.password_prompt()
    helpers.create_password_file(username, password)


def main(args=sys.argv[1:]):
    """
    Main command-line execution loop.
    """
    parser = parse_options()
    try:
        parser_options = parser.parse_args(args)
        store_credentials(parser_options.username, parser_options.password)
    except Error as err:
        parser.error(str(err))
    except KeyboardInterrupt:
        print >> sys.stderr, "\nStopped."
        sys.exit()
