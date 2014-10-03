""" iotlabcli package implementing a cli for iotlab REST API """
VERSION = "1.4.0"
import json


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
