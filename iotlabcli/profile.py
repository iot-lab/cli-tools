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

"""Class python for Profile serialization JSON"""

from dataclasses import dataclass, field

# pylint:disable=too-few-public-methods


@dataclass
class ProfileM3A8:
    """A generic Profile for M3 and A8"""

    choices = {
        "power_mode": ["dc", "battery"],
        "consumption": {
            "period": [140, 204, 332, 588, 1100, 2116, 4156, 8244],
            "average": [1, 4, 16, 64, 128, 256, 512, 1024],
        },
        "radio": {
            "channels": range(11, 27),
            "num_per_channel": range(0, 256),
            "period": range(1, 2**16),
        },
    }
    arch = None

    profilename: str
    power: str
    nodearch: str = field(init=False)
    consumption: dict | None = field(init=False)
    radio: dict | None = field(init=False)

    def __post_init__(self) -> None:
        assert self.power in self.choices["power_mode"]
        assert self.arch is not None, "Using Generic class"
        self.nodearch = self.arch
        self.consumption = None
        self.radio = None

    def set_consumption(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        period: int | None,
        average: int | None,
        power: bool = False,
        voltage: bool = False,
        current: bool = False,
    ) -> None:
        """Configure consumption measures"""
        if not power and not voltage and not current:
            return
        _err = "Required values period/average for consumption measure."
        assert period is not None and average is not None, _err

        assert period in self.choices["consumption"]["period"]
        assert average in self.choices["consumption"]["average"]
        self.consumption = {
            "period": period,
            "average": average,
            "power": power,
            "voltage": voltage,
            "current": current,
        }

    def set_radio(
        self,
        mode: str | None,
        channels: list[int] | None,
        period: int | None = None,
        num_per_channel: int | None = None,
    ) -> None:
        """Configure radio measures"""
        if not mode:
            return
        assert channels
        for channel in channels:
            assert channel in self.choices["radio"]["channels"]

        assert mode in ["rssi", "sniffer"]
        self.radio = {"mode": mode}

        config_radio = {
            "rssi": self._cfg_radio_rssi,
            "sniffer": self._cfg_radio_sniffer,
        }
        config_radio[mode](channels, period, num_per_channel)

    def _cfg_radio_rssi(
        self,
        channels: list[int],
        period: int,
        num_per_channel: int | None = None,
    ) -> None:
        """Check parameters for rssi measures and set config"""
        num_per_channel = num_per_channel or 0

        _err = "Required 'channels/period' for radio rssi measure"
        assert period is not None and channels is not None, _err

        # num_per_channel is required when multiple channels are given
        _err = "Required 'num_per_channel' as multiple channels provided"
        assert len(channels) == 1 or num_per_channel != 0, _err

        assert period in self.choices["radio"]["period"]
        assert num_per_channel in self.choices["radio"]["num_per_channel"]

        # Write usefull parameters
        self.radio["channels"] = channels
        self.radio["period"] = period
        self.radio["num_per_channel"] = num_per_channel

    def _cfg_radio_sniffer(
        self,
        channels: list[int],
        period: int | None = None,
        num_per_channel: int | None = None,
    ) -> None:
        """Check parameters for sniffer measures and set the configuration"""

        # 'Period' and multiple channels should be handled later when supported
        _err = "`period` and `num_per_channel` not allowed for sniffer"
        assert period is None and num_per_channel is None, _err

        assert len(channels) == 1, "Only one channel is allowed"

        # Write config
        self.radio["channels"] = channels
        self.radio["period"] = None
        self.radio["num_per_channel"] = None


class ProfileM3(ProfileM3A8):
    """A Profile measure class for M3."""

    arch = "m3"


class ProfileA8(ProfileM3A8):
    """A Profile measure class for A8."""

    arch = "a8"


class ProfileCustom(ProfileM3A8):
    """A Profile measure class for Custom."""

    arch = "custom"
