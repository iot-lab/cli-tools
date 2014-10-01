""" Integration tests for cli-tools """

from __future__ import print_function
import os
import sys
import json
import shlex
import time
import runpy
import unittest

try:
    # pylint:disable=F0401,E0611
    from mock import patch
    from cStringIO import StringIO
except ImportError:  # pragma: no cover
    from unittest.mock import patch  # pylint:disable=F0401,E0611
    from io import StringIO


class TestCliToolsExperiments(unittest.TestCase):
    """ Test the cli tools experiments """

    def _start_experiment(self, cmd, firmwares=()):
        """ Start an experiment using 'cmd'.
        Add firmwares path to allow checking later """
        print(cmd)
        self.firmwares = firmwares
        self.exp_desc = call_cli(cmd + ' --print')
        self.exp_id = call_cli(cmd, "id")
        self.id = ' --id {} '.format(self.exp_id)
        print(self.exp_id)

    def _get_exp_info(self):
        """ Get experiment info and check them """
        cmd = 'experiment-cli get --print' + self.id
        self.deploymentresults = call_cli(cmd, 'deploymentresults')
        # there should be successfull deployements
        self.assertNotEquals([], self.deploymentresults['0'])

        cmd = 'experiment-cli get --resources-id -i {}'.format(self.exp_id)
        call_cli(cmd)
        cmd = 'experiment-cli get --resources -i {}'.format(self.exp_id)
        call_cli(cmd)
        call_cli('experiment-cli get -a -i {}'.format(self.exp_id))

    def test_an_experiment_alias(self):
        """ Run an experiment """
        nodes = '5,site=devgrenoble+archi=m3:at86rf231'
        cmd = ('experiment-cli submit -d 5 -n test_cli ' +
               '-l {} '.format(nodes) + '-l {}'.format(nodes))

        self._start_experiment(cmd)
        self.assertEquals('Running', self._wait_state_or_finished('Running'))

        time.sleep(5)
        self._get_exp_info()
        time.sleep(5)

        cmd = 'experiment-cli stop -i {}'.format(self.exp_id)
        print(cmd)
        ret = call_cli(cmd)
        print(ret['status'])

        state = self._wait_state_or_finished()

    def _wait_state_or_finished(self, state=None):
        """ Wait experiment get in state, or states error and terminated """
        states_list = ['Error', 'Terminated']
        if state is not None:
            states_list.append(state)
        while True:
            cmd = 'experiment-cli get --exp-state -i {}'.format(self.exp_id)
            state = call_cli(cmd, "state")
            print(state)
            if state in states_list:
                return state
            time.sleep(5)

    # run whole tests only without experiments

    def setUp(self):
        self.cleanup()

    @classmethod
    def tearDownClass(cls):
        cls.cleanup()

    @classmethod
    def cleanup(cls):
        """ Cleanup currently running experiments """
        print("Cleanup", file=sys.stderr)
        cmd = 'experiment-cli get --list --state Running,Waiting'
        experiments = call_cli(cmd, "items")

        for exp in experiments:
            exp_id = exp["id"]
            call_cli('experiment-cli stop -i {}'.format(exp_id))


def call_cli(cmd, field=None):
    """ Call cli tool """
    argv = shlex.split(cmd)
    stdout = StringIO()
    with patch('sys.stdout', stdout):
        with patch('sys.argv', argv):
            runpy.run_path(argv[0])
    ret = json.loads(stdout.getvalue())
    if field:
        try:
            ret = ret[field]
        except KeyError as err:
            print(ret, file=sys.stderr)
            raise err

    stdout.close()
    return ret


if __name__ == '__main__':
    # TODO Setup with auth_cli
    # with patch('iotlabcli.auth.RC_FILE', 'test_auth_file'):
    unittest.main()
