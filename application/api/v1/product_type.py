#
# Copyright (c) 2020 FTI-CAS
#

from flask_restful import Resource
from webargs import fields
from webargs.flaskparser import use_args

from application import app
from application.api.v1 import base
from application.base import context
from application import models as md
from application import product_types

LOCATION = 'default'
auth = base.auth


#####################################################################
# PRODUCT TYPES
#####################################################################

def do_get_product_type(args):
    """
    Do get product type.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get product type',
        data=args)
    return base.exec_manager_func(product_types.get_product_type, ctx)


def do_get_product_types(args):
    """
    Do get multiple product types.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get product types',
        data=args)
    return base.exec_manager_func(product_types.get_product_types, ctx)


def do_create_product_type(args):
    """
    Do create product type.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create product type',
        data=args)
    return base.exec_manager_func_with_log(product_types.create_product_type, ctx,
                                           action=md.HistoryAction.CREATE_PRODUCT_TYPE)


def do_update_product_type(args):
    """
    Do update product type.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update product type',
        data=args)
    return base.exec_manager_func_with_log(product_types.update_product_type, ctx,
                                           action=md.HistoryAction.UPDATE_PRODUCT_TYPE)


def do_delete_product_type(args):
    """
    Do delete product type.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete product type',
        data=args)
    return base.exec_manager_func_with_log(product_types.delete_product_type, ctx,
                                           action=md.HistoryAction.DELETE_PRODUCT_TYPE)


class ProductTypes(Resource):
    get_product_types_args = base.LIST_OBJECTS_ARGS

    create_product_type_args = {
        # TODO
    }

    @auth.login_required
    @use_args(get_product_types_args, location=LOCATION)
    def get(self, args):
        return do_get_product_types(args=args)

    @auth.login_required
    @use_args(create_product_type_args, location=LOCATION)
    def post(self, args):
        return do_create_product_type(args=args)


class ProductType(Resource):
    get_product_type_args = base.GET_OBJECT_ARGS

    update_product_type_args = {
        # TODO
    }

    delete_product_type_args = {
    }

    @auth.login_required
    @use_args(get_product_type_args, location=LOCATION)
    def get(self, args, product_type):
        args['product_type'] = product_type
        return do_get_product_type(args=args)

    @auth.login_required
    @use_args(update_product_type_args, location=LOCATION)
    def put(self, args, product_type):
        args['product_type'] = product_type
        return do_update_product_type(args=args)

    @auth.login_required
    @use_args(delete_product_type_args, location=LOCATION)
    def delete(self, args, product_type):
        args['product_type'] = product_type
        return do_delete_product_type(args=args)
