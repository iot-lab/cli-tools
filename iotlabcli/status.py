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

""" Implement the 'status' requests """


def status_command(api, command, **selections):
    """ Launch testbed status commands

    :param api: API Rest api object
    :param command: command that should be run
    :param **selections: other selections (site, archi, state)
    """
    assert command in ('sites', 'nodes', 'nodes-ids',
                       'experiments')
    if command == 'experiments':
        result = api.get_running_experiments()
    elif command == "sites":
        result = api.get_sites_details()
    elif command == "nodes":
        result = api.get_nodes(**selections)
    else:
        result = api.get_nodes(list_id=True, **selections)
    return result
