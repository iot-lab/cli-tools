# -*- coding:utf-8 -*-

""" Implement the 'robot' requests """


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
