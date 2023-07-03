#
# Copyright (c) 2020 FTI-CAS
#

from neutronclient.neutron import client as neutronclient

from application import app
from application.product_types.openstack.utils import keystone_util as ks_util

LOG = app.logger

DEFAULT_NEUTRON_API_VERSION = 1.0


def get_neutron_client_version():
    """
    Get Neutron API version
    :return:
    """
    try:
        api_version = app.config['OS_SERVICES_VERSION']['neutron']
    except KeyError:
        return DEFAULT_NEUTRON_API_VERSION
    else:
        return api_version


def get_neutron_client(os_info):
    """
    Get Neutron client

    :param os_info
    :return
    """
    sess = ks_util.get_session(os_info)
    return neutronclient.Client(get_neutron_client_version(), session=sess)

