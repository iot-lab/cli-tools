# -*- coding:utf-8 -*-

""" Common parsing methods """

from __future__ import print_function
import sys
import argparse
import itertools
import iotlabcli
from iotlabcli import helpers
from iotlabcli import rest
DOMAIN_DNS = 'iot-lab.info'
try:
    # pylint: disable=import-error,no-name-in-module
    from urllib.error import HTTPError
except ImportError:  # pragma: no cover
    # pylint: disable=import-error,no-name-in-module
    from urllib2 import HTTPError


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
    parser.add_argument(
        '-v', '--version', action='version', version=iotlabcli.__version__)


def main_cli(function, parser, args=None):  # flake8: noqa
    """ Main command-line execution. """
    args = args or sys.argv[1:]
    try:
        parser_opts = parser.parse_args(args)
        result = function(parser_opts)
        print(helpers.json_dumps(result))
        return

    except HTTPError as err:  # should be first as it's an IOError
        if 401 == err.code:
            # print an info on how to get rid of the error
            err = ("HTTP Error 401: Unauthorized: Wrong login/password\n\n"
                   "\tRegister your login:password using `auth-cli`\n")
        print(err, file=sys.stderr)

    except (IOError, ValueError) as err:
        parser.error(str(err))
    except RuntimeError as err:
        print("RuntimeError:\n{err!s}".format(err=err), file=sys.stderr)

    except KeyboardInterrupt:  # pragma: no cover
        print("\nStopped.", file=sys.stderr)
    sys.exit(1)


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


def nodes_list_from_info(site, archi, nodes_str):
    """ Cheks archi, nodes_str format and return nodes list

    >>> nodes_list_from_info('grenoble', 'm3', '1-4+6+7-8')
    ['m3-1.grenoble.iot-lab.info', 'm3-2.grenoble.iot-lab.info', \
'm3-3.grenoble.iot-lab.info', 'm3-4.grenoble.iot-lab.info', \
'm3-6.grenoble.iot-lab.info', 'm3-7.grenoble.iot-lab.info', \
'm3-8.grenoble.iot-lab.info']

    >>> nodes_list_from_info('grenoble', 'm3', '1-4-5')
    Traceback (most recent call last):
    ValueError: Invalid nodes list: 1-4-5 ([0-9+-])

    >>> nodes_list_from_info('grenoble', 'wsn430', 'a-b')
    Traceback (most recent call last):
    ValueError: Invalid nodes list: a-b ([0-9+-])

    >>> nodes_list_from_info('grenoble', 'inval_arch', '1-2')
    Traceback (most recent call last):
    ValueError: Invalid node archi: 'inval_arch' not in ['wsn430', 'm3', 'a8']
    """

    _check_archi(archi)
    nodes_list = nodes_id_list(archi, nodes_str)
    fmt = "%s.{site}.{domain}".format(site=site, domain=DOMAIN_DNS)
    nodes_url_list = [fmt % node for node in nodes_list]
    return nodes_url_list


def _check_archi(archi):
    """ Check that archi is valid
    >>> [_check_archi(archi) for archi in ['wsn430', 'm3', 'a8']]
    [None, None, None]

    >>> _check_archi('msp430')
    Traceback (most recent call last):
    ValueError: Invalid node archi: 'msp430' not in ['wsn430', 'm3', 'a8']

    """

    archi_list = ['wsn430', 'm3', 'a8']
    if archi in archi_list:
        return  # valid archi
    raise ValueError("Invalid node archi: %r not in %s" % (archi, archi_list))


def nodes_id_list(archi, nodes_list):
    """ Expand short nodes_list 'archi', '1-5+6+8-12'
    to a regular nodes list
    """

    nodes_num_list = expand_short_nodes_list(nodes_list)

    node_fmt = '{archi}-%u'.format(archi=archi)
    nodes = [node_fmt % num for num in nodes_num_list]

    return nodes


def _expand_minus_str(minus_nodes_str):
    """ Expand a '1-5' or '6' string to a list on integer
    :raises: ValueError on invalid values
    """
    minus_node = minus_nodes_str.split('-')
    if len(minus_node) == 1:
        # ['6']
        return [int(minus_node[0])]
    else:
        # ['1', '4'] or ['7', '8']
        first, last = minus_node
        nodes_range = range(int(first), int(last) + 1)
        # first >= last
        if len(nodes_range) <= 1:
            raise ValueError

        # Add nodes range
        return nodes_range


def expand_short_nodes_list(nodes_str):
    """ Expand short nodes_list '1-5+6+8-12' to a regular nodes list

    >>> expand_short_nodes_list('1-4+6+7-8')
    [1, 2, 3, 4, 6, 7, 8]

    >>> expand_short_nodes_list('1-4-5')
    Traceback (most recent call last):
    ValueError: Invalid nodes list: 1-4-5 ([0-9+-])

    >>> expand_short_nodes_list('3-3')
    Traceback (most recent call last):
    ValueError: Invalid nodes list: 3-3 ([0-9+-])

    >>> expand_short_nodes_list('3-2')
    Traceback (most recent call last):
    ValueError: Invalid nodes list: 3-2 ([0-9+-])

    >>> expand_short_nodes_list('a-b')
    Traceback (most recent call last):
    ValueError: Invalid nodes list: a-b ([0-9+-])
    """

    try:
        # '1-4+6+8-8'
        nodes_ll = [_expand_minus_str(minus_nodes_str) for minus_nodes_str in
                    nodes_str.split('+')]
        # [[1, 2, 3], [6], [12]]
        return list(itertools.chain.from_iterable(nodes_ll))  # flatten
    except ValueError:
        # invalid: 6-3 or 6-7-8 or non int values
        raise ValueError('Invalid nodes list: %s ([0-9+-])' % nodes_str)
