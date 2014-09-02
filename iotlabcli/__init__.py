""" iotlabcli package implementing a cli for iotlab REST API """
VERSION = "1.3.1"


class Error(Exception):
    """ iotlabcli error """
    def __init__(self, value):
        super(Error, self).__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)
