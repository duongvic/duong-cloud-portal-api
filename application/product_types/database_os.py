#
# Copyright (c) 2020 FTI-CAS
#

import functools
import ipaddress

from application import app
from application.base import errors
from application import models as md
from application.product_types import base, os_base
from application.product_types.openstack import os_database_api as db_api
from application.managers import user_mgr
from application.utils import date_util

LOG = app.logger

ADMIN_ROLES = (md.UserRole.ADMIN, md.UserRole.ADMIN_SALE, md.UserRole.ADMIN_IT)
GET_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
LIST_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
CREATE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)
UPDATE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)
DELETE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)


class OSDatabase(os_base.OSBase):
    """
    Openstack trove
    """

    def __init__(self):
        """
        Initialize keypair
        """
        super().__init__()

    @property
    def supported(self):
        return True

    def get_os_client(self, ctx, cluster=None, engine='console', services='trove'):
        """
        Get openstack client
        :param ctx:
        :param cluster:
        :param engine:
        :param services:
        :return
        """
        cluster = cluster or self.parse_ctx_cluster(ctx)
        if ctx.failed:
            return
        os_config = self.get_os_config(ctx, cluster=cluster)
        if ctx.failed:
            return
        return db_api.get_database_client(cluster=cluster, os_config=os_config,
                                          engine=engine, services=services)

    def get_datastore(self, ctx):
        """
        Get a datastore being created.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_datastore(ctx)

    def do_get_datastore(self, ctx):
        """
        Subclass should override this method.
        :param ctx:
        :return:
        """
        data = ctx.data
        listing = self.parse_ctx_listing(ctx)

        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        error, datastore = os_client.get_datastore(datastore_id=data['datastore_id'],
                                                   listing=listing)
        if error:
            ctx.set_error(errors.DATASTORE_GET_FAILED, cause=error, status=404)
            return

        ctx.response = datastore
        return datastore

    def get_datastores(self, ctx):
        """
        Get all datastores created by user.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=LIST_ROLES):
            return

        return self.do_get_datastores(ctx)

    def do_get_datastores(self, ctx):
        """
        Subclass should override this method.
        :param ctx:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        data = ctx.data
        listing = self.parse_ctx_listing(ctx)
        filters = data.get('filters') or {}

        error, datastores = os_client.get_datastores(listing=listing, **filters)
        if error:
            ctx.set_error(errors.DATASTORE_GET_FAILED, cause=error, status=404)
            return
        ctx.response = datastores
        return datastores['data']

    def get_datastore_version(self, ctx):
        """
        Get a datastore_version being created.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_datastore_version(ctx)

    def do_get_datastore_version(self, ctx):
        """
        Subclass should override this method.
        :param ctx:
        :return:
        """
        data = ctx.data
        listing = self.parse_ctx_listing(ctx)

        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        error, datastore_version = os_client.get_datastore_version(version_id=data['version_id'],
                                                                   datastore_id=data['datastore_id'],
                                                                   listing=listing)
        if error:
            ctx.set_error(errors.DATASTORE_VERSION_GET_FAILED, cause=error, status=404)
            return

        ctx.response = datastore_version
        return datastore_version

    def get_datastore_versions(self, ctx):
        """
        Get all datastore_versions created by user.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=LIST_ROLES):
            return

        return self.do_get_datastore_versions(ctx)

    def do_get_datastore_versions(self, ctx):
        """
        Subclass should override this method.
        :param ctx:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        data = ctx.data
        listing = self.parse_ctx_listing(ctx)
        filters = data.get('filters') or {}

        error, datastore_versions = os_client.get_datastore_versions(datastore_id=data['datastore_id'],
                                                                     listing=listing, **filters)
        if error:
            ctx.set_error(errors.DATASTORE_VERSION_GET_FAILED, cause=error, status=404)
            return
        ctx.response = datastore_versions
        return datastore_versions['data']

    def get_db_cluster(self, ctx):
        """
        Get a db_cluster being created.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_db_cluster(ctx)

    def do_get_db_cluster(self, ctx):
        """
        Subclass should override this method.
        :param ctx:
        :return:
        """
        data = ctx.data
        listing = self.parse_ctx_listing(ctx)

        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        error, db_cluster = os_client.get_cluster(id=data['db_cluster_id'], listing=listing)
        if error:
            ctx.set_error(errors.DB_CLUSTER_GET_FAILED, cause=error, status=404)
            return

        ctx.response = db_cluster
        return db_cluster

    def get_db_clusters(self, ctx):
        """
        Get all db_clusters created by user.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=LIST_ROLES):
            return

        return self.do_get_db_clusters(ctx)

    def do_get_db_clusters(self, ctx):
        """
        Subclass should override this method.
        :param ctx:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        data = ctx.data
        listing = self.parse_ctx_listing(ctx)
        filters = data.get('filters') or {}

        error, db_clusters = os_client.get_clusters(listing=listing, **filters)
        if error:
            ctx.set_error(errors.DB_CLUSTER_GET_FAILED, cause=error, status=404)
            return
        ctx.response = db_clusters
        return db_clusters['data']

    def create_db_cluster(self, ctx):
        """
        Do create new db_cluster.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        self.validate_create_db_cluster(ctx)
        if ctx.failed:
            return

        data = ctx.data
        db_cluster = {
            'name': data['name'],
            'datastore_id': data['datastore_id'],
            'datastore_version_id': data['datastore_version_id'],
            'flavor_id': data['flavor_id'],
            'volume_size': data['volume_size'],
            'volume_type': data.get('volume_type'),
            'number_of_instances': data['number_of_instances'],
            'network_id': data['network_id'],
            'locality': data.get('locality'),
            'extended_properties': data.get('extra_properties'),
            'configuration': data.get('configuration'),
            'wait': data.get('wait') or False,
        }
        return self.do_create_db_cluster(ctx, db_cluster=db_cluster)

    def validate_create_db_cluster(self, ctx):
        """
        Validate db_cluster
        :param ctx:
        :return:
        """

    def do_create_db_cluster(self, ctx, db_cluster, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param db_cluster:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, db_obj=db_cluster,
                                         func=functools.partial(os_client.create_cluster, **db_cluster),
                                         method=method,
                                         on_result=on_result or self.on_create_db_cluster_result)

    def _execute_client_func(self, ctx, db_obj, func, method, on_result):
        """
        Execute client func.
        :param ctx:
        :param db_obj:
        :param func:
        :param method:
        :param on_result:
        :return:
        """

        def _on_result(ctx, result):
            on_result(ctx=ctx, db_obj=db_obj, result=result)
            # Finish history log for the action (if there is)
            self.finish_action_log(ctx, error=result[0])

        self.execute_client_func(ctx, func=func, method=method, on_result=_on_result)

    def on_create_db_cluster_result(self, ctx, db_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param db_cluster_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to create db_cluster: {}. Error {}.'.format(db_obj, error))
            ctx.set_error(errors.DB_CLUSTER_CREATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def update_db_cluster(self, ctx):
        """
        Do update a db_cluster.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
            return

        data = ctx.data
        db_cluster = {
            'id': data['db_cluster_id'],
            'name': data.get('name'),
            'description': data.get('description'),
        }
        tags = data.get('tags')
        if tags:
            db_cluster['tags'] = tags

        return self.do_update_db_cluster(ctx, db_cluster=db_cluster)

    def do_update_db_cluster(self, ctx, db_cluster, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param db_cluster:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, db_obj=db_cluster,
                                         func=functools.partial(os_client.update_db_cluster, **db_cluster),
                                         method=method,
                                         on_result=on_result or self.on_update_db_cluster_result)

    def on_update_db_cluster_result(self, ctx, db_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param db_cluster_obj:
        :param result
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to create db_cluster: {}. Error {}.'.format(db_obj, error))
            ctx.set_error(errors.DB_CLUSTER_UPDATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def delete_db_cluster(self, ctx):
        """
        Do delete a db_cluster.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
            return

        data = ctx.data
        db_cluster = {
            'id': data['db_cluster_id'],
        }
        return self.do_delete_db_cluster(ctx, db_cluster=db_cluster)

    def do_delete_db_cluster(self, ctx, db_cluster, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param db_cluster:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, db_obj=db_cluster,
                                         func=functools.partial(os_client.delete_db_cluster, **db_cluster),
                                         method=method,
                                         on_result=on_result or self.on_delete_db_cluster_result)

    def on_delete_db_cluster_result(self, ctx, db_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param db_cluster_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to delete db_cluster: {}. Error {}.'.format(db_obj, error))
            ctx.set_error(errors.DB_CLUSTER_DELETE_FAILED, cause=error, status=db_obj)

        ctx.response = data
        return data

    def get_db_instance(self, ctx):
        """
        Get a db_instance being created.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_db_instance(ctx)

    def do_get_db_instance(self, ctx):
        """
        Subclass should override this method.
        :param ctx:
        :return:
        """
        data = ctx.data
        listing = self.parse_ctx_listing(ctx)

        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        error, db_instance = os_client.get_instance(id=data['db_instance_id'], listing=listing)
        if error:
            ctx.set_error(errors.DB_INSTANCE_GET_FAILED, cause=error, status=404)
            return

        ctx.response = db_instance
        return db_instance

    def get_db_instances(self, ctx):
        """
        Get all db_instances created by user.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=LIST_ROLES):
            return

        return self.do_get_db_instances(ctx)

    def do_get_db_instances(self, ctx):
        """
        Subclass should override this method.
        :param ctx:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        data = ctx.data
        listing = self.parse_ctx_listing(ctx)
        filters = data.get('filters') or {}

        error, db_instances = os_client.get_instances(listing=listing, **filters)
        if error:
            ctx.set_error(errors.DB_INSTANCE_GET_FAILED, cause=error, status=404)
            return
        ctx.response = db_instances
        return db_instances['data']

    def create_db_instance(self, ctx):
        """
        Do create new db_instance.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        self.validate_create_db_instance(ctx)
        if ctx.failed:
            return

        data = ctx.data
        db_instance = {
            'name': data['name'],
            'flavor_id': data['flavor_id'],
            'datastore_id': data['datastore_id'],
            'datastore_version_id': data['datastore_version_id'],
            'locality': data.get('locality'),
            'configuration': data.get('configuration'),
            'wait': data.get('wait') or False,
        }
        databases = data.get('databases')
        if databases:
            db_instance['databases'] = databases
            users = []
            username = data.get('db_username')
            if username:
                users.append({
                    'name': username,
                    'password': data.get('db_password'),
                    'databases': [dict(name=db.get('name')) for db in databases],
                })
                db_instance['users'] = users

        volume = {
            'size': data['volume_size'],
        }
        volume_type = data.get('volume_type')
        if volume_type:
            volume['type'] = volume_type
        db_instance['volume'] = volume

        nics = [
            {
                'net-id': data['network_id']
            }
        ]
        db_instance['nics'] = nics

        replica_of = data.get('replica_of')
        if replica_of:
            db_instance['replica_of'] = replica_of
            db_instance['replica_count'] = data.get('replica_count') or 1

        is_public = data.get('is_public')
        if is_public:
            db_instance['access'] = {
                'is_public': is_public,
                'allowed_cidrs': data.get('allowed_cidrs') or []
            }

        return self.do_create_db_instance(ctx, db_instance=db_instance)

    def validate_create_db_instance(self, ctx):
        """
        Validate db_instance
        :param ctx:
        :return:
        """

    def do_create_db_instance(self, ctx, db_instance, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param db_instance:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, db_obj=db_instance,
                                         func=functools.partial(os_client.create_instance, **db_instance),
                                         method=method,
                                         on_result=on_result or self.on_create_db_instance_result)

    def on_create_db_instance_result(self, ctx, db_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param db_instance_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to create db_instance: {}. Error {}.'.format(db_obj, error))
            ctx.set_error(errors.DB_INSTANCE_CREATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def update_db_instance(self, ctx):
        """
        Do update a db_instance.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
            return

        data = ctx.data
        db_instance = {
            'id': data['db_instance_id'],
            'name': data.get('name'),
            'configuration': data.get('configuration'),
            'volume_size': data.get('volume_size'),
        }

        return self.do_update_db_instance(ctx, db_instance=db_instance)

    def do_update_db_instance(self, ctx, db_instance, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param db_instance:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, db_obj=db_instance,
                                         func=functools.partial(os_client.update_instance, **db_instance),
                                         method=method,
                                         on_result=on_result or self.on_update_db_instance_result)

    def on_update_db_instance_result(self, ctx, db_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param db_instance_obj:
        :param result
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to create db_instance: {}. Error {}.'.format(db_obj, error))
            ctx.set_error(errors.DB_CLUSTER_UPDATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def delete_db_instance(self, ctx):
        """
        Do delete a db_instance.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
            return

        data = ctx.data
        db_instance = {
            'id': data['db_instance_id'],
        }
        return self.do_delete_db_instance(ctx, db_instance=db_instance)

    def do_delete_db_instance(self, ctx, db_instance, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param db_instance:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, db_obj=db_instance,
                                         func=functools.partial(os_client.delete_instance, **db_instance),
                                         method=method,
                                         on_result=on_result or self.on_delete_db_instance_result)

    def on_delete_db_instance_result(self, ctx, db_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param db_instance_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to delete db_instance: {}. Error {}.'.format(db_obj, error))
            ctx.set_error(errors.DB_INSTANCE_DELETE_FAILED, cause=error, status=500)

        ctx.response = data
        return data

    def get_db_backup(self, ctx):
        """
        Get a db_backup being created.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_db_backup(ctx)

    def do_get_db_backup(self, ctx):
        """
        Subclass should override this method.
        :param ctx:
        :return:
        """
        data = ctx.data
        listing = self.parse_ctx_listing(ctx)

        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        error, db_backup = os_client.get_backup(id=data['db_backup_id'], listing=listing)
        if error:
            ctx.set_error(errors.DB_BACKUP_GET_FAILED, cause=error, status=404)
            return

        ctx.response = db_backup
        return db_backup

    def get_db_backups(self, ctx):
        """
        Get all db_backups created by user.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=LIST_ROLES):
            return

        return self.do_get_db_backups(ctx)

    def do_get_db_backups(self, ctx):
        """
        Subclass should override this method.
        :param ctx:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        data = ctx.data
        db_instance_id = data['db_instance_id']
        datastore_id = data.get('datastore_id')
        listing = self.parse_ctx_listing(ctx)
        filters = data.get('filters') or {}

        error, db_backups = os_client.get_backups(instance_id=db_instance_id,
                                                  datastore_id=datastore_id,
                                                  listing=listing, **filters)
        if error:
            ctx.set_error(errors.DB_BACKUP_GET_FAILED, cause=error, status=404)
            return
        ctx.response = db_backups
        return db_backups['data']

    def create_db_backup(self, ctx):
        """
        Do create new db_backup.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        self.validate_create_db_backup(ctx)
        if ctx.failed:
            return

        data = ctx.data
        db_backup = {
            'name': data['name'],
            'instance_id': data['db_instance_id'],
            'description': data.get('description'),
        }
        return self.do_create_db_backup(ctx, db_backup=db_backup)

    def validate_create_db_backup(self, ctx):
        """
        Validate db_backup
        :param ctx:
        :return:
        """

    def do_create_db_backup(self, ctx, db_backup, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param db_backup:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, db_obj=db_backup,
                                         func=functools.partial(os_client.create_backup, **db_backup),
                                         method=method,
                                         on_result=on_result or self.on_create_db_backup_result)

    def on_create_db_backup_result(self, ctx, db_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param db_backup_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to create db_backup: {}. Error {}.'.format(db_obj, error))
            ctx.set_error(errors.DB_BACKUP_CREATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def update_db_backup(self, ctx):
        """
        Do update a db_backup.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
            return

        data = ctx.data
        db_backup = {
            'id': data['db_backup_id'],
            'name': data.get('name'),
            'configuration': data.get('configuration'),
            'volume_size': data.get('volume_size'),
        }

        return self.do_update_db_backup(ctx, db_backup=db_backup)

    def do_update_db_backup(self, ctx, db_backup, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param db_backup:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, db_obj=db_backup,
                                         func=functools.partial(os_client.update_backup, **db_backup),
                                         method=method,
                                         on_result=on_result or self.on_update_db_backup_result)

    def on_update_db_backup_result(self, ctx, db_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param db_backup_obj:
        :param result
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to create db_backup: {}. Error {}.'.format(db_obj, error))
            ctx.set_error(errors.DB_BACKUP_UPDATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def delete_db_backup(self, ctx):
        """
        Do delete a db_backup.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
            return

        data = ctx.data
        db_backup = {
            'id': data['db_backup_id'],
        }
        return self.do_delete_db_backup(ctx, db_backup=db_backup)

    def do_delete_db_backup(self, ctx, db_backup, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param db_backup:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, db_obj=db_backup,
                                         func=functools.partial(os_client.delete_backup, **db_backup),
                                         method=method,
                                         on_result=on_result or self.on_delete_db_backup_result)

    def on_delete_db_backup_result(self, ctx, db_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param db_backup_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to delete db_backup: {}. Error {}.'.format(db_obj, error))
            ctx.set_error(errors.DB_BACKUP_DELETE_FAILED, cause=error, status=500)

        ctx.response = data
        return data

