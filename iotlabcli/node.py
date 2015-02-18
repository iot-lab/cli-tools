# -*- coding:utf-8 -*-

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
    assert command in ('update', 'profile', 'start', 'stop', 'reset')

    result = None
    if 'update' == command:
        assert cmd_opt is not None, '`cmd_opt` required for update'
        files = helpers.FilesDict()

        files.add_firmware(cmd_opt)
        files[NODE_FILENAME] = json.dumps(nodes_list)
        result = api.node_update(exp_id, files)
    elif 'profile' == command:
        cmd_opt = '&name={0}'.format(cmd_opt)
        result = api.node_command(command, exp_id, nodes_list, cmd_opt)
    else:
        result = api.node_command(command, exp_id, nodes_list)

    return result
