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

""" Integration tests for cli-tools """

# pylint:disable=I0011,too-many-public-methods
# pylint:disable=I0011,attribute-defined-outside-init
# pylint:disable=I0011,invalid-name


# Test that may be added:
#  * physical experiments
#  * load experiment
#  * Validates JSON outputs
#  * run commands without exp_id in error cases no exp or many exps running


import argparse
import os
import json
import shlex
import time
import runpy
import unittest
import logging
from tempfile import NamedTemporaryFile

from iotlabcli.parser.common import expand_short_nodes_list

try:
    # pylint:disable=I0011,F0401,E0611
    from mock import patch
    from cStringIO import StringIO
except ImportError:  # pragma: no cover
    from unittest.mock import patch  # pylint:disable=I0011,F0401,E0611
    from io import StringIO


LOGGER = logging.getLogger(__file__)
LOGGER.setLevel(logging.INFO)

_FMT = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
_HANDLER = logging.StreamHandler()
_HANDLER.setFormatter(_FMT)
LOGGER.addHandler(_HANDLER)


SITES = {
    'prod': {
        'm3': 'grenoble',
        'cc1101': 'strasbourg',
    },
    'dev': {
        'm3': 'devgrenoble',
    }
}

NODES = SITES['prod']

CUR_DIR = os.path.dirname(__file__)

FIRMWARE = {
    'm3': os.path.join(CUR_DIR, 'firmwares', 'm3_autotest.elf'),
    'cc1101': os.path.join(CUR_DIR, 'firmwares', 'cc1101.hex'),
}


class TestCliToolsExperiments(unittest.TestCase):
    """ Test the cli tools experiments """

    def test_an_experiment_alias_multi_same_node_firmware(self):
        """ Exp alias multiple time same reservation firmware """
        nodes = f"5,site={NODES['m3']}+archi=m3:at86rf231,{FIRMWARE['m3']}"
        cmd = ('iotlab-experiment submit -d 5 -n test_cli'
               ' -l {0} -l {0} -l {0}'.format(nodes))

        self._start_experiment(cmd)
        self.assertEqual('Running', self._wait_state_or_finished('Running'))
        time.sleep(1)
        self._get_exp_info()
        self._stop_experiment()
        self._wait_state_or_finished()

        # Test get start-time
        cmd = f'iotlab-experiment get --start-time -i {self.exp_id}'
        self.assertNotEqual(0, call_cli(cmd)['start_time'])

    def test_an_experiment_alias_multi_same_node(self):
        """ Run an experiment with alias and multiple time same reservation """
        nodes = f"5,site={NODES['m3']}+archi=m3:at86rf231"
        cmd = 'iotlab-experiment submit -d 5 -n test_cli -l {0} -l {0}'.format(
            nodes)

        self._start_experiment(cmd)
        self.assertEqual('Running', self._wait_state_or_finished('Running'))
        time.sleep(1)
        self._get_exp_info()
        self._reset_nodes_no_expid()
        f_nodes = self.nodes_str_from_desc(archi='m3', n_type='-l')
        self._flash_nodes(FIRMWARE['m3'], f_nodes)
        self._stop_experiment()
        self._wait_state_or_finished()

    def test_an_experiment_alias_multisite(self):
        """ Run an experiment with multisite/archi """
        # ensure profile test_m3 exists
        call_cli('iotlab-profile addm3 -n test_m3 -sniffer -channels 11')

        cmd = 'iotlab-experiment submit -d 5 -n test_cli'
        cmd += (
            f" -l 5,"
            f"site={NODES['m3']}+archi=m3:at86rf231,{FIRMWARE['m3']},test_m3"
        )
        cmd += (
            f" -l 1,"
            f"site={NODES['cc1101']}+archi=wsn430:cc1101,{FIRMWARE['cc1101']}"
        )

        self._start_experiment(cmd)
        self.assertEqual('Running', self._wait_state_or_finished('Running'))
        time.sleep(1)
        self._get_exp_info()
        self._reset_nodes_no_expid()

        # flash all but wsn430 nodes
        nodes = self.nodes_str_from_desc(archi='wsn430', n_type='-e')
        self._flash_nodes(FIRMWARE['m3'], nodes)

        self._stop_experiment()
        self._wait_state_or_finished()

    @staticmethod
    def _find_working_nodes(site, archi, num):
        """ Find working nodes, there should be at least num nodes """
        cmd = f'iotlab-experiment info -li --site {site}'
        nodes = expand_short_nodes_list(next(
            s['ids']
            for n in call_cli(cmd)["items"][0]['archis'] if n['archi'] == archi
            for s in n['states'] if s['state'] == 'Alive'
        ))
        nodes_str = '+'.join(str(n) for n in nodes[0:num])
        LOGGER.debug("nodes_str: %r", nodes_str)
        return f"{site},{archi.split(':')[0]},{nodes_str}"

    def test_an_experiment_physical_one_site(self):
        """ Run an experiment on m3 nodes simple"""
        site = NODES['m3']

        cmd = f'iotlab-experiment info -li --site {site}'

        nodes = self._find_working_nodes(site, 'm3:at86rf231', 3)
        cmd = f'iotlab-experiment submit -d 5 -n test_cli -l {nodes} '
        self._start_experiment(cmd)
        self.assertEqual('Running', self._wait_state_or_finished('Running'))
        time.sleep(1)
        self._get_exp_info()
        self._reset_nodes_no_expid()
        f_nodes = self.nodes_str_from_desc(archi='m3', n_type='-l')
        self._flash_nodes(FIRMWARE['m3'], f_nodes)
        self._debug('start', f_nodes)
        self._debug('stop', f_nodes)
        self._stop_experiment()
        self._wait_state_or_finished()

    # helpers methods
    @staticmethod
    def _reset_nodes_no_expid():
        """ Flash all nodes of type archi """
        cmd = 'iotlab-node --reset'
        LOGGER.info(cmd)
        call_cli(cmd)

    def nodes_str_from_desc(self, site='', archi='', n_type='-l'):
        """ extract nodes that match description """
        _nodes = self.exp_desc["nodes"]['items']
        nodes = [n for n in _nodes
                 if (archi in n['archi']) and (site in n['site'])]

        nodes_dict = {}
        for n in nodes:
            archi, num = n['network_address'].split('.')[0].split('-')[0:2]
            nodes_dict.setdefault((n['site'], archi), []).append(num)

        LOGGER.debug(nodes_dict)

        nodes_list = []
        for (_site, _archi), nums in nodes_dict.items():
            node_str = f"{_site},{_archi},{'+'.join(nums)}"
            LOGGER.debug("nodes: %s", node_str)
            nodes_list.append(node_str)

        # create the joined string
        node_str = ''.join(f' {n_type} {n}' for n in nodes_list)
        return node_str

    def _flash_nodes(self, firmware, cmd_append=''):
        """ Flash all nodes of type archi """
        cmd = f'iotlab-node -i {self.exp_id} -up {firmware} {cmd_append}'
        LOGGER.info(cmd)
        ret = call_cli(cmd)
        LOGGER.debug(ret)

    def _debug(self, mode, cmd_append=''):
        """ Flash all nodes of type archi """
        cmd = f'iotlab-node -i {self.exp_id} --debug-{mode} {cmd_append}'
        LOGGER.info(cmd)
        ret = call_cli(cmd)
        LOGGER.debug(ret)

    def _start_experiment(self, cmd, firmwares=()):
        """ Start an experiment using 'cmd'.
        Add firmwares path to allow checking later """
        LOGGER.info(cmd)
        self.firmwares = firmwares
        call_cli(cmd + ' --print')
        self.exp_id = call_cli(cmd)["id"]
        self.id_str = f' --id {self.exp_id} '
        LOGGER.info(self.exp_id)

    def _stop_experiment(self):
        """ Stop current experiment """
        cmd = f'iotlab-experiment stop -i {self.exp_id}'
        ret = call_cli(cmd)
        LOGGER.info("%s: %r", cmd, ret['status'])

    def _get_exp_info(self):
        """ Get experiment info and check them """
        cmd = 'iotlab-experiment get -d' + self.id_str
        self.exp_desc = {}
        self.exp_desc['deploymentresults'] = exp_deployment = call_cli(cmd)
        try:
            self.assertNotEqual([], exp_deployment['0'])
        except KeyError:
            LOGGER.warning("No 0 Deploymentresults: %r", exp_deployment)

        cmd = 'iotlab-experiment get -n' + self.id_str
        self.exp_desc['nodes'] = call_cli(cmd)

        self.assertIsInstance(self.exp_desc['nodes'], dict)
        self.assertIsInstance(self.exp_desc['nodes']['items'][0], dict)

        cmd = f'iotlab-experiment get --nodes-id -i {self.exp_id}'
        call_cli(cmd)
        cmd = f'iotlab-experiment get --nodes -i {self.exp_id}'
        call_cli(cmd)
        call_cli(f'iotlab-experiment get -a -i {self.exp_id}')

    def _wait_state_or_finished(self, states='Stopped,Error,Terminated'):
        """ Wait experiment get in state, or states error and terminated """
        cmd = (
            f"iotlab-experiment wait --state {states} "
            f"--step 5 -i {self.exp_id}"
        )
        LOGGER.info(cmd)
        return call_cli(cmd)

    # run whole tests only without experiments
    def setUp(self):
        self.cleanup()

    def tearDown(self):
        try:
            os.remove(f"{self.exp_id}.tar.gz")
        except (OSError, AttributeError):
            pass

    @classmethod
    def tearDownClass(cls):
        cls.cleanup()

    @classmethod
    def cleanup(cls):
        """ Cleanup currently running experiments """
        LOGGER.debug("cleanup")
        cmd = 'iotlab-experiment get --list --state Running,Waiting'
        experiments = call_cli(cmd)["items"]

        for exp in experiments:
            exp_id = exp["id"]
            call_cli(f'iotlab-experiment stop -i {exp_id}')

        remote_profs = call_cli('iotlab-profile get --list')
        profiles_names = [p['profilename'] for p in remote_profs]
        if 'test_m3' in profiles_names:
            call_cli('iotlab-profile del -n test_m3')


class TestCliToolsProfile(unittest.TestCase):
    """ Test the cli tools profile """
    profile = {
        'm3': 'test_cli_profile_m3',
        'm3_full': 'test_cli_profile_m3_full',
        'm3_sniffer': 'test_cli_profile_m3_sniffer',
        'wsn430': 'test_cli_profile_wsn430',
        'wsn430_full': 'test_cli_profile_wsn430_full',
    }

    @classmethod
    def setUpClass(cls):
        """ Remove the tests profiles if they are here """
        remote_profs = call_cli('iotlab-profile get --list')
        profiles_names = [p['profilename'] for p in remote_profs]
        for prof in cls.profile.values():
            if prof in profiles_names:
                call_cli(f'iotlab-profile del --name {prof}')

    def _del_prof(self, name):
        """ Add a profile and get it to check it's the same """
        cmd_result = call_cli(f'iotlab-profile del --name {name}')
        self.assertIsNone(cmd_result)

    def _add_profile_simple(self, cmd, name):
        """ Add a profile and get it to check it's the same """
        profile_dict = call_cli(cmd + ' --json')
        profile_dict = {k: v for k, v in profile_dict.items() if v is not None}

        # add profile return name
        self.assertEqual(profile_dict, call_cli(cmd))

        get_profile_dict = call_cli(f'iotlab-profile get --name {name}')
        # compare that initial dict is a subset of result dict
        #     can't '<=' dict in python3, so update result dict with initial
        #     values and see if it stays equals
        cmp_prof_dict = get_profile_dict.copy()
        cmp_prof_dict.update(profile_dict)
        self.assertEqual(cmp_prof_dict, get_profile_dict)

    def _get_and_load(self, name):
        """ Get a profile and try loading it
        We then check that getting both profiles return the same output
        """

        get_profile_dict = call_cli(f'iotlab-profile get --name {name}')

        call_cli(f'iotlab-profile del --name {name}')

        with NamedTemporaryFile(mode='w+') as prof:
            prof.write(json.dumps(get_profile_dict))
            prof.flush()
            load_ret = call_cli(f'iotlab-profile load --file {prof.name}')
        # returned name are the same
        self.assertEqual(get_profile_dict, load_ret)
        get_loaded_profile = call_cli(f'iotlab-profile get --name {name}')
        # returned profile are the same
        self.assertEqual(get_profile_dict, get_loaded_profile)

    def _add_prof(self, cmd, name):
        """ Test adding and loading a user profile """
        self._add_profile_simple(cmd.format(name), name)
        self._get_and_load(name)  # erase same profile

    def test_m3_profile(self):
        """ Test creating M3 profiles and deleting them """

        profs = call_cli('iotlab-profile get -l')
        profiles_names = {p['profilename'] for p in profs}

        self._add_prof(
            'iotlab-profile addm3 -n {} -sniffer -channels 11',
            self.profile['m3']
        )
        profiles_names.add(self.profile['m3'])

        prof_cmd = 'iotlab-profile addm3 -n {} -p dc'
        prof_cmd += ' -power -voltage -current -period 8244 -avg 1024'
        prof_cmd += ' -rssi -channels 11 16 21 26 -num 255 -rperiod 65535'
        self._add_prof(prof_cmd, self.profile['m3_full'])
        profiles_names.add(self.profile['m3_full'])

        prof_cmd = 'iotlab-profile addm3 -n {}'
        prof_cmd += ' -sniffer -channels 11'
        self._add_prof(prof_cmd, self.profile['m3_sniffer'])
        profiles_names.add(self.profile['m3_sniffer'])

        # check that profiles have been added
        profs = call_cli('iotlab-profile get -l')
        profiles_names_new = {p['profilename'] for p in profs}
        self.assertEqual(profiles_names, profiles_names_new)

        self._del_prof(self.profile['m3'])
        self._del_prof(self.profile['m3_full'])
        self._del_prof(self.profile['m3_sniffer'])


class TestAnErrorCase(unittest.TestCase):
    """ Test cli tools error cases """

    def test_node_parser_errors(self):
        """ Test some node parser errors """
        # invalid argument number
        self.assertRaises(
            SystemExit, call_cli,
            'iotlab-node --reset -l {m3},m3'.format(**NODES),
            print_err=False)

        # invalid site
        self.assertRaises(
            SystemExit, call_cli, 'iotlab-node --reset -l invalid_site,m3,1',
            print_err=False)

        # invalid archi
        self.assertRaises(
            SystemExit, call_cli,
            'iotlab-node --reset -l {m3},m4,1'.format(**NODES),
            print_err=False)

        # invalid state
        self.assertRaises(
            SystemExit, call_cli,
            ('iotlab-experiment --user test --password test get ' +
             ' -l --state=Terminateded'),
            print_err=False)

    def test_experiment_parser_errors(self):
        """ Test some experiment parser errors """
        self.assertRaises(
            SystemExit, call_cli,
            'iotlab-experiment submit -d 20 -l {m3},m3,70-1'.format(**NODES),
            print_err=False)

        # alias invalid archi
        self.assertRaises(
            SystemExit, call_cli,
            ('iotlab-experiment submit -d 20' +
             ' -l 3,site={m3}+archi=inval+mobile=1'.format(**NODES)),
            print_err=False)

        # too many values
        self.assertRaises(
            SystemExit, call_cli,
            ('iotlab-experiment submit -d 20' +
             '-l {m3},m3,1,fw,prof,extra'.format(**NODES)),
            print_err=False)

        # alias and physical
        self.assertRaises(
            SystemExit, call_cli,
            ('iotlab-experiment submit -d 20' +
             ' -l {m3},m3,1' +
             ' -l 3,site={m3}+archi=m3:at86rf231+mobile=true').format(**NODES),
            print_err=False)

        # alias invalid values
        self.assertRaises(
            SystemExit, call_cli,
            ('iotlab-experiment submit -d 20' +
             ' -l 3,site={m3}+archi=m3:at86rf231+inval_prop=2'.format(**NODES)
             ),
            print_err=False)

        # No site or archi
        self.assertRaises(
            SystemExit, call_cli,
            ('iotlab-experiment submit -d 20 -l 3,archi=m3:at86rf231'),
            print_err=False)

        # invalid properties
        self.assertRaises(
            SystemExit, call_cli,
            ('iotlab-experiment submit -d 20 -l 3,archi='),
            print_err=False)
        self.assertRaises(
            SystemExit, call_cli,
            ('iotlab-experiment submit -d 20 -l 3,archi=val_1+archi=val_2'),
            print_err=False)

        # invalid mobile
        self.assertRaises(
            SystemExit, call_cli,
            ('iotlab-experiment submit -d 20' +
             ' -l 3,archi=m3:at86rf231+site={m3}+mobile=turtlebot').format(
                 **NODES),
            print_err=False)

    def test_rest_errors(self):
        """ Test some rest error """
        self.assertRaises(SystemExit, call_cli,
                          'iotlab-experiment get -p -i 0',
                          print_err=False)


def treat_cli_return(stdout, stderr):
    try:
        stdout_value = stdout.getvalue()
        ret = json.loads(stdout_value)
    except json.JSONDecodeError:
        ret = None

    stdout.close()
    stderr.close()
    return ret


def call_cli(cmd, print_err=True):
    """ Call cli tool """
    argv = shlex.split(cmd)
    stdout = StringIO()
    stderr = StringIO()
    LOGGER.info(cmd)
    try:
        with patch('sys.stderr', stderr):
            with patch('sys.stdout', stdout):
                with patch('sys.argv', argv):
                    runpy.run_path(argv[0])
    except SystemExit as err:
        if print_err:
            LOGGER.error('%r', stderr.getvalue())
        raise err

    return treat_cli_return(stdout, stderr)


def try_config_iotlab_test_account():
    """ Try to configure tests to use 'iotlab' account """
    try:
        password = os.environ['IOTLAB_TEST_PASSWORD']
        # use a fake auth_file
        os.environ['IOTLAB_PASSWORD_FILE'] = 'test_auth_file'
        call_cli(f"iotlab-auth --user iotlab --password {password}")
    except KeyError:
        pass


def opts_parser():
    """ Argument parser """
    parser = argparse.ArgumentParser('Integration tests')
    parser.add_argument('--dev', action='store_true', default=False,
                        help='Run againt dev platform, default to prod')
    parser.add_argument('--stop', action='store_true', default=False,
                        help='Stop tests after first error')
    parser.add_argument('--verbose', action='store_const', default=1,
                        const=4, help='Verbose output')
    return parser


if __name__ == '__main__':
    failfast = False
    opts = opts_parser().parse_args()
    if opts.dev:
        os.environ['IOTLAB_API_URL'] = 'https://devwww.iot-lab.info/rest/'
        NODES = SITES['dev']

    try_config_iotlab_test_account()
    unittest.main(argv=[__file__], verbosity=opts.verbose, failfast=opts.stop)
