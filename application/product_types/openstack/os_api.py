#
# Copyright (c) 2020 FTI-CAS
#
from foxcloud import client as fox_client
from application import app
from application.product_types.openstack import (os_base, os_api_identity, os_api_compute,
                                                 os_api_network, os_api_image, os_api_volume)

LOG = app.logger

CLUSTERS = {}


def init_clusters(clusters_config):
    """
    Init cluster API.
    :param clusters_config:
    :return:
    """
    clusters = {}
    for info in clusters_config['clusters']:
        clusters[info['cluster']] = {
            'info': info,
        }

    global CLUSTERS
    CLUSTERS = clusters


def iter_clusters():
    """
    Iterate over clusters info.
    :return:
    """
    for k, v in CLUSTERS.items():
        yield v['info']


def get_cluster_config(cluster):
    """
    Get config for cluster.
    :param cluster:
    :return:
    """
    return CLUSTERS[cluster]['info']


def find_target_cluster(info):
    """
    Choose cluster for compute provisioning.
    :param info:
    :return:
    """
    region_id = info['region_id']
    target_clusters = info.get('target_clusters') or None
    ignored_clusters = info.get('ignored_clusters') or None

    found = []
    for info in iter_clusters():
        if not info.get("enabled"):
            continue
        cluster = info['cluster']
        if target_clusters is not None and cluster not in target_clusters:
            continue
        if ignored_clusters is not None and cluster in ignored_clusters:
            continue
        if info['region_id'] == region_id:
            found.append(info)

    if not found:
        raise ValueError('Found no cluster for region {}.'.format(region_id))

    # TODO
    return found[0]


def get_project_quotas(cluster):
    """
    Get project quota for cluster.

    :param cluster:
    :return:
    """
    os_info = CLUSTERS[cluster]['os_info']
    return os_info['project']['quotas']


def get_mtu_size(cluster):
    """
    Get max transmission unit.
    This is the largest data package that the network will accept

    :param cluster:
    :return:
        """
    quotas = get_project_quotas(cluster=cluster)
    return quotas['mtu_size']


def get_heat_api_version():
    """
    Get heat version

    :return
    """
    return app.config['HEAT_API_VERSION']['heat']


def get_os_client(cluster, os_config, engine='console', services='shade'):
    """
    Create OS client.
    :param cluster:
    :param os_config:
    :param engine:
    :param services:
    :return:
    """
    return OpenstackAPI(cluster=cluster, os_config=os_config,
                        engine=engine, services=services)


def get_admin_os_client(cluster, os_config=None, engine='console', services='shade'):
    """
    Create OS client.
    :param cluster:
    :param os_config:
    :param engine:
    :param services:
    :return:
    """
    if not os_config:
        cluster_config = get_cluster_config(cluster)
        os_info = cluster_config['os_info']
        os_config = {
            'region_name': os_info['region_name'],
            'auth': os_info['auth'],
        }
    return OpenstackAPI(cluster=cluster, os_config=os_config,
                        engine=engine, services=services)


class OpenstackAPI(os_base.OSBaseMixin,
                   os_api_identity.OSIdentityMixin, os_api_compute.OSComputeMixin,
                   os_api_network.OSNetworkMixin, os_api_volume.OSVolumeMixin,
                   os_api_image.OSImageMixin):
    """Api interface for OpenStack"""

    @property
    def default_domain(self):
        auth = self.os_config['auth']
        return auth.get('user_domain_name') or 'tripleodomain'
