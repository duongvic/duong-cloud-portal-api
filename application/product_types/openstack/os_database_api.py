#
# Copyright (c) 2020 FTI-CAS
#
from foxcloud import exceptions as fox_exc

from application import app
from application.product_types.openstack import os_base

LOG = app.logger


def get_database_client(cluster, os_config, engine='console', services='trove'):
    """
    Create OS client.
    :param cluster:
    :param os_config:
    :param engine:
    :param services:
    :return:
    """
    return DatabaseAPI(cluster=cluster, os_config=os_config, engine=engine, services=services)


class DatabaseAPI(os_base.OSBaseMixin):
    def get_datastores(self, limit=None, marker=None, listing={}):
        """
        List all datastores
        :param listing:
        :return:
        """
        try:
            data = self.client.trove.get_datastores(limit=limit, marker=marker)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_clusters()]: %s.", e)
            return self.fail(e)

    def get_datastore(self, datastore_id, listing={}):
        """
        Get a specific datastore
        :param listing:
        :param cluster_id:
        :return:
        """
        try:
            data = self.client.trove.get_datastore(datastore_id=datastore_id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_datastore(%s)]: %s.", datastore_id, e)
            return self.fail(e)

    def get_datastore_versions(self, datastore_id, limit=None, marker=None, listing={}):
        """
        List all datastore_versions
        :param listing:
        :return:
        """
        try:
            data = self.client.trove.get_datastore_versions(datastore_id=datastore_id,
                                                            limit=limit, marker=marker)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_clusters()]: %s.", e)
            return self.fail(e)

    def get_datastore_version(self, datastore_id, version_id, listing={}):
        """
        Get a specific datastore_version
        :param listing:
        :param datastore_id:
        :param version_id:
        :return:
        """
        try:
            data = self.client.trove.get_datastore_version(datastore_id=datastore_id,
                                                           datastore_version_id=version_id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            print(e)
            LOG.error("Error [get_datastore_version(%s)]: %s.", version_id, e)
            return self.fail(e)

    def get_clusters(self, listing={}):
        """
        List all clusters
        :param listing:
        :param filters:
        :return:
        """
        try:
            data = self.client.trove.get_clusters()
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_clusters()]: %s.", e)
            return self.fail(e)

    def get_cluster(self, id, listing={}):
        """
        Get a specific cluster
        :param listing:
        :param id:
        :return:
        """
        try:
            data = self.client.trove.get_cluster(cluster_id=id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_lb(%s)]: %s.", id, e)
            return self.fail(e)

    def create_cluster(self, name, datastore_id, datastore_version_id, flavor_id, volume_size,
                       volume_type=None, number_of_instances=3, network_id=None, locality=None,
                       availability_zone=None, extended_properties=None, configuration=None,
                       wait=False):
        """

        :param name:
        :param datastore_id:
        :param datastore_version_id:
        :param flavor_id:
        :param volume_size:
        :param volume_type:
        :param number_of_instances:
        :param network_id:
        :param locality:
        :param availability_zone:
        :param extended_properties:
        :param configuration:
        :param wait:
        :return:
        """
        try:
            data = self.client.trove.create_cluster(name=name, datastore_id=datastore_id,
                                                    datastore_version_id=datastore_version_id,
                                                    flavor_id=flavor_id, volume_size=volume_size,
                                                    volume_type=volume_type,
                                                    number_of_instances=number_of_instances,
                                                    network_id=network_id, locality=locality,
                                                    availability_zone=availability_zone,
                                                    extended_properties=extended_properties,
                                                    configuration=configuration, wait=wait)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_cluster(%s)]: %s.", name, e)
            return self.fail(e)

    def update_cluster(self, id, **kwargs):
        """
        Update an existing cluster
        :param id:
        :param kwargs:
        :return:
        """
        try:
            data = self.client.trove.update_cluster(cluster_id=id, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [update_cluster(%s)]: %s.", id, e)
            return self.fail(e)

    def delete_cluster(self, id):
        """
        Delete an existing cluster
        :param id:
        :return:
        """
        try:
            data = self.client.trove.delete_cluster(cluster_id=id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_cluster(%s)]: %s.", id, e)
            return self.fail(e)

    def get_instances(self, listing={}, filters={}):
        """
        List all instances
        :param listing:
        :param filters:
        :return:
        """
        try:
            data = self.client.trove.get_instances(**filters)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_instances()]: %s.", e)
            return self.fail(e)

    def get_instance(self, id, listing={}):
        """
        Get a specific instance
        :param listing:
        :param id:
        :return:
        """
        try:
            data = self.client.trove.get_instance(instance_id=id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_lb(%s)]: %s.", id, e)
            return self.fail(e)

    def create_instance(self, name, flavor_id=None, volume=None, databases=None,
                        users=None, restore_point=None, availability_zone=None,
                        datastore_id=None, datastore_version_id=None, nics=None,
                        configuration=None, replica_of=None, replica_count=None,
                        modules=None, locality=None, region_name=None, access=None,
                        wait=False, **kwargs):
        """
        Create a new instance
        :param name:
        :param flavor_id:
        :param volume:
        :param databases:
        :param users:
        :param restore_point:
        :param availability_zone:
        :param datastore_id:
        :param datastore_version_id:
        :param nics:
        :param configuration:
        :param replica_of:
        :param replica_count:
        :param modules:
        :param locality:
        :param region_name:
        :param access:
        :param wait:
        :param kwargs:
        :return:
        """
        try:
            data = self.client.trove.create_instance(name, flavor_id, volume, databases,
                                                     users, restore_point, availability_zone,
                                                     datastore_id, datastore_version_id, nics,
                                                     configuration, replica_of, replica_count,
                                                     modules, locality, region_name, access,
                                                     wait, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_instance(%s)]: %s.", name, e)
            return self.fail(e)

    def update_instance(self, id, **kwargs):
        """
        Update an existing instance
        :param id:
        :param kwargs:
        :return:
        """
        try:
            volume_size = kwargs.pop('volume_size', None)
            if volume_size:
                data = self.client.trove.resize_volume(instance_id=id,
                                                       volume_size=volume_size)
                return data.parse()

            if kwargs.get('name') or kwargs.get('configuration'):
                data = self.client.trove.update_instance(instance_id=id, **kwargs)
                return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [update_instance(%s)]: %s.", id, e)
            return self.fail(e)

    def perform_action(self, id, action='restart'):
        try:
            data = self.client.trove.do_instance_action(instance_id=id, action=action)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [perform_action(%s)]: %s.", id, e)
            return self.fail(e)

    def delete_instance(self, id, force=False):
        """
        Delete an existing instance
        :param id:
        :param force:
        :return:
        """
        try:
            data = self.client.trove.delete_instance(instance_id=id, force=force)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_instance(%s)]: %s.", id, e)
            return self.fail(e)

    def get_backups(self, instance_id, datastore_id, listing={}, filters={}):
        """
        List all backups
        :param instance_id:
        :param datastore_id:
        :param listing:
        :param filters:
        :return:
        """
        try:
            data = self.client.trove.get_backups(instance_id=instance_id, datastore_id=datastore_id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_backups()]: %s.", e)
            return self.fail(e)

    def get_backup(self, id, listing={}):
        """
        Get a specific backup
        :param listing:
        :param id:
        :return:
        """
        try:
            data = self.client.trove.get_backup(backup_id=id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_lb(%s)]: %s.", id, e)
            return self.fail(e)

    def create_backup(self, name, description, instance_id, **kwargs):
        """
        Create a new backup
        :param name:
        :param description:
        :param protocol:
        :param port:
        :param lb_id:
        :param wait:
        :param kwargs:
        :return:
        """
        try:
            data = self.client.trove.create_backup(name=name, description=description,
                                                   instance_id=instance_id, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_backup(%s)]: %s.", name, e)
            return self.fail(e)

    def update_backup(self, id, **kwargs):
        """
        Update an existing backup
        :param id:
        :param kwargs:
        :return:
        """

    def delete_backup(self, id):
        """
        Delete an existing backup
        :param id:
        :return:
        """
        try:
            data = self.client.trove.delete_backup(backup_id=id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_backup(%s)]: %s.", id, e)
            return self.fail(e)
