# -*- coding:utf-8 -*-
"""Class python for Profile serialization JSON"""

# pylint:disable=too-few-public-methods


class ProfileM3(object):
    """A Profile measure class for M3 """
    choices = {
        'power_mode': ['dc', 'battery'],
        'consumption': {'period': [140, 204, 332, 588, 1100, 2116, 4156, 8244],
                        'average': [1, 4, 16, 64, 128, 256, 512, 1024]},
        'radio': {'channels': range(11, 27), 'num_per_channel': range(0, 256),
                  'period': range(1, 2**16)}
    }

    def __init__(self, profilename, power):
        assert power in ProfileM3.choices['power_mode']
        self.nodearch = 'm3'
        self.profilename = profilename
        self.power = power

        self.consumption = None
        self.radio = None

    # pylint: disable=too-many-arguments
    def set_consumption(self, period, average,
                        power=False, voltage=False, current=False):
        """ Configure consumption measures """
        if not power and not voltage and not current:
            return
        _err = "Required values period/average for consumption measure."
        assert period is not None and average is not None, _err

        assert period in self.choices['consumption']['period']
        assert average in self.choices['consumption']['average']
        self.consumption = {
            'period': period,
            'average': average,
            'power': power,
            'voltage': voltage,
            'current': current,
        }

    def set_radio(self, mode, channels, period=None, num_per_channel=0):
        """ Configure radio measures """
        if not mode:
            return
        for channel in channels:
            assert channel in self.choices['radio']['channels']

        assert mode in ['rssi']
        self._check_radio_rssi(channels, period, num_per_channel)

        self.radio = {
            'mode': mode,
            'period': period,
            'channels': channels,
            'num_per_channel': num_per_channel,
        }

    def _check_radio_rssi(self, channels, period, num_per_channel=0):
        """ Check parameters for rssi measures """

        _err = "Required 'channels/period' for radio rssi measure"
        assert period is not None and channels is not None, _err

        # num_per_channels is required when multiple channels are given
        _err = "Required 'num_per_channels' as multiple channels provided"
        assert len(channels) == 1 or num_per_channel != 0, _err

        assert period in self.choices['radio']['period']
        assert num_per_channel in self.choices['radio']['num_per_channel']

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class ProfileWSN430(object):
    """A Profile measure class for WSN430 """
    choices = {
        'power_mode': ['dc', 'battery'],
        'consumption': {'frequency': [5000, 1000, 500, 100, 70]},
        'radio': {'frequency': [5000, 1000, 500]},
        'sensor': {'frequency': [30000, 10000, 5000, 1000]},
    }

    def __init__(self, profilename, power):
        assert power in ProfileWSN430.choices['power_mode']
        self.nodearch = 'wsn430'
        self.profilename = profilename
        self.power = power

        self.consumption = None
        self.radio = None
        self.sensor = None

    def set_consumption(self, frequency, power=False, voltage=False,
                        current=False):
        """ Configure consumption measures """
        if not power and not voltage and not current:
            return
        _err = "Required 'frequency' for consumption measure"
        assert frequency is not None, _err

        assert frequency in self.choices['consumption']['frequency']
        self.consumption = {
            'frequency': frequency,
            'power': power,
            'voltage': voltage,
            'current': current,
        }

    def set_radio(self, frequency):
        """ Configure radio measures """
        if not frequency:
            return
        assert frequency in self.choices['radio']['frequency']
        self.radio = {
            'frequency': frequency,
            'rssi': True,
        }

    def set_sensors(self, frequency, temperature=False, luminosity=False):
        """ Configure sensor measures """
        if not temperature and not luminosity:
            return
        _err = "Required 'frequency' for sensor measure"
        assert frequency is not None, _err

        assert frequency in self.choices['sensor']['frequency']
        self.sensor = {
            'frequency': frequency,
            'luminosity': luminosity,
            'temperature': temperature,
        }

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
