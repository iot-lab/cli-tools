""" iotlabcli package implementing a cli for iotlab REST API """
__version__ = "1.5.3"

# flake8: noqa

# simpler access for external usage
from iotlabcli.auth import get_user_credentials
from iotlabcli.rest import Api
from iotlabcli.helpers import get_current_experiment
