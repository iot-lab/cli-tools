# -*- coding: utf-8 -*-

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

"""Main parser."""

import sys
from argparse import ArgumentParser

import iotlabcli.parser.auth
import iotlabcli.parser.admin
import iotlabcli.parser.experiment
import iotlabcli.parser.node
import iotlabcli.parser.profile
import iotlabcli.parser.robot


def main(args=None):
    """'iotlab' main function."""
    args = args or sys.argv[1:]

    commands = {
        'auth': iotlabcli.parser.auth.main,
        'admin': iotlabcli.parser.admin.main,
        'experiment': iotlabcli.parser.experiment.main,
        'node': iotlabcli.parser.node.main,
        'profile': iotlabcli.parser.profile.main,
        'robot': iotlabcli.parser.robot.main,
        'help': None
    }

    parser = ArgumentParser()
    parser.add_argument('command', nargs='?',
                        choices=commands.keys(), default='help')
    commands['help'] = lambda args: parser.print_help()

    opts, args = parser.parse_known_args(args)

    return commands[opts.command](args)
