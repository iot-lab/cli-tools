import argparse
import helpers
import json
import sys
from help_parser import *
from argparse import RawTextHelpFormatter

def parse_options():
    """
    Handle profile-cli command-line options with argparse
    """
    parent_parser = argparse.ArgumentParser(add_help=False) 
    # We create top level parser
    parser = argparse.ArgumentParser(description=AUTH_PARSER, parents=[parent_parser],
       formatter_class=RawTextHelpFormatter)
    parser.add_argument('-u','--user', required=True, dest='username')
    parser.add_argument('-p','--password', dest='password')

    return parser 

def store_credentials(parser_options, parser):
    """ Store authentication credentials. 

    :param parser_options: command-line parser options
    :type parser_options: Namespace object with options attribute
    :param request: API Rest request object
    """
    username = parser_options.username
    password = parser_options.password
    if (password is None):
       password = helpers.password_prompt()
    helpers.create_password_file(username, password, parser)

def main():
    """ 
    Main command-line execution loop.
    """
    try:
       parser = parse_options()
       parser_options = parser.parse_args()
       store_credentials(parser_options, parser)
    except KeyboardInterrupt:
        print >> sys.stderr, "\nStopped."
        sys.exit()
