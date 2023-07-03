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


keypair_os = product_types.get_product_type(
    context.create_admin_context(task='get os keypair type'),
    product_type=md.ProductType.KEY_PAIR)


#####################################################################
# COMPUTE KEYPAIR
#####################################################################

def do_get_keypair(args):
    """
    Get a keypair
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get keypair',
        data=args)
    return base.exec_manager_func(keypair_os.get_keypair, ctx)


def do_get_keypairs(args):
    """
    Get all keypairs of user
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get keypairs',
        data=args)
    return base.exec_manager_func(keypair_os.get_keypairs, ctx)


def do_create_keypair(args):
    """
    Create a new keypair
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create keypair',
        data=args)
    return base.exec_manager_func_with_log(keypair_os.create_keypair, ctx,
                                           action=md.HistoryAction.CREATE_KEYPAIR)


def do_update_keypair(args):
    """
    Update a keypair
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update keypair',
        data=args)
    return base.exec_manager_func_with_log(keypair_os.update_keypair, ctx,
                                           action=md.HistoryAction.UPDATE_KEYPAIR)


def do_delete_keypair(args):
    """
    Delete a keypair
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create keypair',
        data=args)
    return base.exec_manager_func_with_log(keypair_os.delete_keypair, ctx,
                                           action=md.HistoryAction.DELETE_KEYPAIR)


class KeyPairs(Resource):
    get_keypairs_args = {
        'user_id': fields.Str(required=False),
        **base.LIST_OBJECTS_ARGS
    }

    create_keypair_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=True, validate=data_util.validate_name),
        'public_key': fields.Str(required=True),
        'key_type': fields.Str(required=False, missing='ssh',
                               validate=validate.OneOf(['ssh', 'x509'])),
        'user_id': fields.Str(required=False),
    }

    @auth.login_required
    @use_args(get_keypairs_args, location=LOCATION)
    def get(self, args):
        return do_get_keypairs(args=args)

    @auth.login_required
    @use_args(create_keypair_args, location=LOCATION)
    def post(self, args):
        return do_create_keypair(args=args)


class KeyPair(Resource):
    get_keypair_args = {
        'user_id': fields.Str(required=False),
        **base.LIST_OBJECTS_ARGS
    }

    update_keypair_args = {
    }

    delete_keypair_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_keypair_args, location=LOCATION)
    def get(self, args, keypair_id):
        args['keypair_id'] = keypair_id
        return do_get_keypair(args=args)

    @auth.login_required
    @use_args(update_keypair_args, location=LOCATION)
    def put(self, args):
        raise Exception("Not support this method")

    @auth.login_required
    @use_args(delete_keypair_args, location=LOCATION)
    def delete(self, args, keypair_id):
        args['keypair_id'] = keypair_id
        return do_delete_keypair(args=args)
