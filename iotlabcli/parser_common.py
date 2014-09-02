# -*- coding:utf-8 -*-

""" Common parsing methods """

import argparse
from iotlabcli import VERSION
from iotlabcli import rest


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


class Platform(object):
    _sites = None

    def __init__(self):
        if Platform._sites is not None:
            return
        sites_dict = rest.Api.get_sites()
        Platform._sites = [site["site"] for site in sites_dict["items"]]

    def sites(self):
        """ return platform sites dict """
        return self._sites
