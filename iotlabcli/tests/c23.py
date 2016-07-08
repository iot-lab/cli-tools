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

"""Tests Compatibility imports for python2 and python3."""


# pylint: disable=import-error,no-name-in-module
# pylint: disable=unused-import
# pylint: disable=ungrouped-imports
# pylint: disable=wrong-import-order
# flake8: noqa

from sys import version_info
if version_info[0] == 2:  # pragma: no cover
    # python2
    from urllib2 import HTTPError
    import mock
elif version_info[0:2] <= (3, 2):  # pragma: no cover
    # python3.2
    from urllib.error import HTTPError
    import mock
elif version_info[0] == 3:  # pragma: no cover
    # python3
    from urllib.error import HTTPError
    from unittest import mock
else:  # pragma: no cover
    raise ValueError('Unknown python version %r' % version_info)

# pylint:disable=wrong-import-position
from mock import patch, Mock, mock_open  # noqa
