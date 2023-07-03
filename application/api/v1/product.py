#
# Copyright (c) 2020 FTI-CAS
#

from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args

from application import app
from application.api.v1 import base
from application.base import context
from application.managers import product_mgr
from application import models as md

LOCATION = 'default'
auth = base.auth


#####################################################################
# PRODUCTS
#####################################################################

def do_get_product(args):
    """
    Do get product.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get product',
        check_token=False,
        data=args)
    return base.exec_manager_func(product_mgr.get_product, ctx)


def do_get_products(args):
    """
    Do get multiple products.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get products',
        check_token=False,
        data=args)
    return base.exec_manager_func(product_mgr.get_products, ctx)


def do_create_product(args):
    """
    Do create product.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create product',
        data=args)
    return base.exec_manager_func_with_log(product_mgr.create_product, ctx,
                                           action=md.HistoryAction.CREATE_PRODUCT)


def do_update_product(args):
    """
    Do update product.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update product',
        data=args)
    return base.exec_manager_func_with_log(product_mgr.update_product, ctx,
                                           action=md.HistoryAction.UPDATE_PRODUCT)


def do_delete_product(args):
    """
    Do delete product.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete product',
        data=args)
    return base.exec_manager_func_with_log(product_mgr.delete_product, ctx,
                                           action=md.HistoryAction.DELETE_PRODUCT)


class Products(Resource):
    get_products_args = base.LIST_OBJECTS_ARGS

    create_product_args = {
        # TODO
    }

    @use_args(get_products_args, location=LOCATION)
    def get(self, args):
        """
        Get products.
        :param args:
        :return:
        ---
        tags:
          - products
        definitions:
          - schema:
              id: Group
              properties:
                name:
                  type: string
                  description: the group's name
        parameters:
          - in: body
            name: body
            schema:
              id: User
              required:
                - email
                - name
              properties:
                email:
                  type: string
                  description: email for user
                name:
                  type: string
                  description: name for user
                address:
                  description: address for user
                  schema:
                    id: Address
                    properties:
                      street:
                        type: string
                      state:
                        type: string
                      country:
                        type: string
                      postalcode:
                        type: string
                groups:
                  type: array
                  description: list of groups
                  items:
                    $ref: "#/definitions/Group"
        responses:
          201:
            description: User created
        """
        return do_get_products(args=args)

    @auth.login_required
    @use_args(create_product_args, location=LOCATION)
    def post(self, args):
        return do_create_product(args=args)


class Product(Resource):
    get_product_args = base.GET_OBJECT_ARGS

    update_product_args = {
        # TODO
    }

    delete_product_args = {
    }

    @use_args(get_product_args, location=LOCATION)
    def get(self, args, product_id):
        args['product_id'] = product_id
        return do_get_product(args=args)

    @auth.login_required
    @use_args(update_product_args, location=LOCATION)
    def put(self, args, product_id):
        args['product_id'] = product_id
        return do_update_product(args=args)

    @auth.login_required
    @use_args(delete_product_args, location=LOCATION)
    def delete(self, args, product_id):
        args['product_id'] = product_id
        return do_delete_product(args=args)


#####################################################################
# PRODUCT PRICING
#####################################################################

def do_get_price(args):
    """
    Do get products price.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get product price',
        check_token=False,
        data=args,
    )
    if args.get('products'):
        return base.exec_manager_func(product_mgr.get_products_price, ctx)
    else:
        return base.exec_manager_func(product_mgr.get_product_price, ctx)


class Price(Resource):
    get_price_args = {
        'products': fields.List(
            fields.Dict(keys=fields.Str(),),
            required=False,
        ),
        'product_id': fields.Int(required=False),
        'amount': fields.Int(required=False, missing=1),
        'duration': fields.Str(required=False, missing='1 month'),
        'currency': fields.Str(required=False, missing='VND'),
        'data': fields.Dict(
            keys=fields.Str(),
            required=False,
        ),
        'promotion_id': fields.Int(required=False),
    }

    @use_args(get_price_args, location=LOCATION)
    def get(self, args):
        return do_get_price(args=args)

    @use_args(get_price_args, location=LOCATION)
    def post(self, args):
        return do_get_price(args=args)
