#
# Copyright (c) 2020 FTI-CAS
#

import munch
from shade import exc
from foxcloud import exceptions as fox_exc

from application import app
from application.base import errors
from application.utils import data_util
from application.utils.data_util import valid_kwargs

LOG = app.logger


class OSVolumeMixin(object):

    def get_volume_id(self, volume_name):
        try:
            data = self.client.shade.get_volume_id(volume_name)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_volume_id(%s)]: %s.", volume_name, e)
            return self.fail(e)

    def get_volume(self, volume_id, filters=None, listing={}):
        """
        Get a volume by name or ID.

        :param volume_id: ID of the volume.
        :param filters: A dictionary of meta data to use for further filtering.

        :returns: A volume ``munch.Munch`` or None if no matching volume is found.
        """
        try:
            data = self.client.shade.get_volume(name_or_id=volume_id, filters=filters)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_volume(%s)]: %s.", volume_id, e)
            return self.fail(e)

    def get_volumes(self, server_id=None, cache=True, listing={}):
        """
        Get all available volumes.

        :param server_id: if pass, get all volumes of a server.
        :param cache:
        :returns: A list of volume ``munch.Munch``.
        """
        try:
            if server_id:
                server = {'id': server_id}
                data = self.client.shade.get_volumes(server=server, cache=cache)
            else:
                data = self.client.shade.list_volumes(cache=cache)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_volumes()]: %s.", e)
            return self.fail(e)

    def create_volume(self, size, wait=True, timeout=None,
                      image=None, **kwargs):
        """
        Create a volume.

        :param size: Size, in GB of the volume to create.
        :param wait: If true, waits for volume to be created.
        :param timeout: Seconds to wait for volume creation. None is forever.
        :param image: (optional) Image name, ID or object from which to create
                      the volume.

        :returns: The created volume object.
        """
        try:
            data = self.client.shade.create_volume(size, wait=wait, timeout=timeout,
                                                   image=image, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_volume(%s, %s)]: %s.", size, image, e)
            return self.fail(e)

    def delete_volume(self, name_or_id=None, wait=True, timeout=None):
        """
        Delete a volume.

        :param name_or_id:(string) Name or unique ID of the volume.
        :param wait:(bool) If true, waits for volume to be deleted.
        :param timeout:(string) Seconds to wait for volume deletion. None is forever.

        :return:  True on success, False otherwise.
        """
        try:
            data = self.client.shade.delete_volume(name_or_id=name_or_id,
                                                   wait=wait, timeout=timeout)
            return self.parse(data)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_volume(%s)]: %s.", name_or_id, e)
            return self.fail(e)

    def detach_volume(self, server_id, volume_id,
                      wait=True, timeout=None):
        """
        Detach a volume from a server.

        :param server_id: The server name or id to detach from.
        :param volume_id: The volume name or id to detach.
        :param wait: If true, waits for volume to be detached.
        :param timeout: Seconds to wait for volume detachment. None is forever.

        :return: True on success.
        """
        try:
            data = self.client.shade.get_volume(volume_id)
            error, volume = data.parse()
            if error:
                return self.fail(error)
            data = self.client.shade.get_server(server_id=server_id, detailed=True)
            error, server = data.parse()
            if error:
                return self.fail(error)

            data = self.client.detach_volume(server['id'], volume['id'], wait=wait, timeout=timeout)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [detach_volume(%s, %s)]: %s.", server_id, volume_id, e)
            return self.fail(e)

    # *************************************
    # SNAPSHOT
    # *************************************

    def get_snapshot(self, snapshot_id, listing={}):
        """
        Get a snapshot by name or ID.

        :param snapshot_id: ID of the volume snapshot.
        :param filters:
        :returns:
        """
        try:
            data = self.client.shade.get_volume_snapshot(snapshot_id=snapshot_id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_volume_snapshot(%s)]: %s.", snapshot_id, e)
            return self.fail(e)

    def get_snapshots(self, info, listing={}):
        """
        Get a snapshot being created
        Currently, support two types of snapshot: ['volume', 'image']
        :param info:
        :return
        """
        # List containing volume(s)
        volume_id = info.get('volume_id')
        server_id = info.get('server_id')
        volumes = []
        if volume_id:  # only one volume
            data = self.client.shade.get_volume(server_id=server_id,
                                                volume_id=volume_id)
            err, vol = data.parse()
            if err:
                return err, None
            if vol:
                volumes.append(vol)
        else:  # all volumes of server
            data = self.client.shade.get_volumes(server_id=server_id)
            err, vols = data.parse()
            if err:
                return err, None
            volumes = vols
        result = []
        for vol in volumes:
            data = self.client.shade.get_volume_snapshots(search_opts={'volume_id': vol['id']})
            error, snaps = data.parse()
            if err:
                return self.fail(err)
            else:
                result.append({
                    'volume_id': vol['id'],
                    'volume_name': vol.get('name'),
                    'snapshots': snaps,
                })
        return self.parse(result, **listing)

    def create_volume_snapshot(self, volume_id, force=False,
                               wait=True, timeout=None, **kwargs):
        """
        Create a volume snapshot.

        :param volume_id: the ID of the volume to snapshot.
        :param force: If set to True the snapshot will be created even if the
                      volume is attached to an server, if False it will not
                      Without the force flag, the volume will be took snapshot
                      only if its status is available.
                      The snapshot of an in-use volume means your data is crash consistent.
                      With the force flag, the volume will be backed up whether
                      its status is available or in-use.
        :param wait: If true, waits for volume snapshot to be created.
        :param timeout: Seconds to wait for volume snapshot creation. None is
                        forever.

        :returns: The created volume object.
        """
        try:
            s = self.client.create_volume_snapshot(volume_id=volume_id,
                                                   force=force, wait=wait,
                                                   timeout=timeout, **kwargs)
            return self.parse(s)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_volume_snapshot(%s)]: %s.", volume_id, e)
            return self.fail(e)

    def create_snapshot(self, info):
        """
        Create a snapshot being created
        Currently, support two types of snapshot: ['volume', 'image']
        :param info:
        :return
        """
        # List containing volume(s)
        volume_id = info.get('volume_id')
        server_id = info.get('server_id')
        volumes = []
        if volume_id:  # only one volume
            data = self.client.shade.get_volume(server_id=server_id,
                                                volume_id=volume_id)
            err, vol = data.parse()
            if err:
                return self.fail(err)
            if vol:
                volumes.append(vol)
        else:  # all volumes of server
            data = self.client.shade.get_volumes(server_id=server_id)
            err, vols = data.parse()
            if err:
                return self.fail(err)
            volumes = vols

        result = []
        index = 0
        for vol in volumes:
            name = '{}-{}'.format(info['name'], str(index))
            index += 1
            data = self.client.shade.create_volume_snapshot(volume_id=vol['id'],
                                                            force=info['force'],
                                                            description=info.get('description'),
                                                            name=name)
            err, snaps = data.parse()
            if err:
                return self.fail(err)
            else:
                result.append({
                    'volume_id': vol['id'],
                    'volume_name': vol.get('name'),
                    'snapshots': snaps,
                })
        return self.parse(data)

    @valid_kwargs('name', 'description')
    def update_volume_snapshot(self, snapshot_id, **kwargs):
        """
        Update the name or description for a snapshot.

        :param snapshot_id:
        :param kwargs
        """
        try:
            s = self.cinder_client.volume_snapshots.update(snapshot=snapshot_id,
                                                           **kwargs)
            return self.parse(s)
        except Exception as e:
            LOG.error("Error [update_volume_snapshot(%s)]: %s.", snapshot_id, e)
            return self.fail(e)

    def update_snapshot(self, info):
        """
        Update a snapshot.
        Currently, support two types of backup: ['volume', 'image']

        :param info:
        :return
        """
        kw = data_util.no_null_kv_dict({
            'name': info.get('name'),
            'description': info.get('description'),
        })
        return self.client.shade.update_volume_snapshot(snapshot_id=info['snapshot_id'], **kw)

    def delete_volume_snapshot(self, snapshot_id=None, force=False):
        """
        Delete a volume snapshot.

        :param snapshot_id: Unique ID of the volume snapshot.
        :param force:
        """
        try:
            s = self.client.shade.delete_volume_snapshot(snapshot_id=snapshot_id, force=force)
            return self.parse(s)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_volume_snapshot(%s)]: %s.", snapshot_id, e)
            return self.fail(e)

    def delete_snapshot(self, info):
        """
        Delete a snapshot being created
        Currently, support two types of snapshot: ['volume', 'image']

        :param info:
        :return
        """
        return self.delete_volume_snapshot(snapshot_id=info['snapshot_id'], force=info['force'])

    def rollback_volume_snapshot(self, volume_id, snapshot_id):
        """
        Revert a volume to a snapshot.

        :param volume_id: Unique ID of the volume volume.
        :param snapshot_id: Unique ID of the volume snapshot.
        :return
        """
        from foxcloud import client as fox_client
        from foxcloud import exceptions as fox_exc

        try:
            ceph_config = app.config['CEPH']
            params = {
                'ceph_config': ceph_config['config_file'],
                'ceph_pool': ceph_config['pool'],
                'ceph_keyring': ceph_config['keyring']
            }
            f_client = fox_client.Client(services='ceph', **params)
            s = f_client.ceph.rollback_snapshot(volume_id=volume_id, snapshot_id=snapshot_id)
            return self.parse(s)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [rollback_volume_snapshot(%s, %s)]: %s.", volume_id, snapshot_id, e)
            return self.fail(e)

    def rollback_snapshot(self, info):
        """
        Revert a snapshot being created.
        Currently, support two types of snapshot: ['volume', 'image']

        :param info:
        :return
        """
        type_ = info['type']
        if type_ == 'volume':
            err, s = self.rollback_volume_snapshot(volume_id=info['volume_id'],
                                                   snapshot_id=info['snapshot_id'])
            if err:
                return self.fail(err)

            return self.get_server_status(server_id=info['server_id'])

        return self.fail("Snapshot type %s unsupported" % type_)

    # *************************************
    # BACKUP
    # *************************************

    def get_backup(self, backup_id, listing={}):
        """
        Get a volume by name or ID.

        :param backup_id: ID of the volume backup.
        :param filters:
        :returns: A volume ``munch.Munch`` or None if no matching volume is found.
        """
        try:
            data = self.client.shade.get_volume_backup(backup_id=backup_id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_volume_backup(%s)]: %s.", backup_id, e)
            return self.fail(e)

    def get_backups(self, info, listing={}, **kw):
        """
        List all backups.
        Currently, support two types of backup: ['volume', 'image']

        :param info:
        :return
        """
        volume_id = info.get('volume_id')
        server_id = info.get('server_id')
        volumes = []
        if volume_id:  # only one volume
            data = self.client.shade.get_volume(server_id=server_id,
                                                volume_id=volume_id)
            err, vol = data.parse()
            if err:
                return self.fail(err)
            if vol:
                volumes.append(vol)
        else:  # all volumes of server
            data = self.client.shade.get_volumes(server_id=server_id)
            err, vols = data.parse()
            if err:
                return self.fail(err)
            volumes = vols

        result = []
        for vol in volumes:
            data = self.client.shade.get_volume_backups(search_opts={'volume_id': vol['id']})
            err, backups = data.parse()
            if err:
                return self.fail(err)
            else:
                result.append({
                    'volume_id': vol['id'],
                    'volume_name': vol.get('name'),
                    'backups': backups,
                })
        return self.parse(result, **listing)

    def create_volume_backup(self, volume_id, name=None, description=None,
                             force=True):
        try:
            b = self.client.create_volume_backup(volume_id=volume_id, name=name,
                                                 description=description, force=force)
            return self.parse(b)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_volume_backup(%s, %s)]: %s.", volume_id, name, e)
            return self.fail(e)

    def create_backup(self, info):
        """
        Create a backup.
        Currently, support two types of backup: ['volume', 'image']

        :param info:
        :return
        """
        # List containing volume(s)
        volume_id = info.get('volume_id')
        server_id = info.get('server_id')
        volumes = []
        if volume_id:  # only one volume
            data = self.client.shade.get_volume(server_id=server_id,
                                                volume_id=volume_id)
            err, vol = data.parse()
            if err:
                return self.fail(err)
            if vol:
                volumes.append(vol)
        else:  # all volumes of server
            data = self.client.shade.get_volumes(server_id=server_id)
            err, vols = data.parse()
            if err:
                return self.fail(err)
            volumes = vols

        index = 0
        backups = []
        for vol in volumes:
            name = '{}-{}'.format(info['name'], str(index))
            index += 1
            data = self.client.shade.create_volume_backup(volume_id=vol['id'],
                                                          name=name,
                                                          description=info.get('description'),
                                                          force=info.get('force', True))
            err, bka = data.parse()
            if err:
                return self.fail(err)
            else:
                backups.append({
                    'volume_id': vol['id'],
                    'volume_name': vol.get('name'),
                    'backup': bka,
                })
        return self.parse(backups)

    def delete_backup(self, backup_id=None, force=False):
        """
        Delete a volume backup.

        :param backup_id: Unique ID of the volume backup.
        :param force:
        """
        try:
            data = self.client.shade.delete_volume_backup(name_or_id=backup_id, force=force)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_volume_backup(%s)]: %s.", backup_id, e)
            return self.fail(e)

    def reset_volume_state(self, volume_id, state):
        try:
            data = self.client.client.reset_volume_state(volume_id=volume_id, state=state)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [reset_volume_state(%s)]: %s.", volume_id, e)
            return self.fail(e)

    def restore_backup(self, backup_id, volume_id=None, name=None):
        """
        Restore a backup to a volume.

        :param backup_id: The ID of the backup to restore.
        :param volume_id: The ID of the volume to restore the backup to.
        :param name: The name for new volume creation to restore.
        :return:
        """
        try:
            data = self.client.shade.restore_volume_backup(backup_id=backup_id,
                                                           volume_id=volume_id,
                                                           name=name)
            return data.parse()
        except Exception as e:
            LOG.error("Error [restore_volume_backup(%s)]: %s.", backup_id, e)
            return self.fail(e)
