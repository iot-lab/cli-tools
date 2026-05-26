# -*- coding:utf-8 -*-

# This file is a part of IoT-LAB cli-tools
# Copyright (C) 2015 INRIA (Contact: admin@iot-lab.info)
# Contributor(s) : see AUTHORS file
#
# This software is governed by the CeCILL license under French law
# and abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# http://www.cecill.info.
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

"""Common parsing methods"""

import argparse
import contextlib
import errno
import sys
from argparse import ArgumentParser
from collections import OrderedDict
from collections.abc import Callable, Generator
from typing import Any

# pylint: disable=wrong-import-order
try:
    # pylint: disable=import-error,no-name-in-module
    from urllib.error import HTTPError
except ImportError:  # pragma: no cover
    # pylint: disable=import-error,no-name-in-module
    from urllib2 import HTTPError

import jmespath

import iotlabcli
from iotlabcli import helpers, rest

DOMAIN_DNS = "iot-lab.info"


def base_parser(user_required: bool = False) -> ArgumentParser:
    """Base parser giving 'user' 'password' and 'version' arguments
    :param user_required: set 'user' argument as required or not"""
    parser = argparse.ArgumentParser(add_help=False)
    add_auth_arguments(parser, user_required)
    add_version(parser)
    add_output_formatter(parser)

    return parser


def add_auth_arguments(parser: ArgumentParser, usr_required: bool = False) -> None:
    """Add 'user' and 'password' arguments
    :param user_required: set 'user' argument as required or not"""
    parser.add_argument("-u", "--user", dest="username", required=usr_required)
    parser.add_argument("-p", "--password", dest="password")


def add_version(parser: ArgumentParser) -> None:
    """Add 'version' argument"""
    parser.add_argument(
        "-v", "--version", action="version", version=iotlabcli.__version__
    )


def add_output_formatter(parser: ArgumentParser) -> None:
    """Add '--jmespath' argument"""
    group = parser.add_argument_group("Output Format")
    group.add_argument(
        "--jmespath",
        "--jp",
        type=jmespath.compile,
        help="Query output using `jmespath` syntax",
    )
    group.add_argument(
        "--format",
        "--fmt",
        type=eval,
        help="Format function, default `helpers.json_dumps`",
    )


def add_expid_arg(parser: ArgumentParser, required: bool = False) -> None:
    """Add '-i' / '--id' for 'experiment_id' option."""
    parser.add_argument(
        "-i",
        "--id",
        dest="experiment_id",
        type=int,
        required=required,
        help="experiment id submission",
    )


class HelpAction(argparse.Action):
    """Action to provide a custom 'help' command."""

    HELPMSG = None

    def __call__(
        self,
        parser: ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: str | None = None,
    ) -> None:
        print(self.HELPMSG, end="")
        parser.exit()

    @classmethod
    def for_message(cls, msg: str) -> type["HelpAction"]:
        """Create action for help message."""

        class HelpActionWithMessage(cls):
            """Action with custom 'help' message."""

            HELPMSG = msg

        return HelpActionWithMessage

    @classmethod
    def add_help(
        cls, parser: ArgumentParser, name: str, description: str, msg: str
    ) -> None:
        """Method to add a custom help option.

        :param parser: parser object to add to
        :param name: attribute name
        :param description: attribute help description
        :param msg: help message to display
        """
        action = cls.for_message(msg)
        parser.add_argument(name, action=action, nargs=0, help=description)


def print_result(  # noqa: C901
    result: Any,
    jmespath_expr: Any = None,
    format_function: Callable[[Any], str] | None = None,
) -> None:
    """Print result vule"""
    format_function = format_function or helpers.json_dumps

    # early bail out if nothing was returned
    if result is None:
        return

    # Query using jmespath
    if jmespath_expr is not None:
        keep_dict_order = jmespath.Options(dict_cls=OrderedDict)
        result = jmespath_expr.search(result, keep_dict_order)

    # Format output
    formatted = format_function(result)

    try:
        print(formatted)
    except IOError as err:
        # Ignore BrokenPipe
        if err.errno != errno.EPIPE:
            raise err


@contextlib.contextmanager
def catch_missing_auth_cli() -> Generator[None, None, None]:
    """Catch HTTPError 401 and display a message on missing iotlab-auth."""

    auth_cli_err = (
        "HTTP Error 401: Unauthorized: Wrong login/password\n\n"
        "\tRegister your login:password using `iotlab-auth`\n"
    )
    try:
        yield
    except HTTPError as err:
        if err.code != 401:
            raise
        print(auth_cli_err, file=sys.stderr)
        sys.exit(1)


def main_cli(  # noqa: C901
    function: Callable[[argparse.Namespace], Any],
    parser: ArgumentParser,
    args: list[str] | None = None,
) -> None:
    """Main command-line execution."""
    args = args or sys.argv[1:]
    try:
        with catch_missing_auth_cli():
            parser_opts = parser.parse_args(args)
            result = function(parser_opts)
    except HTTPError as err:  # should be first as it's an IOError
        print(err, file=sys.stderr)

    except (IOError, ValueError) as err:
        parser.error(str(err))
    except RuntimeError as err:
        print(f"RuntimeError:\n{err!s}", file=sys.stderr)

    except KeyboardInterrupt:  # pragma: no cover
        print("\nStopped.", file=sys.stderr)
    else:
        print_result(result, parser_opts.jmespath, parser_opts.format)
        return
    sys.exit(1)


def sites_list() -> list[str]:
    """Return the list of sites"""
    sites_dict = rest.Api.get_sites()
    return [site["site"] for site in sites_dict["items"]]


def check_site_with_server(
    site_name: str, _sites_list: list[str] | None = None
) -> None:
    """Check if the given site exists by requesting the server list.
    If sites_list is given, it is used instead of doing a remote request

    >>> _sites_list = ['strasbourg', 'grenoble']
    >>> check_site_with_server('grenoble', _sites_list)
    >>> check_site_with_server('unknown', _sites_list)
    ... # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ArgumentTypeError: Unknown site name 'unknown'
    """
    sites = _sites_list or sites_list()
    if site_name in sites:
        return  # site_name is valid
    raise argparse.ArgumentTypeError(f"Unknown site name {site_name!r}")


def site_with_domain_checked(site: str, domain: str = DOMAIN_DNS) -> str:
    """Return site with domain and check site exists."""
    check_site_with_server(site)
    return f"{site}.{domain}"


def nodes_list_from_info(site: str, archi: str, nodes_str: str) -> list[str]:
    """ Cheks archi, nodes_str format and return nodes list

    >>> nodes_list_from_info('grenoble', 'm3', '1-4+6+7-8')
    ...  # doctest: +NORMALIZE_WHITESPACE
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
    """

    nodes_list = nodes_id_list(archi, nodes_str)
    fmt = f"%s.{site}.{DOMAIN_DNS}"
    nodes_url_list = [fmt % node for node in nodes_list]
    return nodes_url_list


def nodes_id_list(archi: str, nodes_list: str) -> list[str]:
    """Expand short nodes_list 'archi', '1-5+6+8-12'
    to a regular nodes list
    """

    nodes_num_list = expand_short_nodes_list(nodes_list)

    node_fmt = f"{archi}-%u"
    nodes = [node_fmt % num for num in nodes_num_list]

    return nodes


def _expand_minus_str(minus_nodes_str: str) -> list[int] | range:
    """Expand a '1-5' or '6' string to a list on integer
    :raises: ValueError on invalid values
    """
    minus_node = minus_nodes_str.split("-")
    res = None
    if len(minus_node) == 1:
        # ['6']
        res = [int(minus_node[0])]
    else:
        # ['1', '4'] or ['7', '8']
        first, last = minus_node
        nodes_range = range(int(first), int(last) + 1)
        # first >= last
        if len(nodes_range) <= 1:
            raise ValueError

        # Add nodes range
        res = nodes_range
    return res


def expand_short_nodes_list(nodes_str: str) -> list[int]:
    """Expand short nodes_list '1-5+6+8-12' to a regular nodes list

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
        nodes_ll = [
            _expand_minus_str(minus_nodes_str)
            for minus_nodes_str in nodes_str.split("+")
        ]
        # [[1, 2, 3], [6], [12]]
        return helpers.flatten_list_list(nodes_ll)
    except ValueError:
        # invalid: 6-3 or 6-7-8 or non int values
        raise ValueError(f"Invalid nodes list: {nodes_str} ([0-9+-])")


def add_nodes_selection_list(parser: ArgumentParser) -> None:
    """Add '-l' and '-e' experiment nodes selection"""
    list_group = parser.add_mutually_exclusive_group()

    list_group.add_argument(
        "-e",
        "--exclude",
        action="append",
        type=nodes_list_from_str,
        dest="exclude_nodes_list",
        help="exclude nodes list",
    )
    list_group.add_argument(
        "-l",
        "--list",
        action="append",
        type=nodes_list_from_str,
        dest="nodes_list",
        help="nodes list",
    )


def list_nodes(
    api: Any,
    exp_id: int,
    nodes_ll: list[list[str]] | None = None,
    excl_nodes_ll: list[list[str]] | None = None,
) -> list[str]:
    """Return the list of nodes where the command will apply"""

    if nodes_ll is not None:
        # flatten lists into one
        nodes = helpers.flatten_list_list(nodes_ll)

    elif excl_nodes_ll is not None:
        # flatten lists into one
        excl_nodes = set(helpers.flatten_list_list(excl_nodes_ll))

        # remove exclude nodes from experiment nodes
        exp_nodes = set(_get_experiment_nodes_list(api, exp_id))
        nodes = list(exp_nodes - excl_nodes)
    else:
        nodes = []  # all the nodes

    return sorted(nodes, key=helpers.node_url_sort_key)


def _get_experiment_nodes_list(api: Any, exp_id: int) -> list[str]:
    """Get the nodes_list for given experiment"""
    exp_nodes = api.get_experiment_info(exp_id, "nodes")
    nodes = [res["network_address"] for res in exp_nodes["items"]]
    return nodes


def nodes_list_from_str(nodes_list_str: str) -> list[str]:
    """Convert the nodes_list_str to a list of nodes hostname
    Checks that given site exist
    :param nodes_list_str: short nodes format: site_name,archi,node_id_list
                           example: 'grenoble,m3,1-34+72'
    :returns: ['m3-1.grenoble.iot-lab.info', ...]
    """
    try:
        # 'grenoble,m3,1-34+72' -> ['grenoble', 'm3', '1-34+72']
        site, archi, nodes_str = nodes_list_str.split(",")
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid number of argument in nodes list: {nodes_list_str!r}"
        )
    check_site_with_server(site)  # needs an external request
    return nodes_list_from_info(site, archi, nodes_str)
