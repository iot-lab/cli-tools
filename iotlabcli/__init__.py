""" iotlabcli package implementing a cli for iotlab REST API """
VERSION = "1.3.1"


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
