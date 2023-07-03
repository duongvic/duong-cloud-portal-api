#
# Copyright (c) 2020 FTI-CAS
#
from foxcloud import exceptions as fox_exc
from foxcloud import client as fox_client

from application import app
from application.product_types.openstack import os_base

LOG = app.logger


def get_magnum_client(cluster, os_config, engine='console', services='lbaas'):
    """
    Create OS client.
    :param cluster:
    :param os_config:
    :param engine:
    :param services:
    :return:
    """
    return MagnumAPI(cluster=cluster, os_config=os_config, engine=engine, services=services)


class MagnumAPI(os_base.OSBaseMixin):
    def get_clusters(self, listing={}, filters={}):
        """
        List all clusters
        :param listing:
        :param filters:
        :return:
        """
        try:
            data = self.client.coe.get_clusters(**filters)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_clusters()]: %s.", e)
            return self.fail(e)

    def get_cluster(self, cluster_id, listing={}):
        """
        Get a specific cluster
        :param listing:
        :param cluster_id:
        :return:
        """
        try:
            data = self.client.coe.get_cluster(cluster_id=cluster_id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_cluster(%s)]: %s.", cluster_id, e)
            return self.fail(e)

    def create_cluster(self, name, template_id, keypair_id, node_flavor_id, master_flavor_id,
                       node_count=1, master_count=1, network_id=None, subnet_id=None, timeout=3600,
                       floating_ip_enabled=True, labels={}, wait=False):

        try:
            data = self.client.coe.create_cluster(name=name, template_id=template_id, keypair_id=keypair_id,
                                                  node_flavor_id=node_flavor_id, master_flavor_id=master_flavor_id,
                                                  node_count=node_count, master_count=master_count,
                                                  network_id=network_id,
                                                  subnet_id=subnet_id, timeout=timeout,
                                                  floating_ip_enabled=floating_ip_enabled, labels=labels, wait=wait)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_cluster()]: %s.", e)
            return self.fail(e)

    def update_cluster(self, id, patch):
        """
        Update an existing cluster
        :param id:
        :param patch:
        :return:
        """
        try:
            data = self.client.coe.update_cluster(cluster_id=id, patch=patch)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [update_cluster_template(%s)]: %s.", id, e)
            return self.fail(e)

    def delete_cluster(self, id):
        """
        Delete an existing cluster
        :param id:
        :return:
        """
        try:
            data = self.client.coe.delete_cluster(cluster_id=id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_cluster(%s)]: %s.", id, e)
            return self.fail(e)

    def get_cluster_templates(self, listing={}, filters={}):
        """
        List all cluster_templates
        :param listing:
        :param filters:
        :return:
        """
        try:
            data = self.client.coe.get_cluster_templates()
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_cluster_templates()]: %s.", e)
            return self.fail(e)

    def get_cluster_template(self, template_id, listing={}):
        """
        Get a specific cluster_template
        :param listing:
        :param template_id:
        :return:
        """
        try:
            data = self.client.coe.get_cluster_template(template_id=template_id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_cluster_template(%s)]: %s.", template_id, e)
            return self.fail(e)

    def create_cluster_template(self, name, keypair_id, docker_volume_size, external_network_id, image_id,
                                coe='kubernetes', network_driver='flannel', dns='8.8.8.8',
                                master_lb_enabled=False, floating_ip_enabled=True, volume_driver='cinder',
                                server_type='vm', docker_storage_driver='overlay', tls_disabled=True,
                                is_public=False, hidden=False, labels={}, wait=False, **kwargs):
        """
        Create a new cluster template
        :param name:
        :param keypair_id:
        :param docker_volume_size:
        :param external_network_id:
        :param image_id:
        :param coe:
        :param network_driver:
        :param dns:
        :param master_lb_enabled:
        :param floating_ip_enabled:
        :param volume_driver:
        :param server_type:
        :param docker_storage_driver:
        :param tls_disabled:
        :param is_public:
        :param hidden:
        :param labels:
        :param wait:
        :param kwargs:
        :return:
        """
        try:
            data = self.client.coe.create_cluster_template(name=name, keypair_id=keypair_id,
                                                           docker_volume_size=docker_volume_size,
                                                           external_network_id=external_network_id,
                                                           image_id=image_id, coe=coe, network_driver=network_driver,
                                                           dns=dns, master_lb_enabled=master_lb_enabled,
                                                           floating_ip_enabled=floating_ip_enabled,
                                                           volume_driver=volume_driver,
                                                           server_type=server_type,
                                                           docker_storage_driver=docker_storage_driver,
                                                           tls_disabled=tls_disabled, is_public=is_public,
                                                           hidden=hidden, labels=labels, wait=wait, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_cluster_template()]: %s.", e)
            return self.fail(e)

    def update_cluster_template(self, id, patch):
        """
        Update an existing cluster_template
        :param id:
        :param patch:
        :return:
        """
        try:
            data = self.client.coe.update_cluster_template(template_id=id, patch=patch)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [update_cluster_template(%s)]: %s.", id, e)
            return self.fail(e)

    def delete_cluster_template(self, id):
        """
        Delete an existing cluster_template
        :param id:
        :return:
        """
        try:
            data = self.client.coe.delete_cluster_template(template_id=id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_cluster_template(%s)]: %s.", id, e)
            return self.fail(e)
