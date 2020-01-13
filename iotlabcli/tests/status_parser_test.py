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

""" Test the iotlabcli.parser.status module """

import iotlabcli.parser.status as status_parser
from iotlabcli.tests.my_mock import MainMock

from .c23 import patch


@patch('iotlabcli.status.status_command')
class TestMainStatusParser(MainMock):
    """ Test iotlab-status main parser """
    def test_main(self, status_command):
        """ Run the parser.status.main function """
        status_command.return_value = {'result': 'test'}

        # sites
        args = ['--sites']
        status_parser.main(args)
        status_command.assert_called_with(self.api, 'sites')
        # nodes
        args = ['--nodes']
        status_parser.main(args)
        status_command.assert_called_with(self.api, 'nodes')
        # nodes
        args = ['--nodes-ids']
        status_parser.main(args)
        status_command.assert_called_with(self.api, 'nodes-ids')
        # experiments
        args = ['--experiments-running']
        status_parser.main(args)
        status_command.assert_called_with(self.api, 'experiments')

        # Use other selections
        status_parser.main(['--nodes', '--archi', 'm3',
                            '--state', 'Alive'])
        status_command.assert_called_with(self.api, 'nodes', archi='m3',
                                          state='Alive')

        status_parser.main(['--nodes-ids', '--site', 'lille', '--archi', 'm3'])
        status_command.assert_called_with(self.api, 'nodes-ids', site='lille',
                                          archi='m3')
