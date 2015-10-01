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

""" Implement the 'robot' requests """

from iotlabcli.rest import Api


def robot_command(api, command, exp_id, nodes_list=()):
    """ Launch commands ('status',) on nodes_list

    :param api: API Rest api object
    :param command: command that should be run
    :param exp_id: Target experiment id
    :param nodes_list: List of nodes where to run command.
                       Empty list runs on all nodes
    """
    assert command in ('status',)
    result = api.robot_command(command, exp_id, nodes_list)
    return result


def robot_update_mobility(api, exp_id, name, site, nodes_list=()):
    """Update robot mobility 'name [site]' on nodes_list.

    :param api: API Rest api object
    :param exp_id: Target experiment id
    :param name: mobility name
    :param site: mobility site
    :param nodes_list: List of nodes where to run command.
                       Empty list runs on all nodes
    """
    result = api.robot_update_mobility(exp_id, name, site, nodes_list)
    return result


def mobility_command(api, command, arg=None):
    """Run mobility command.

    Command argument:

    * 'list' no arguments
    * 'get': Mobility (name, site) tuple.

    :param command: in ['list', 'get']
    :param arg: argument specific to command

    """
    assert command in ('list', 'get')

    if command == 'list':
        result = api.mobility_user_list()
    elif command == 'get':
        name, site = arg  # pylint:disable=unpacking-non-sequence
        result = api.mobility_user_get(name, site)
    else:  # pragma: no cover
        raise ValueError('Unknown command %r' % command)

    return result


def robot_get_map(site):
    """ Download all robot map files

    Download robot site config, map and docks list """
    map_cfg = {}

    map_cfg['config'] = Api.get_robot_mapfile(site, 'mapconfig')
    map_cfg['image'] = Api.get_robot_mapfile(site, 'mapimage')
    map_cfg['dock'] = Api.get_robot_mapfile(site, 'dockconfig')

    return map_cfg
