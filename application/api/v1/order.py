#
# Copyright (c) 2020 FTI-CAS
#

from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args

from application import app
from application.api.v1 import base
from application.base import context
from application.managers import order_mgr
from application import models as md


LOCATION = 'default'
auth = base.auth


#####################################################################
# ORDERS
#####################################################################

def do_get_order(args):
    """
    Do get order.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get order',
        data=args)
    return base.exec_manager_func(order_mgr.get_order, ctx)


def do_get_orders(args):
    """
    Do get multiple orders.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get orders',
        data=args)
    return base.exec_manager_func(order_mgr.get_orders, ctx)


def do_create_order(args):
    """
    Do create order.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create order',
        data=args)
    return base.exec_manager_func_with_log(order_mgr.create_order, ctx,
                                           action=md.HistoryAction.CREATE_ORDER)


def do_update_order(args):
    """
    Do update order.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update order',
        data=args)
    return base.exec_manager_func_with_log(order_mgr.update_order, ctx,
                                           action=md.HistoryAction.UPDATE_ORDER)


def do_delete_order(args):
    """
    Do delete order.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete order',
        data=args)
    return base.exec_manager_func_with_log(order_mgr.delete_order, ctx,
                                           action=md.HistoryAction.DELETE_ORDER)


def do_renew_order(args):
    """
    Do renew order.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='renew order',
        data=args)
    return base.exec_manager_func_with_log(order_mgr.renew_order, ctx,
                                           action=md.HistoryAction.RENEW_ORDER)


class Orders(Resource):
    get_orders_args = base.LIST_OBJECTS_ARGS

    create_order_args = {
        'groups': fields.List(
            fields.Dict(keys=fields.Str()),
            required=False,
        ),
        'type': fields.Str(required=False),
        'code': fields.Str(required=False),
        'payment_type': fields.Str(required=False),
        'currency': fields.Str(required=False),
        'region_id': fields.Str(required=False),
        'notes': fields.Str(required=False),
        'products': fields.List(
            fields.Dict(keys=fields.Str()),
            required=False,
        ),
        'amount': fields.Int(required=False),
        'duration': fields.Str(required=False),
        'settings': fields.Dict(keys=fields.Str(), required=False),
        # ADMIN only fields
        'status': fields.Str(required=False),
        'price': fields.Int(required=False),
        'price_paid': fields.Int(required=False),
    }

    @auth.login_required
    @use_args(get_orders_args, location=LOCATION)
    def get(self, args, user_id=None):
        args['user_id'] = user_id
        return do_get_orders(args=args)

    @auth.login_required
    @use_args(create_order_args, location=LOCATION)
    def post(self, args, user_id=None):
        args['user_id'] = user_id
        return do_create_order(args=args)


class Order(Resource):
    get_order_args = base.GET_OBJECT_ARGS

    update_order_args = {
        'groups': fields.List(
            fields.Dict(keys=fields.Str()),
            required=False,
        ),
        'type': fields.Str(required=False),
        'code': fields.Str(required=False),
        'payment_type': fields.Str(required=False),
        'currency': fields.Str(required=False),
        'region_id': fields.Str(required=False),
        'notes': fields.Str(required=False),
        'products': fields.List(
            fields.Dict(keys=fields.Str()),
            required=False,
        ),
        'amount': fields.Int(required=False),
        'duration': fields.Str(required=False),
        'settings': fields.Dict(keys=fields.Str(), required=False),
        # ADMIN only fields
        'status': fields.Str(required=False),
        'price': fields.Int(required=False),
        'price_paid': fields.Int(required=False),
    }

    delete_order_args = {
    }

    @auth.login_required
    @use_args(get_order_args, location=LOCATION)
    def get(self, args, order_id=None):
        args['order_id'] = order_id
        return do_get_order(args=args)

    @auth.login_required
    @use_args(update_order_args, location=LOCATION)
    def put(self, args, order_id=None):
        args['order_id'] = order_id
        return do_update_order(args=args)

    @auth.login_required
    @use_args(delete_order_args, location=LOCATION)
    def delete(self, args, order_id=None):
        args['order_id'] = order_id
        return do_delete_order(args=args)


class OrderRenew(Resource):
    renew_order_args = {
        # TODO
    }

    @auth.login_required
    @use_args(renew_order_args, location=LOCATION)
    def post(self, args, order_id=None):
        args['order_id'] = order_id
        return do_renew_order(args=args)
