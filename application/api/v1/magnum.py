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


magnum_os = product_types.get_product_type(
    context.create_admin_context(task='get os magnum type'),
    product_type=md.ProductType.MAGNUM)


#####################################################################
# magnum_cluster
#####################################################################
def do_get_magnum_cluster(args):
    """
    Get a magnum_cluster
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get magnum_cluster',
        data=args)
    return base.exec_manager_func(magnum_os.get_magnum_cluster, ctx)


def do_get_magnum_clusters(args):
    """
    Get all magnum_clusters of user
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get magnum_clusters',
        data=args)
    return base.exec_manager_func(magnum_os.get_magnum_clusters, ctx)


def do_create_magnum_cluster(args):
    """
    Create a new magnum_cluster
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create magnum_cluster',
        data=args)
    return base.exec_manager_func_with_log(magnum_os.create_magnum_cluster, ctx,
                                           action=md.HistoryAction.CREATE_MAGNUM_CLUSTER)


def do_update_magnum_cluster(args):
    """
    Update a magnum_cluster
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update magnum_cluster',
        data=args)
    return base.exec_manager_func_with_log(magnum_os.update_magnum_cluster, ctx,
                                           action=md.HistoryAction.UPDATE_MAGNUM_CLUSTER)


def do_delete_magnum_cluster(args):
    """
    Delete a magnum_cluster
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create magnum_cluster',
        data=args)
    return base.exec_manager_func_with_log(magnum_os.delete_magnum_cluster, ctx,
                                           action=md.HistoryAction.DELETE_MAGNUM_CLUSTER)


class Clusters(Resource):
    get_magnum_clusters_args = {
        **base.LIST_OBJECTS_ARGS
    }

    create_magnum_cluster_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=True, validate=data_util.validate_name),
        'template_id': fields.Str(required=True),
        'keypair_id': fields.Str(required=True),
        'node_flavor_id': fields.Str(required=True),
        'master_flavor_id': fields.Str(required=True),
        'node_count': fields.Int(required=False, missing=1),
        'master_count': fields.Int(required=False, missing=1),
        'network_id': fields.Str(required=False),
        'subnet_id': fields.Str(required=False),
        'timeout': fields.Int(required=False, missing=3600),
        'floating_ip_enabled': fields.Bool(required=False, missing=False),
        'labels': fields.List(fields.Dict(), required=False, missing={}),
        'wait': fields.Bool(required=False, missing=False),
    }

    @auth.login_required
    @use_args(get_magnum_clusters_args, location=LOCATION)
    def get(self, args):
        return do_get_magnum_clusters(args=args)

    @auth.login_required
    @use_args(create_magnum_cluster_args, location=LOCATION)
    def post(self, args):
        return do_create_magnum_cluster(args=args)


class Cluster(Resource):
    get_magnum_cluster_args = {
        **base.LIST_OBJECTS_ARGS
    }

    update_magnum_cluster_args = {
        **base.REGION_ARGS,
        'patch': fields.List(fields.Dict(), required=False),
    }

    delete_magnum_cluster_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_magnum_cluster_args, location=LOCATION)
    def get(self, args, cluster_id):
        args['cluster_id'] = cluster_id
        return do_get_magnum_cluster(args=args)

    @auth.login_required
    @use_args(update_magnum_cluster_args, location=LOCATION)
    def put(self, args, cluster_id):
        args['cluster_id'] = cluster_id
        return do_update_magnum_cluster(args=args)

    @auth.login_required
    @use_args(delete_magnum_cluster_args, location=LOCATION)
    def delete(self, args, cluster_id):
        args['cluster_id'] = cluster_id
        return do_delete_magnum_cluster(args=args)


#####################################################################
# magnum_cluster_template
#####################################################################
def do_get_magnum_cluster_template(args):
    """
    Get a magnum_cluster_template
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get magnum_cluster_template',
        data=args)
    return base.exec_manager_func(magnum_os.get_magnum_cluster_template, ctx)


def do_get_magnum_cluster_templates(args):
    """
    Get all magnum_cluster_templates of user
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get magnum_cluster_templates',
        data=args)
    return base.exec_manager_func(magnum_os.get_magnum_cluster_templates, ctx)


def do_create_magnum_cluster_template(args):
    """
    Create a new magnum_cluster_template
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create magnum_cluster_template',
        data=args)
    return base.exec_manager_func_with_log(magnum_os.create_magnum_cluster_template, ctx,
                                           action=md.HistoryAction.CREATE_MAGNUM_CLUSTER_TEMPLATE)


def do_update_magnum_cluster_template(args):
    """
    Update a magnum_cluster_template
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update magnum_cluster_template',
        data=args)
    return base.exec_manager_func_with_log(magnum_os.update_magnum_cluster_template, ctx,
                                           action=md.HistoryAction.UPDATE_MAGNUM_CLUSTER_TEMPLATE)


def do_delete_magnum_cluster_template(args):
    """
    Delete a magnum_cluster_template
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create magnum_cluster_template',
        data=args)
    return base.exec_manager_func_with_log(magnum_os.delete_magnum_cluster_template, ctx,
                                           action=md.HistoryAction.DELETE_MAGNUM_CLUSTER_TEMPLATE)


class ClusterTemplates(Resource):
    get_magnum_cluster_templates_args = {
        **base.LIST_OBJECTS_ARGS
    }

    create_magnum_cluster_template_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=True, validate=data_util.validate_name),
        'keypair_id': fields.Str(required=True),
        'docker_volume_size': fields.Int(required=False, missing=25),
        'external_network_id': fields.Str(required=True),
        'image_id': fields.Str(required=True),
        'coe': fields.Str(required=False, missing='kubernetes',
                          validate=validate.OneOf(['kubernetes', 'swarm', 'mesos'])),
        'network_driver': fields.Str(required=False, missing='flannel',
                                     validate=validate.OneOf(['flannel', 'docker', 'calico'])),
        'master_lb_enabled': fields.Bool(required=False, missing=False),
        'floating_ip_enabled': fields.Str(required=False, missing=False),
        'volume_driver': fields.Str(required=False, missing='cinder',
                                    validate=validate.OneOf(['cinder', 'rexray'])),
        'docker_storage_driver': fields.Str(required=False, missing='overlay',
                                            validate=validate.OneOf(['overlay'])),
        'dns': fields.Str(required=False),
        'tls_disabled': fields.Bool(required=False, missing=False),
        'is_public': fields.Bool(required=False, missing=False),
        'hidden': fields.Bool(required=False, missing=False),
        'labels': fields.List(fields.Dict(), required=False, missing={}),
        # 'wait': fields.Bool(required=False, missing=False),
    }

    @auth.login_required
    @use_args(get_magnum_cluster_templates_args, location=LOCATION)
    def get(self, args):
        return do_get_magnum_cluster_templates(args=args)

    @auth.login_required
    @use_args(create_magnum_cluster_template_args, location=LOCATION)
    def post(self, args):
        return do_create_magnum_cluster_template(args=args)


class ClusterTemplate(Resource):
    get_magnum_cluster_template_args = {
        **base.LIST_OBJECTS_ARGS
    }

    update_magnum_cluster_template_args = {
        **base.REGION_ARGS,
        'patch': fields.List(fields.Dict(), required=False),
    }

    delete_magnum_cluster_template_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_magnum_cluster_template_args, location=LOCATION)
    def get(self, args, template_id):
        args['template_id'] = template_id
        return do_get_magnum_cluster_template(args=args)

    @auth.login_required
    @use_args(update_magnum_cluster_template_args, location=LOCATION)
    def put(self, args, template_id):
        args['template_id'] = template_id
        return do_update_magnum_cluster_template(args=args)

    @auth.login_required
    @use_args(delete_magnum_cluster_template_args, location=LOCATION)
    def delete(self, args, template_id):
        args['template_id'] = template_id
        return do_delete_magnum_cluster_template(args=args)
