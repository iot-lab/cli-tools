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


def add_nodes_selection_list(parser):
    """ Add '-l' and '-e' experiment nodes selection """
    list_group = parser.add_mutually_exclusive_group()

    list_group.add_argument(
        '-e', '--exclude', action='append', type=nodes_list_from_str,
        dest='exclude_nodes_list', help='exclude nodes list')
    list_group.add_argument(
        '-l', '--list', action='append', type=nodes_list_from_str,
        dest='nodes_list', help='nodes list')


def list_nodes(api, exp_id, nodes_ll=None, excl_nodes_ll=None):
    """ Return the list of nodes where the command will apply """

    if nodes_ll is not None:
        # flatten lists into one
        nodes = list(itertools.chain.from_iterable(nodes_ll))

    elif excl_nodes_ll is not None:
        # flatten lists into one
        excl_nodes = set(itertools.chain.from_iterable(excl_nodes_ll))

        # remove exclude nodes from experiment nodes
        exp_nodes = set(_get_experiment_nodes_list(api, exp_id))
        nodes = list(exp_nodes - excl_nodes)
    else:
        nodes = []  # all the nodes

    return sorted(nodes, key=helpers.node_url_sort_key)


def _get_experiment_nodes_list(api, exp_id):
    """ Get the nodes_list for given experiment"""
    exp_resources = api.get_experiment_info(exp_id, 'resources')
    exp_nodes = [res["network_address"] for res in exp_resources["items"]]
    return exp_nodes


def nodes_list_from_str(nodes_list_str):
    """ Convert the nodes_list_str to a list of nodes hostname
    Checks that given site exist
    :param nodes_list_str: short nodes format: site_name,archi,node_id_list
                           example: 'grenoble,m3,1-34+72'
    :returns: ['m3-1.grenoble.iot-lab.info', ...]
    """
    try:
        # 'grenoble,m3,1-34+72' -> ['grenoble', 'm3', '1-34+72']
        site, archi, nodes_str = nodes_list_str.split(',')
    except ValueError:
        raise argparse.ArgumentTypeError(
            'Invalid number of argument in nodes list: %r' % nodes_list_str)
    check_site_with_server(site)  # needs an external request
    return nodes_list_from_info(site, archi, nodes_str)
