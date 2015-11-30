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


def node_command(api, command, exp_id, nodes_list=(), cmd_opt=None):
    """ Launch commands (start, stop, reset, update)
    on resources (JSONArray) user experiment

    :param api: API Rest api object
    :param command: command that should be run
    :param exp_id: Target experiment id
    :param nodes_list: List of nodes where to run command.
                       Empty list runs on all nodes
    :param cmd_opt: Firmware path for update, profile name for profile
    """
    assert command in ('update', 'profile', 'start', 'stop', 'reset',
                       'debug-start', 'debug-stop')

    result = None
    if command == 'update':
        assert cmd_opt is not None, '`cmd_opt` required for update'
        files = helpers.FilesDict()

        files.add_firmware(cmd_opt)
        files[NODE_FILENAME] = json.dumps(nodes_list)
        result = api.node_update(exp_id, files)
    elif command == 'profile':
        cmd_opt = '&name={0}'.format(cmd_opt)
        result = api.node_command(command, exp_id, nodes_list, cmd_opt)
    else:
        result = api.node_command(command, exp_id, nodes_list)

    return result
