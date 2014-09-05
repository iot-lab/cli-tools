# -*- coding:utf-8 -*-

""" Common parsing methods """

import sys
import argparse
import json
from iotlabcli import VERSION
from iotlabcli import rest
from iotlabcli import Error


def base_parser(user_required=False):
    """ Base parser giving 'user' 'password' and 'version' arguments
    :param user_required: set 'user' argument as required or not """
    parser = argparse.ArgumentParser(add_help=False)
    add_auth_arguments(parser, user_required)
    add_version(parser)

    return parser


def add_auth_arguments(parser, usr_required=False):
    """ Add 'user' and 'password' arguments
    :param user_required: set 'user' argument as required or not  """
    parser.add_argument('-u', '--user', dest='username', required=usr_required)
    parser.add_argument('-p', '--password', dest='password')


def add_version(parser):
    """ Add 'version' argument """
    parser.add_argument('-v', '--version', action='version', version=VERSION)


def main_cli(function, parser, args=sys.argv[1:]):
    """ Main command-line execution." """
    try:
        parser_opts = parser.parse_args(args)
        result = function(parser_opts)
        print json.dumps(result, indent=4, sort_keys=True)
    except Error as err:
        parser.error(str(err))
    except KeyboardInterrupt:
        print >> sys.stderr, "\nStopped."
        sys.exit()


class Singleton(object):
    _sites = None
    _current_alias = 0

    def __init__(self):
        if Singleton._sites is not None:
            return
        sites_dict = rest.Api.get_sites()
        Singleton._sites = [site["site"] for site in sites_dict["items"]]

    def sites(self):
        """ return platform sites dict """
        return self._sites

    @staticmethod
    def new_alias():
        Singleton._current_alias += 1
        return Singleton._current_alias
