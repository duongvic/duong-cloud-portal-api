#
# Copyright (c) 2020 FTI-CAS
#

from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args

from application import app
from application.api.v1 import base
from application.base import context
from application import models as md
from application import product_types


LOCATION = 'default'
auth = base.auth


os_base = product_types.get_product_type(
    context.create_admin_context(task='get OpenStack base'),
    product_type=md.ProductType.COMPUTE).os_base()


#####################################################################
# CLUSTERS
#####################################################################


def do_get_cluster(args):
    """
    Do get cluster.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get cluster',
        data=args)
    return base.exec_manager_func(os_base.get_cluster, ctx)


def do_get_clusters(args):
    """
    Do get multiple clusters.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get clusters',
        data=args)
    return base.exec_manager_func(os_base.get_clusters, ctx)


def do_create_cluster(args):
    """
    Do create cluster.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create cluster',
        data=args)

    return base.exec_manager_func_with_log(os_base.create_cluster, ctx,
                                           action=md.HistoryAction.CREATE_CLUSTER)


def do_update_cluster(args):
    """
    Do update cluster.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update cluster',
        data=args)

    return base.exec_manager_func_with_log(os_base.update_cluster, ctx,
                                           action=md.HistoryAction.UPDATE_CLUSTER)


def do_delete_cluster(args):
    """
    Do delete cluster.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete cluster',
        data=args)

    return base.exec_manager_func_with_log(os_base.delete_cluster, ctx,
                                           action=md.HistoryAction.DELETE_CLUSTER)


class Clusters(Resource):
    get_clusters_args = base.LIST_OBJECTS_ARGS

    create_cluster_args = {

    }

    @auth.login_required
    @use_args(get_clusters_args, location=LOCATION)
    def get(self, args):
        return do_get_clusters(args=args)

    @auth.login_required
    @use_args(create_cluster_args, location=LOCATION)
    def post(self, args):
        return do_create_cluster(args=args)


class Cluster(Resource):
    get_cluster_args = base.GET_OBJECT_ARGS

    update_cluster_args = {
    }

    delete_cluster_args = {
    }

    @auth.login_required
    @use_args(get_cluster_args, location=LOCATION)
    def get(self, args, cluster_id=None):
        args['cluster_id'] = cluster_id
        return do_get_cluster(args=args)

    @auth.login_required
    @use_args(update_cluster_args, location=LOCATION)
    def put(self, args, cluster_id=None):
        args['cluster_id'] = cluster_id
        return do_update_cluster(args=args)

    @auth.login_required
    @use_args(delete_cluster_args, location=LOCATION)
    def delete(self, args, cluster_id):
        args['cluster_id'] = cluster_id
        return do_delete_cluster(args=args)
