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


def robot_update_mobility(api, exp_id, name, nodes_list=()):
    """Update robot mobility on nodes_list.

    :param api: API Rest api object
    :param exp_id: Target experiment id
    :param name: mobility name
    :param nodes_list: List of nodes where to run command.
                       Empty list runs on all nodes
    """
    result = api.robot_update_mobility(exp_id, name, nodes_list)
    return result


def circuit_command(api, command, name=None, **selection):
    """Run mobilities circuit commands.

    :param command: in ['list', 'get']
    :param name: circuit name
    :param **selections: selections by circuit site and type

    """
    assert command in ('list', 'get')
    if 'type' in selection:
        assert selection['type'] in ('predefined', 'userdefined',)

    if command == 'list':
        result = api.get_circuits(**selection)
    elif command == 'get':
        result = api.get_circuit(name)
    else:  # pragma: no cover
        raise ValueError('Unknown command %r' % command)

    return result


def robot_get_map(site):
    """ Download all robot map files

    Download robot site config, map and docks list """
    map_cfg = {}

    map_cfg['config'] = Api.get_robot_mapfile(site, 'map/config')
    map_cfg['image'] = Api.get_robot_mapfile(site, 'map/image')
    map_cfg['dock'] = Api.get_robot_mapfile(site, 'dock/config')

    return map_cfg
