""" iotlabcli package implementing a cli for iotlab REST API """
VERSION = "1.3.1"

import json


class Error(Exception):
    """ iotlabcli Exception

    >>> raise Error('error_message')  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    iotlabcli.Error: 'error_message'
    """
    def __init__(self, message):
        super(Error, self).__init__()
        self.message = message

    def __str__(self):
        return str(self.message)


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
