# Copyright (c) 2020 FTI-CAS
#

from glanceclient import client as glanceclient

from application import app
from application.product_types.openstack.utils import keystone_util as ks_util

LOG = app.logger

DEFAULT_GLANCE_API_VERSION = 1.0


def get_glance_client_version():
    """
    Get Glance API version
    :return:
    """
    try:
        api_version = app.config['OS_SERVICES_VERSION']['glance']
    except KeyError:
        return DEFAULT_GLANCE_API_VERSION
    else:
        return api_version


def get_glance_client():
    """
    Get Glance client
    :return:
    """
    sess = ks_util.get_session()
    return glanceclient.Client(get_glance_client_version(), session=sess)
