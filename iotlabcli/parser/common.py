# -*- coding:utf-8 -*-

""" Common parsing methods """

from __future__ import print_function
import sys
import argparse
from iotlabcli import VERSION, json_dumps
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


def main_cli(function, parser, args=None):  # flake8: noqa
    """ Main command-line execution. """
    args = args or sys.argv[1:]
    try:
        parser_opts = parser.parse_args(args)
        result = function(parser_opts)
        print(json_dumps(result))
    except (IOError, ValueError) as err:
        parser.error(str(err))
    except RuntimeError as err:
        print("RuntimeError:\n{err!s}".format(err=err), file=sys.stderr)
        sys.exit()
    except KeyboardInterrupt:  # pragma: no cover
        print("\nStopped.", file=sys.stderr)
        sys.exit()


def sites_list():
    """ Return the list of sites """
    sites_dict = rest.Api.get_sites()
    return [site["site"] for site in sites_dict["items"]]


def check_site_with_server(site_name, _sites_list=None):
    """ Check if the given site exists by requesting the server list.
    If sites_list is given, it is used instead of doing a remote request

    >>> sites = ["strasbourg", "grenoble"]
    >>> check_site_with_server("grenoble", sites)
    >>> check_site_with_server("unknown", sites)  \
        # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ArgumentTypeError: Unknown site name 'unknown'
    """
    sites = _sites_list or sites_list()
    if site_name in sites:
        return  # site_name is valid
    raise argparse.ArgumentTypeError("Unknown site name %r" % site_name)
