# -*- coding:utf-8 -*-
"""Authentication parser"""

import argparse
import sys
import getpass
from argparse import RawTextHelpFormatter

from iotlabcli.parser import common
import iotlabcli.auth
from iotlabcli.parser import help_msgs


def parse_options():
    """ Handle profile-cli command-line options with argparse """
    parent_parser = common.base_parser(user_required=True)
    # We create top level parser
    parser = argparse.ArgumentParser(
        parents=[parent_parser], formatter_class=RawTextHelpFormatter,
        description=help_msgs.AUTH_PARSER)

    return parser


def auth_parse_and_run(opts):
    """ Parse namespace 'opts' object and execute requested command
    :returns: result object
    """
    password = opts.password or password_prompt()
    iotlabcli.auth.write_password_file(opts.username, password)
    return 'Written'


def password_prompt():
    """ password prompt when command-line option username (e.g. -u or --user)
    is used without password

    :returns password
    """
    pprompt = lambda: (getpass.getpass(), getpass.getpass('Retype password: '))
    prompt1, prompt2 = pprompt()
    while prompt1 != prompt2:  # pragma: no cover
        print 'Passwords do not match. Try again'
        prompt1, prompt2 = pprompt()
    return prompt1


def main(args=sys.argv[1:]):
    """ Main command-line execution loop." """
    parser = parse_options()
    common.main_cli(auth_parse_and_run, parser, args)
