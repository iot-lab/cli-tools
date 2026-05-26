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

"""Implement the 'experiment' requests"""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from os.path import basename
from typing import Any

try:
    # pylint: disable=import-error,no-name-in-module
    import backport_collections as collections
except ImportError:  # pragma: no cover
    # pylint: disable=import-error,no-name-in-module
    import collections

from iotlabcli import helpers
from iotlabcli.associations import AssociationsMap, associationsmapdict_from_dict

# static name for experiment file : rename by server-rest
EXP_FILENAME = "new_exp.json"
RUN_FILENAME = "script.json"

NODES_ASSOCIATIONS_FILE_ASSOCS = ("firmware",)
SITE_ASSOCIATIONS_FILE_ASSOCS = ("script", "scriptconfig")

# Default wait timeout when waiting for an experiment to be in Running state
WAIT_TIMEOUT_DEFAULT = float("+inf")


def submit_experiment(  # pylint:disable=too-many-arguments,too-many-positional-arguments
    api: Any,
    name: str | None,
    duration: int,
    resources: list[dict[str, Any]],
    start_time: int | None = None,
    print_json: bool = False,
    sites_assocs: Sequence[SiteAssociationTuple] | None = None,
) -> Any:
    """Submit user experiment with JSON Encoder serialization object
    Experiment and firmware(s). If submission is accepted by scheduler OAR
    we print JSONObject response with id submission.

    :param api: API Rest api object
    :param name: experiment name
    :param duration: experiment duration in minutes
    :param resources: list of 'exp_resources'
    :param print_json: select if experiment should be printed as json instead
        of submitted
    :param sites_assocs: list of 'site_association'
    """

    assert resources, f"Empty resources: {resources!r}"
    experiment = _Experiment(name, duration, start_time)

    exp_files = helpers.FilesDict()
    for res_dict in resources:
        inserted_resources = exp_files.add_files_from_dict(
            NODES_ASSOCIATIONS_FILE_ASSOCS, res_dict
        )
        res_dict.update(inserted_resources)
        experiment.add_exp_resources(res_dict)

    sites_assocs = sites_assocs or ()
    for site_assoc in sites_assocs:
        assocs = site_assoc.associations
        inserted_assocs = exp_files.add_files_from_dict(
            SITE_ASSOCIATIONS_FILE_ASSOCS, assocs
        )
        assocs.update(inserted_assocs)
        experiment.add_site_association(site_assoc)

    if print_json:  # output experiment description
        return experiment

    # submit experiment
    exp_files[EXP_FILENAME] = helpers.json_dumps(experiment)  # exp description

    return api.submit_experiment(exp_files)


def stop_experiment(api: Any, exp_id: int) -> Any:
    """Stop user experiment submission.

    :param api: API Rest api object
    :param exp_id: scheduler OAR id submission
    """
    return api.stop_experiment(exp_id)


def get_experiments_list(api: Any, state: str | None, limit: int, offset: int) -> Any:
    """Get the experiment list with the specific restriction:
    :param state: State of the experiment
    :param limit: maximum number of outputs
    :param offset: offset of experiments to start at
    """
    state = helpers.check_experiment_state(state)
    return api.get_experiments(state, limit, offset)


def get_experiment(api: Any, exp_id: int, option: str = "") -> Any:
    """Get user experiment's description :

    :param api: API Rest api object
    :param exp_id: experiment id
    :param option: Restrict to some values
            * '':            experiment submission
            * 'nodes':       nodes list
            * 'nodes_ids':   nodes id list: (1-34+72 format)
            * 'state':       experiment state
            * 'data':        experiment tar.gz with description and firmwares
            * 'start':       expected start time
            * 'deployment':  deployment info
    """
    result = api.get_experiment_info(exp_id, option)
    if option == "data":
        _write_experiment_archive(exp_id, result)
        result = "Written"

    return result


def get_active_experiments(api: Any, running_only: bool = True) -> dict[str, list[int]]:
    """Get active experiments with it's state.

    :param api: API Rest api object
    :param running_only: if False search for a waiting/starting experiment
    :returns: {'Running': [EXP_ID], 'Waiting': [EXP_ID, EXP_ID]}
    """
    states = ["Running"] if running_only else helpers.ACTIVE_STATES
    exp_by_states = helpers.exps_by_states_dict(api, states)
    return exp_by_states


def load_experiment(
    api: Any, exp_desc_path: str, files_list: Sequence[str] = ()
) -> Any:
    """Load and submit user experiment description with firmware(s)

    Firmwares and scripts required for experiment will be loaded from
    current directory, except if their path is given in files_list

    :param api: API Rest api object
    :param exp_desc_path: path to experiment json description file
    :param files_list: list of files path
    """

    # 1. load experiment description
    exp_dict = json.loads(helpers.read_file(exp_desc_path))
    experiment = _Experiment.from_dict(exp_dict)

    # 2. List files and update path with provided path
    files = _files_with_filespath(experiment.filenames(), files_list)

    # Construct experiment files
    exp_files = helpers.FilesDict()
    exp_files[EXP_FILENAME] = helpers.json_dumps(experiment)
    for exp_file in files:
        exp_files.add_file(exp_file)
    return api.submit_experiment(exp_files)


def _files_with_filespath(files: list[str], filespath: Sequence[str]) -> list[str]:
    """Return `files` updated with `filespath`.

    Return a `files` list with path taken from `filespath` if basename
    matches one in `files`.

    >>> _files_with_filespath(['a', 'b', 'c', 'a'], ['dir/c', 'dir/a'])
    ['b', 'dir/a', 'dir/c']

    >>> _files_with_filespath(['a', 'b', 'c', 'a'], [])
    ['a', 'b', 'c']

    >>> _files_with_filespath(['a', 'b'], ['dir/a', 'dir/c'])
    Traceback (most recent call last):
    ...
    ValueError: Filespath ['dir/c'] not in files list ['a', 'b']
    """
    # Change filespath to a dict by basename
    filespathdict = {basename(f): f for f in filespath}

    # Update to full filepath if provided
    updatedfiles = [filespathdict.pop(f, f) for f in set(files)]

    # Error if there are remaining files in filespath
    if filespathdict:
        raise ValueError(
            f"Filespath {list(filespathdict.values())} not in "
            f"files list {sorted(set(files))}"
        )

    return sorted(updatedfiles)


def reload_experiment(
    api: Any, exp_id: int, duration: int | None = None, start_time: int | None = None
) -> Any:
    """Reload given experiment, duration and start_time can be adapted.

    :param api: API Rest api object
    :param exp_id: experiment id
    :param duration: experiment duration in minutes. None for same duration.
    :param start_time: experiment start time timestamp.
        None for as soon as possible
    """
    exp_json = {}

    # API needs strings and values shoud be absent if None
    if duration is not None:
        exp_json["duration"] = str(duration)
    if start_time is not None:
        exp_json["reservation"] = str(start_time)

    return api.reload_experiment(exp_id, exp_json)


def info_experiment(
    api: Any, list_id: bool = False, site: str | None = None, **selections: str
) -> Any:
    """Print testbed information for user experiment submission:
    * nodes description
    * nodes description in short mode

    :param api: API Rest api object
    :param list_id: By default, return full nodes list, if list_id
        return output in exp_list format '3-12+42'
    :param site: Restrict informations collection on site
    :param **selections: other selections than site
    """
    return api.get_nodes(list_id, site, **selections)


def script_experiment(api: Any, exp_id: int, command: str, *options: Any) -> Any:
    """Upload an run scripts on sites.

    :param api: API Rest api object
    :param command: in ('run', 'kill', 'status')
    :param *options: list of 'site_association' with script 'run'
                     list of sites for 'kill', 'status' may be None
    """
    res = None
    if command == "run":
        files_dict = _script_run_files_dict(*options)
        res = api.script_command(exp_id, command, files=files_dict)

    elif command in ("kill", "status"):
        sites_list = sorted(options)
        res = api.script_command(exp_id, command, json=sites_list)

    if res is None:
        raise ValueError(f"Unknown script command {command!r}")

    return res


def _script_run_files_dict(*site_associations: SiteAssociationTuple) -> Any:
    """Return script start files dict.

    Returns dict with format
    {
        <RUN_FILENAME>: json({'script': [<scripts_associations>], ...}),
        'scriptname': b'scriptcontent',
    }
    """

    if not site_associations:
        raise ValueError(f"Got empty site_associations: {site_associations}")

    _check_sites_uniq(*site_associations)

    files_dict = helpers.FilesDict()

    # Save association and files
    associations = {}
    for site_assoc in site_associations:
        sites, assocs = site_assoc.sites, site_assoc.associations
        for assoctype, assocname in assocs.items():
            _add_siteassoc_to_dict(associations, sites, assoctype, assocname)
        inserted_assocs = files_dict.add_files_from_dict(
            SITE_ASSOCIATIONS_FILE_ASSOCS, assocs
        )
        assocs.update(inserted_assocs)

    # Add scrit sites association to files_dict
    files_dict[RUN_FILENAME] = helpers.json_dumps(associations)
    return files_dict


def _add_siteassoc_to_dict(
    assocs: dict[str, Any], sites: tuple[str, ...], assoctype: str, assocname: str
) -> None:
    """Add given site association to 'assocs' dict."""
    name = site_association_name(assoctype, assocname)
    assoc = assocs.setdefault(assoctype, AssociationsMap(assoctype, "sites"))
    assoc.extendvalues(name, sites)


def _check_sites_uniq(*site_associations: SiteAssociationTuple) -> None:
    """Check that sites are uniq

    >>> _check_sites_uniq(site_association('grenoble', script='script'),
    ...                   site_association('lille', script='script'))
    >>> _check_sites_uniq(site_association('grenoble', script='script'),
    ...                   site_association('grenoble', script='script2'))
    Traceback (most recent call last):
    ...
    ValueError: Sites may only be given once: ['grenoble']
    """
    sites = [assocs.sites for assocs in site_associations]
    sites = helpers.flatten_list_list(sites)
    duplicates = [s for s, c in collections.Counter(sites).items() if c > 1]

    if duplicates:
        raise ValueError(f"Sites may only be given once: {duplicates}")


def wait_experiment(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    api: Any,
    exp_id: int,
    states: str = "Running",
    step: int = 5,
    timeout: float = WAIT_TIMEOUT_DEFAULT,
    cancel_on_timeout: bool = False,
) -> str | None:
    """Wait for the experiment to be in `states`.

    Also returns if Terminated or Error

    :param api: API Rest api object
    :param exp_id: scheduler OAR id submission
    :param states: Comma separated string of states to wait for
    :param step: time to wait between each server check
    :param timeout: timeout if wait takes too long
    :param cancel_on_timeout: cancel the experiment if the timeout is reached
    """

    def _state_function():
        """Get current user experiment state."""
        return get_experiment(api, exp_id, "")["state"]

    def _stop_function():
        """Cancel submitted user experiment."""
        stop_experiment(api, exp_id)

    exp_str = f"{exp_id}"

    return wait_state(
        _state_function,
        _stop_function,
        exp_str,
        states,
        step,
        timeout,
        cancel_on_timeout,
    )


def _states_from_str(states_str: str) -> list[str]:
    """Return list of states from comma separated string.

    Also verify given states are valid.
    """
    return helpers.check_experiment_state(states_str).split(",")


STOPPED_STATES = set(_states_from_str("Terminated,Error"))


def _raise_timeout_msg(
    exp_str: str, stop_fct: Callable[[], None], cancel_on_timeout: bool
) -> None:
    msg = "Timeout reached"
    if cancel_on_timeout:
        msg += f", cancelling experiment {exp_str}"
        stop_fct()

    raise RuntimeError(msg)


def wait_state(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    state_fct: Callable[[], str],
    stop_fct: Callable[[], None],
    exp_str: str,
    states: str = "Running",
    step: int = 5,
    timeout: float = WAIT_TIMEOUT_DEFAULT,
    cancel_on_timeout: bool = False,
) -> str | None:
    """Wait until `state_fct` returns a state in `states`
    and also Terminated or Error

    :param state_fct: function that returns current state
    :param states: Comma separated string of states to wait for
    :param step: time to wait between each server check
    :param timeout: timeout if wait takes too long
    """
    expected_states = set(_states_from_str(states))
    start_time = time.time()

    while not _timeout(start_time, timeout):
        state = state_fct()

        if state in expected_states:
            return state

        if state in STOPPED_STATES:
            # Terminated or Error
            err = "Experiment {0} already in state '{1!s}'"
            raise RuntimeError(err.format(exp_str, state))

        # Still wait
        time.sleep(step)

    _raise_timeout_msg(exp_str, stop_fct, cancel_on_timeout)
    return None  # pragma: no cover


def _timeout(start_time: float, timeout: float) -> bool:
    """Return if timeout is reached.

    :param start_time: initial time
    :param timeout: timeout
    :param _now: allow overriding 'now' call
    """
    return time.time() > start_time + timeout


def exp_resources(
    nodes: list[str] | "AliasNodes",
    firmware_path: str | None = None,
    profile_name: str | None = None,
    **associations: str,
) -> dict[str, Any]:
    """Create an experiment resources dict.

    :param nodes: a list of nodes url or a AliasNodes object
        * ['m3-1.grenoble.iot-lab.info', 'wsn430-2.strasbourg.iot-lab.info']
        * AliasNodes(5, 'grenoble', 'm3:at86rf321', mobile=False)
    :param firmware_path: Firmware association
    :param profile_name: Profile association
    :param **associations: Other name associations
    """

    if isinstance(nodes, AliasNodes):
        exp_type = "alias"
    else:
        exp_type = "physical"

    resources = {
        "type": exp_type,
        "nodes": nodes,
        "firmware": firmware_path,
        "profile": profile_name,
        "associations": associations,
    }

    return resources


@dataclass(frozen=True)
class SiteAssociationTuple:
    """Holds the sites and keyword associations for a site association."""

    sites: tuple
    associations: dict


def site_association(*sites: str, **kwassociations: str) -> SiteAssociationTuple:
    """Return a site_association tuple."""
    if not sites:
        raise ValueError("No sites given")

    if len(sites) != len(set(sites)):
        raise ValueError(f"Sites are not uniq {sites}")

    # Associations are mandatory
    if not kwassociations:
        raise ValueError("No association given")

    return SiteAssociationTuple(sites, kwassociations)


class AliasNodes:  # pylint: disable=too-few-public-methods
    """An AliasNodes class

    >>> AliasNodes(5, 'grenoble', 'm3:at86rf231', False)
    AliasNodes(5, 'grenoble', 'm3:at86rf231', False, _alias='1')
    >>> save = AliasNodes(2, 'strasbourg', 'wsn430:cc1101', True)
    >>> save
    AliasNodes(2, 'strasbourg', 'wsn430:cc1101', True, _alias='2')

    >>> save == AliasNodes(2, 'strasbourg', 'wsn430:cc1101', True, _alias='2')
    True

    """

    _alias = 0  # static count of current alias number

    def __init__(
        self,
        nbnodes: int,
        site: str,
        archi: str,
        mobile: bool = False,
        _alias: str | None = None,
    ) -> None:
        """
        {
            "alias":"1",
            "nbnodes":1,
            "properties":{
                "archi":"wsn430:cc2420",
                "site":"devlille",
                "mobile":False
            }
        }
        """
        self.alias = self._alias_uid(_alias)
        self.nbnodes = nbnodes
        self.properties = {
            "archi": archi,
            "site": site,
            "mobile": mobile,
        }

    @classmethod
    def _alias_uid(cls, alias: str | int | None = None) -> str:
        """Return an unique uid string.

        if alias is given, return it as a String
        """
        if alias is None:
            cls._alias += 1
            alias = cls._alias
        return str(alias)

    def __repr__(self):  # pragma: no cover
        return (
            f"AliasNodes({self.nbnodes!r}, {self.properties['site']!r}, "
            f"{self.properties['archi']!r}, {self.properties['mobile']!r}, "
            f"_alias={self.alias!r})"
        )

    def __eq__(self, other):  # pragma: no cover
        return self.__dict__ == other.__dict__


# # # # # # # # # #
# Private methods #
# # # # # # # # # #

# Kwargs to initialize 'AssociationsMap' for nodes sorted.
_NODESMAPKWARGS = {"resource": "nodes", "sortkey": helpers.node_url_sort_key}


class _Experiment:  # pylint:disable=too-many-instance-attributes
    """Class describing an experiment"""

    ASSOCATTR_FMT = "{}associations"

    def __init__(
        self, name: str | None, duration: int, start_time: int | None = None
    ) -> None:
        self.duration = duration
        self.reservation = start_time
        self.name = name

        self.type = None
        self.nodes = []
        self.firmwareassociations = None
        self.profileassociations = None
        self.associations = None
        self.siteassociations = None
        self.profiles = None
        self.mobilities = None

    def _firmwareassociations(self):
        """Init and return firmwareassociations."""
        return setattr_if_none(
            self, "firmwareassociations", AssociationsMap("firmware", **_NODESMAPKWARGS)
        )

    def _profileassociations(self):
        """Init and return profileassociations."""
        return setattr_if_none(
            self, "profileassociations", AssociationsMap("profile", **_NODESMAPKWARGS)
        )

    def _associations(self, assoctype):
        """Init and return associations[assoctype]."""
        assocs = setattr_if_none(self, "associations", {})
        return assocs.setdefault(
            assoctype, AssociationsMap(assoctype, **_NODESMAPKWARGS)
        )

    def _siteassociations(self, assoctype):
        """Init and return associations[assoctype]."""
        assocs = setattr_if_none(self, "siteassociations", {})
        return assocs.setdefault(assoctype, AssociationsMap(assoctype, "sites"))

    @classmethod
    def from_dict(cls, exp_dict):
        """Create an _Experiment object from given `exp_dict`."""
        experiment = cls(
            exp_dict.pop("name", None),
            exp_dict.pop("duration"),
            exp_dict.pop("reservation", None),
        )

        experiment.type = exp_dict.pop("type")
        experiment.nodes = exp_dict.pop("nodes")

        if "profiles" in exp_dict.keys():
            experiment.profiles = exp_dict.pop("profiles")

        if "mobilities" in exp_dict.keys():
            experiment.mobilities = exp_dict.pop("mobilities")

        experiment._load_assocs(**exp_dict)  # pylint:disable=protected-access
        # No checking
        return experiment

    def _load_assocs(
        self,
        firmwareassociations=None,
        profileassociations=None,
        associations=None,
        siteassociations=None,
    ):
        """Load associations to AssociationsMap and set attributes."""
        self.firmwareassociations = AssociationsMap.from_list(
            firmwareassociations, "firmware", **_NODESMAPKWARGS
        )
        self.profileassociations = AssociationsMap.from_list(
            profileassociations, "profile", **_NODESMAPKWARGS
        )
        self.associations = associationsmapdict_from_dict(
            associations, **_NODESMAPKWARGS
        )
        self.siteassociations = associationsmapdict_from_dict(siteassociations, "sites")

    def _set_type(self, exp_type: str) -> None:
        """Set current experiment type.
        If type was already set and is different ValueError is raised
        """
        if self.type is not None and self.type != exp_type:
            raise ValueError(
                "Invalid experiment, should be only physical or only alias"
            )
        self.type = exp_type

    def add_exp_resources(self, resources):
        """Add 'exp_resources' to current experiment
        It will update node type, nodes, firmware and profile associations
        """
        # Alias/Physical
        self._set_type(resources["type"])

        # register nodes in experiment
        nodes = resources["nodes"]
        self._register_nodes(nodes)  # pylint:disable=not-callable
        nodes = self._nodes_to_assoc(nodes)

        # register firmware
        if resources["firmware"] is not None:
            name = nodes_association_name("firmware", resources["firmware"])
            self._firmwareassociations().extendvalues(name, nodes)

        # register profile, may be None
        if resources["profile"] is not None:
            name = nodes_association_name("profile", resources["profile"])
            self._profileassociations().extendvalues(name, nodes)

        # Add other associations
        associations = resources.get("associations", {})
        for assoctype, assocname in associations.items():
            self._add_nodes_association(nodes, assoctype, assocname)

    def _add_nodes_association(self, nodes, assoctype, assocname):
        """Add given association."""
        name = nodes_association_name(assoctype, assocname)
        self._associations(assoctype).extendvalues(name, nodes)

    def _nodes_to_assoc(self, nodes):
        """Returns nodes to use in association."""
        return [nodes.alias] if self.type == "alias" else nodes

    def add_site_association(self, assoc):
        """Add a site_association."""
        for assoctype, assocname in assoc.associations.items():
            self._add_site_association(assoc.sites, assoctype, assocname)

    def _add_site_association(self, sites, assoctype, assocname):
        """Add given site association."""
        name = site_association_name(assoctype, assocname)
        self._siteassociations(assoctype).extendvalues(name, sites)

    def set_physical_nodes(self, nodes_list):
        """Set physical nodes list"""
        self._set_type("physical")

        # Check that nodes are not already present
        _intersect = list(set(self.nodes) & set(nodes_list))
        if _intersect:
            raise ValueError(f"Nodes specified multiple times {_intersect}")

        self.nodes.extend(nodes_list)
        # Keep unique values and sorted
        self.nodes = sorted(list(set(self.nodes)), key=helpers.node_url_sort_key)

    def set_alias_nodes(self, alias_nodes):
        """Set alias nodes list"""
        self._set_type("alias")
        self.nodes.append(alias_nodes)

    @property
    def _register_nodes(self):
        """Register nodes with the correct method according to exp `type`."""
        assert self.type is not None
        _register_fct_dict = {
            "physical": self.set_physical_nodes,
            "alias": self.set_alias_nodes,
        }
        return _register_fct_dict[self.type]

    def filenames(self):
        """Extract list of filenames required."""
        # No need to check nodes associations if there is only 'firmware'
        assert NODES_ASSOCIATIONS_FILE_ASSOCS == ("firmware",)

        files = []
        # Handle None attributes
        files += (self.firmwareassociations or {}).keys()
        for assoctype in SITE_ASSOCIATIONS_FILE_ASSOCS:
            files += (self.siteassociations or {}).get(assoctype, {}).keys()

        return files


def setattr_if_none(obj: Any, attr: str, default: Any) -> Any:
    """Set attribute as `default` if None

    :returns: attribute value after update
    """
    # Set default if None
    if getattr(obj, attr) is None:
        setattr(obj, attr, default)

    return getattr(obj, attr)


def _write_experiment_archive(exp_id: int, data: bytes) -> None:
    """Write experiment archive contained in 'data' to 'exp_id.tar.gz'"""
    with open(f"{exp_id}.tar.gz", "wb") as archive:
        archive.write(data)


def nodes_association_name(assoctype: str, assocname: str) -> str:
    """Adapt assocname depending of assoctype.

    Return basename(assocname) if assoctype is a file-association.
    """
    return _basename_if_in(assocname, assoctype, NODES_ASSOCIATIONS_FILE_ASSOCS)


def site_association_name(assoctype: str, assocname: str) -> str:
    """Adapt assocname depending on assoctype.

    * Return basename(assocname) if assoctype is a file-association.
    """
    return _basename_if_in(assocname, assoctype, SITE_ASSOCIATIONS_FILE_ASSOCS)


def _basename_if_in(
    value: str,
    key: str,
    container: tuple[str, ...],
    transform: Callable[[str], str] = basename,
) -> str:
    """Return basename if in.

    >>> _basename_if_in('a/b', 1, [1])
    'b'
    >>> _basename_if_in('a/b', 2, (1,))
    'a/b'
    """
    return transform(value) if key in container else value
