#
# Copyright (c) 2020 FTI-CAS
#

from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args

from application import app
from application.api.v1 import base
from application.base import context, common
from application import product_types
from application import models as md
from application.utils import data_util

LOCATION = 'default'
auth = base.auth


db_os = product_types.get_product_type(
    context.create_admin_context(task='get os database type'),
    product_type=md.ProductType.DATABASE)


#####################################################################
# datastore
#####################################################################
def do_get_datastore(args):
    """
    Get a datastore
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get datastore',
        data=args)
    return base.exec_manager_func(db_os.get_datastore, ctx)


def do_get_datastores(args):
    """
    Get all datastores of user
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get datastores',
        data=args)
    return base.exec_manager_func(db_os.get_datastores, ctx)


def do_create_datastore(args):
    """
    Create a new datastore
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create datastore',
        data=args)
    return base.exec_manager_func_with_log(db_os.create_datastore, ctx,
                                           action=md.HistoryAction.CREATE_DB_DATASTORE)


def do_update_datastore(args):
    """
    Update a datastore
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update datastore',
        data=args)
    return base.exec_manager_func_with_log(db_os.update_datastore, ctx,
                                           action=md.HistoryAction.UPDATE_DB_DATASTORE)


def do_delete_datastore(args):
    """
    Delete a datastore
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create datastore',
        data=args)
    return base.exec_manager_func_with_log(db_os.delete_datastore, ctx,
                                           action=md.HistoryAction.DELETE_DB_DATASTORE)


class Datastores(Resource):
    get_datastores_args = {
        **base.LIST_OBJECTS_ARGS
    }

    create_datastore_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_datastores_args, location=LOCATION)
    def get(self, args):
        return do_get_datastores(args=args)

    @auth.login_required
    @use_args(create_datastore_args, location=LOCATION)
    def post(self, args):
        return do_create_datastore(args=args)


class Datastore(Resource):
    get_datastore_args = {
        **base.LIST_OBJECTS_ARGS
    }

    update_datastore_args = {
        **base.REGION_ARGS,
        'patch': fields.List(fields.Dict(), required=False),
    }

    delete_datastore_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_datastore_args, location=LOCATION)
    def get(self, args, datastore_id):
        args['datastore_id'] = datastore_id
        return do_get_datastore(args=args)

    @auth.login_required
    @use_args(update_datastore_args, location=LOCATION)
    def put(self, args, datastore_id):
        args['datastore_id'] = datastore_id
        return do_update_datastore(args=args)

    @auth.login_required
    @use_args(delete_datastore_args, location=LOCATION)
    def delete(self, args, datastore_id):
        args['datastore_id'] = datastore_id
        return do_delete_datastore(args=args)


#####################################################################
# datastore_version
#####################################################################
def do_get_datastore_version(args):
    """
    Get a datastore_version
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get datastore_version',
        data=args)
    return base.exec_manager_func(db_os.get_datastore_version, ctx)


def do_get_datastore_versions(args):
    """
    Get all datastore_versions of user
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get datastore_versions',
        data=args)
    return base.exec_manager_func(db_os.get_datastore_versions, ctx)


def do_create_datastore_version(args):
    """
    Create a new datastore_version
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create datastore_version',
        data=args)
    return base.exec_manager_func_with_log(db_os.create_datastore_version, ctx,
                                           action=md.HistoryAction.CREATE_DB_DATASTORE_VERSION)


def do_update_datastore_version(args):
    """
    Update a datastore_version
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update datastore_version',
        data=args)
    return base.exec_manager_func_with_log(db_os.update_datastore_version, ctx,
                                           action=md.HistoryAction.UPDATE_DB_DATASTORE_VERSION)


def do_delete_datastore_version(args):
    """
    Delete a datastore_version
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create datastore_version',
        data=args)
    return base.exec_manager_func_with_log(db_os.delete_datastore_version, ctx,
                                           action=md.HistoryAction.DELETE_DB_DATASTORE_VERSION)


class DatastoreVersions(Resource):
    get_datastore_versions_args = {
        **base.LIST_OBJECTS_ARGS
    }

    create_datastore_version_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_datastore_versions_args, location=LOCATION)
    def get(self, args, datastore_id):
        args['datastore_id'] = datastore_id
        return do_get_datastore_versions(args=args)

    @auth.login_required
    @use_args(create_datastore_version_args, location=LOCATION)
    def post(self, args, datastore_id):
        args['datastore_id'] = datastore_id
        return do_create_datastore_version(args=args)


class DatastoreVersion(Resource):
    get_datastore_version_args = {
        **base.LIST_OBJECTS_ARGS
    }

    update_datastore_version_args = {
        **base.REGION_ARGS,
        'patch': fields.List(fields.Dict(), required=False),
    }

    delete_datastore_version_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_datastore_version_args, location=LOCATION)
    def get(self, args, version_id, datastore_id):
        args['datastore_id'] = datastore_id
        args['version_id'] = version_id
        return do_get_datastore_version(args=args)

    @auth.login_required
    @use_args(update_datastore_version_args, location=LOCATION)
    def put(self, args, version_id, datastore_id):
        args['datastore_id'] = datastore_id
        args['version_id'] = version_id
        return do_update_datastore_version(args=args)

    @auth.login_required
    @use_args(delete_datastore_version_args, location=LOCATION)
    def delete(self, args, version_id, datastore_id):
        args['datastore_id'] = datastore_id
        args['version_id'] = version_id
        return do_delete_datastore_version(args=args)


#####################################################################
# db_cluster
#####################################################################
def do_get_db_cluster(args):
    """
    Get a db_cluster
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get db_cluster',
        data=args)
    return base.exec_manager_func(db_os.get_db_cluster, ctx)


def do_get_db_clusters(args):
    """
    Get all db_clusters of user
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get db_clusters',
        data=args)
    return base.exec_manager_func(db_os.get_db_clusters, ctx)


def do_create_db_cluster(args):
    """
    Create a new db_cluster
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create db_cluster',
        data=args)
    return base.exec_manager_func_with_log(db_os.create_db_cluster, ctx,
                                           action=md.HistoryAction.CREATE_DB_CLUSTER)


def do_update_db_cluster(args):
    """
    Update a db_cluster
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update db_cluster',
        data=args)
    return base.exec_manager_func_with_log(db_os.update_db_cluster, ctx,
                                           action=md.HistoryAction.UPDATE_DB_CLUSTER)


def do_delete_db_cluster(args):
    """
    Delete a db_cluster
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create db_cluster',
        data=args)
    return base.exec_manager_func_with_log(db_os.delete_db_cluster, ctx,
                                           action=md.HistoryAction.DELETE_DB_CLUSTER)


class DBClusters(Resource):
    get_db_clusters_args = {
        **base.LIST_OBJECTS_ARGS
    }

    create_db_cluster_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=True, validate=data_util.validate_name),
        'datastore_id': fields.Str(required=True),
        'datastore_version_id': fields.Str(required=True),
        'flavor_id': fields.Str(required=True),
        'volume_size': fields.Int(required=False, missing=25, validate=validate.Range(min=10)),
        'volume_type': fields.Str(required=False, validate=data_util.validate_name),
        'number_of_instances': fields.Int(required=False, missing=1, validate=validate.Range(min=3)),
        'network_id': fields.Str(required=True),
        'locality': fields.Str(required=False,
                               validate=validate.OneOf(['affinity', 'anti-affinity'])),
        'extra_properties': fields.List(fields.Dict(), required=False),
        'configuration': fields.List(fields.Dict(), required=False),
        'wait': fields.Bool(required=False, missing=False),
    }

    @auth.login_required
    @use_args(get_db_clusters_args, location=LOCATION)
    def get(self, args):
        return do_get_db_clusters(args=args)

    @auth.login_required
    @use_args(create_db_cluster_args, location=LOCATION)
    def post(self, args):
        return do_create_db_cluster(args=args)


class DBCluster(Resource):
    get_db_cluster_args = {
        **base.LIST_OBJECTS_ARGS
    }

    update_db_cluster_args = {
        **base.REGION_ARGS,
    }

    delete_db_cluster_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_db_cluster_args, location=LOCATION)
    def get(self, args, db_cluster_id):
        args['db_cluster_id'] = db_cluster_id
        return do_get_db_cluster(args=args)

    @auth.login_required
    @use_args(update_db_cluster_args, location=LOCATION)
    def put(self, args, db_cluster_id):
        args['db_cluster_id'] = db_cluster_id
        return do_update_db_cluster(args=args)

    @auth.login_required
    @use_args(delete_db_cluster_args, location=LOCATION)
    def delete(self, args, db_cluster_id):
        args['db_cluster_id'] = db_cluster_id
        return do_delete_db_cluster(args=args)


#####################################################################
# db instance
#####################################################################
def do_get_db_instance(args):
    """
    Get a db_instance
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get db_instance',
        data=args)
    return base.exec_manager_func(db_os.get_db_instance, ctx)


def do_get_db_instances(args):
    """
    Get all db_instances of user
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get db_instances',
        data=args)
    return base.exec_manager_func(db_os.get_db_instances, ctx)


def do_create_db_instance(args):
    """
    Create a new db_instance
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create db_instance',
        data=args)
    return base.exec_manager_func_with_log(db_os.create_db_instance, ctx,
                                           action=md.HistoryAction.CREATE_DB_INSTANCE)


def do_update_db_instance(args):
    """
    Update a db_instance
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update db_instance',
        data=args)
    return base.exec_manager_func_with_log(db_os.update_db_instance, ctx,
                                           action=md.HistoryAction.UPDATE_DB_INSTANCE)


def do_delete_db_instance(args):
    """
    Delete a db_instance
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create db_instance',
        data=args)
    return base.exec_manager_func_with_log(db_os.delete_db_instance, ctx,
                                           action=md.HistoryAction.DELETE_DB_INSTANCE)


class DBInstances(Resource):
    get_db_instances_args = {
        **base.LIST_OBJECTS_ARGS
    }

    create_db_instance_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=True, validate=data_util.validate_name),
        'flavor_id': fields.Str(required=True),
        'volume_size': fields.Int(required=False, missing=25, validate=validate.Range(min=10)),
        'volume_type': fields.Str(required=False, validate=data_util.validate_name),
        'databases': fields.List(fields.Dict(), required=False),
        'db_username': fields.Str(required=False, validate=data_util.validate_name),
        'db_password': fields.Str(required=False),
        'datastore_id': fields.Str(required=True),
        'datastore_version_id': fields.Str(required=True),
        'network_id': fields.Str(required=True),
        'replica_of': fields.Str(required=False),
        'replica_count': fields.Int(required=False),
        'locality': fields.Str(required=False,
                               validate=validate.OneOf(['affinity', 'anti-affinity'])),
        'is_public': fields.Bool(required=False, missing=False),
        'allowed_cidrs': fields.List(fields.Str(), required=False),
        'configuration': fields.List(fields.Dict(), required=False),
        'wait': fields.Bool(required=False, missing=False),
    }

    @auth.login_required
    @use_args(get_db_instances_args, location=LOCATION)
    def get(self, args):
        return do_get_db_instances(args=args)

    @auth.login_required
    @use_args(create_db_instance_args, location=LOCATION)
    def post(self, args):
        return do_create_db_instance(args=args)


class DBInstance(Resource):
    get_db_instance_args = {
        **base.LIST_OBJECTS_ARGS
    }

    update_db_instance_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=False, validate=data_util.validate_name),
        'configuration': fields.List(fields.Dict(), required=False),
        'volume_size': fields.Int(required=False),
    }

    delete_db_instance_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_db_instance_args, location=LOCATION)
    def get(self, args, db_instance_id):
        args['db_instance_id'] = db_instance_id
        return do_get_db_instance(args=args)

    @auth.login_required
    @use_args(update_db_instance_args, location=LOCATION)
    def put(self, args, db_instance_id):
        args['db_instance_id'] = db_instance_id
        return do_update_db_instance(args=args)

    @auth.login_required
    @use_args(delete_db_instance_args, location=LOCATION)
    def delete(self, args, db_instance_id):
        args['db_instance_id'] = db_instance_id
        return do_delete_db_instance(args=args)


#####################################################################
# db_backup
#####################################################################
def do_get_db_backup(args):
    """
    Get a db_backup
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get db_backup',
        data=args)
    return base.exec_manager_func(db_os.get_db_backup, ctx)


def do_get_db_backups(args):
    """
    Get all db_backups of user
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get db_backups',
        data=args)
    return base.exec_manager_func(db_os.get_db_backups, ctx)


def do_create_db_backup(args):
    """
    Create a new db_backup
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create db_backup',
        data=args)
    return base.exec_manager_func_with_log(db_os.create_db_backup, ctx,
                                           action=md.HistoryAction.CREATE_DB_BACKUP)


def do_update_db_backup(args):
    """
    Update a db_backup
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update db_backup',
        data=args)
    return base.exec_manager_func_with_log(db_os.update_db_backup, ctx,
                                           action=md.HistoryAction.UPDATE_DB_BACKUP)


def do_delete_db_backup(args):
    """
    Delete a db_backup
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create db_backup',
        data=args)
    return base.exec_manager_func_with_log(db_os.delete_db_backup, ctx,
                                           action=md.HistoryAction.DELETE_DB_BACKUP)


class DBBackups(Resource):
    get_db_backups_args = {
        **base.LIST_OBJECTS_ARGS
    }

    create_db_backup_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=True, validate=data_util.validate_name),
        'description': fields.Str(required=False),
    }

    @auth.login_required
    @use_args(get_db_backups_args, location=LOCATION)
    def get(self, args, db_instance_id):
        args['db_instance_id'] = db_instance_id
        return do_get_db_backups(args=args)

    @auth.login_required
    @use_args(create_db_backup_args, location=LOCATION)
    def post(self, args, db_instance_id):
        args['db_instance_id'] = db_instance_id
        return do_create_db_backup(args=args)


class DBBackup(Resource):
    get_db_backup_args = {
        **base.LIST_OBJECTS_ARGS,
        'datastore_id': fields.Str(required=False),
    }

    update_db_backup_args = {
        **base.REGION_ARGS,
    }

    delete_db_backup_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_db_backup_args, location=LOCATION)
    def get(self, args, db_backup_id, db_instance_id):
        args['db_instance_id'] = db_instance_id
        args['db_backup_id'] = db_backup_id
        return do_get_db_backup(args=args)

    @auth.login_required
    @use_args(update_db_backup_args, location=LOCATION)
    def put(self, args, db_backup_id, db_instance_id):
        args['db_instance_id'] = db_instance_id
        args['db_backup_id'] = db_backup_id
        return do_update_db_backup(args=args)

    @auth.login_required
    @use_args(delete_db_backup_args, location=LOCATION)
    def delete(self, args, db_backup_id, db_instance_id):
        args['db_instance_id'] = db_instance_id
        args['db_backup_id'] = db_backup_id
        return do_delete_db_backup(args=args)
