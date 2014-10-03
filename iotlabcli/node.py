# -*- coding:utf-8 -*-

""" Implement the 'node' requests """
import json
from iotlabcli import helpers

NODE_FILENAME = 'nodes.json'


def node_command(api, command, exp_id, nodes_list=(), firmware_path=None):
    """ Launch commands (start, stop, reset, update)
    on resources (JSONArray) user experiment

    :param api: API Rest api object
    :param command: command that should be run
    :param exp_id: Target experiment id
    :param nodes_list: List of nodes where to run command.
                       Empty list runs on all nodes
    :param firmware_path: Firmware path for update command
    """
    assert command in ('update', 'start', 'stop', 'reset')

    result = None
    if 'update' == command:
        assert firmware_path is not None, '`firmware_path` required for update'
        files = helpers.FilesDict()

        files.add_firmware(firmware_path)
        files[NODE_FILENAME] = json.dumps(nodes_list)
        result = api.node_update(exp_id, files)
    else:
        result = api.node_command(command, exp_id, nodes_list)

    return result
