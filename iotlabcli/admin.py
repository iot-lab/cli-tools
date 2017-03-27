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

"""Implement the 'admin' requests."""

from iotlabcli import experiment
from iotlabcli import rest


def wait_user_experiment(exp_id, user, states='Running',
                         step=5, timeout=float('+inf')):
    """Wait for the user experiment to be in `states`.

    Also returns if Terminated or Error

    :param exp_id: scheduler OAR id submission
    :param user: owner of the experiment
    :param states: Comma separated string of states to wait for
    :param step: time to wait between each server check
    :param timeout: timeout if wait takes too long
    """
    def _state_fct():
        """Get user experiment state."""
        return rest.Api.get_any_experiment_state(exp_id, user)['state']
    exp_str = '%s/%s' % (exp_id, user)

    # Wait experiment state
    return experiment.wait_state(_state_fct, exp_str, states, step, timeout)
