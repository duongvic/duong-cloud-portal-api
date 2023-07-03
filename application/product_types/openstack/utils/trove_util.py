#
# Copyright (c) 2020 FTI-CAS
#

from troveclient import client as troveclient

from application import app
from application.product_types.openstack.utils import keystone_util as ks_util
from application.utils.data_util import valid_kwargs

LOG = app.logger

DEFAULT_TROVE_API_VERSION = 1.0


def get_trove_client_version():
    """
    Get Trove API version
    :return:
    """
    try:
        api_version = app.config['OS_SERVICES_VERSION']['trove']
    except KeyError:
        return DEFAULT_TROVE_API_VERSION
    else:
        return api_version


@valid_kwargs('endpoint_type', 'service_type', 'region_name')
def get_glance_client(os_auth, **kwargs):
    """
    Get Glance client
    :param kwargs
    :return:
    """
    sess = ks_util.get_session(os_auth)
    return troveclient.Client(get_trove_client_version(), session=sess, **kwargs)


