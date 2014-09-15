# -*- coding:utf-8 -*-
"""Class python for Profile serialization JSON"""

# pylint:disable=too-few-public-methods


class Consumption(object):
    """A Consumption measure class"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Radio(object):
    """A Radio measure class"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Sensor(object):
    """A Sensor measure class"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Profile(object):
    """A Profile measure class"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
