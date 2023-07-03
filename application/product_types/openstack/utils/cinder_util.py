#
# Copyright (c) 2020 FTI-CAS
#

import logging
import os

from cinderclient import client as cinderclient

from application import app
from application.product_types.openstack.utils import keystone_util as ks_util

LOG = app.logger

DEFAULT_CINDER_API_VERSION = 1.0


def get_cinder_client_version():
    """
    Get Cinder API version
    :return:
    """
    try:
        api_version = app.config['OS_SERVICES_VERSION']['cinder']
    except KeyError:
        return DEFAULT_CINDER_API_VERSION
    else:
        return api_version


def get_cinder_client(os_info):
    """
    Get Cinder client

    :param os_info
    """
    sess = ks_util.get_session(os_info)
    return cinderclient.Client(get_cinder_client_version(), session=sess)
