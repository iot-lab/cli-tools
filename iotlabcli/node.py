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

""" Implement the 'node' requests """

import json
from iotlabcli import helpers

NODE_FILENAME = 'nodes.json'
EXPERIMENT = 'experiment.json'


def _node_command_flash(api, exp_id, nodes_list, cmd_opt):
    assert cmd_opt is not None, '`cmd_opt` required for update'
    files = helpers.FilesDict()

    files.add_file(cmd_opt)
    if cmd_opt.endswith('.bin'):
        files[EXPERIMENT] = json.dumps({'nodes': nodes_list, 'offset': 0})
        return api.node_update(exp_id, files, binary=True)

    files[NODE_FILENAME] = json.dumps(nodes_list)
    return api.node_update(exp_id, files)


def _node_command_profile_load(api, exp_id, nodes_list, cmd_opt):
    assert cmd_opt is not None, '`cmd_opt` required for update'
    files = helpers.FilesDict()

    files.add_file(cmd_opt)
    files[NODE_FILENAME] = json.dumps(nodes_list)
    return api.node_profile_load(exp_id, files)


def node_command(api, command, exp_id, nodes_list=(), cmd_opt=None):
    """ Launch commands (start, stop, reset, update)
    on nodes (JSONArray) user experiment

    :param api: API Rest api object
    :param command: command that should be run
    :param exp_id: Target experiment id
    :param nodes_list: List of nodes where to run command.
                       Empty list runs on all nodes
    :param cmd_opt: Firmware path for update, profile name for profile
    """
    assert command in ('flash', 'flash-idle',
                       'profile', 'profile-load', 'profile-reset',
                       'start', 'stop', 'reset',
                       'debug-start', 'debug-stop')

    result = None
    if command == 'flash':
        result = _node_command_flash(api, exp_id, nodes_list, cmd_opt)
    elif command == 'profile-load':
        result = _node_command_profile_load(api, exp_id, nodes_list, cmd_opt)
    elif command == 'profile':
        cmd_opt = '&name={}'.format(cmd_opt)
        result = api.node_command(command, exp_id, nodes_list, cmd_opt)
    else:
        result = api.node_command(command, exp_id, nodes_list)

    return result
