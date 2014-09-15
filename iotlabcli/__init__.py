""" iotlabcli package implementing a cli for iotlab REST API """
VERSION = "1.3.1"

import json


class Error(Exception):
    """ iotlabcli Exception

    >>> raise Error('error_message')
    Traceback (most recent call last):
    Error: 'error_message'
    """
    def __init__(self, value):
        super(Error, self).__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


class _Encoder(json.JSONEncoder):
    """ Encoder for serialization object python to JSON format """
    def default(self, obj):  # pylint: disable=method-hidden
        try:
            return obj.serialize()
        except AttributeError:
            return obj.__dict__


def json_dumps(obj):
    """ Dumps data to json """
    return json.dumps(obj, cls=_Encoder, sort_keys=True, indent=4)
