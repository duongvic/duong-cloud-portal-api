#
# Copyright (c) 2020 FTI-CAS
#

from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args

from application import app
from application.api.v1 import base
from application.base import context
from application.managers import promotion_mgr
from application import models as md

LOCATION = 'default'
auth = base.auth


#####################################################################
# PROMOTIONS
#####################################################################

def do_get_promotion(args):
    """
    Do get promotion.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get promotion',
        check_token=False,
        data=args)
    return base.exec_manager_func(promotion_mgr.get_promotion, ctx)


def do_get_promotions(args):
    """
    Do get multiple promotions.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get promotions',
        check_token=False,
        data=args)
    return base.exec_manager_func(promotion_mgr.get_promotions, ctx)


def do_create_promotion(args):
    """
    Do create promotion.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create promotion',
        data=args)
    return base.exec_manager_func_with_log(promotion_mgr.create_promotion, ctx,
                                           action=md.HistoryAction.CREATE_PROMOTION)


def do_update_promotion(args):
    """
    Do update promotion.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update promotion',
        data=args)
    return base.exec_manager_func_with_log(promotion_mgr.update_promotion, ctx,
                                           action=md.HistoryAction.UPDATE_PROMOTION)


def do_delete_promotion(args):
    """
    Do delete promotion.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete promotion',
        data=args)
    return base.exec_manager_func_with_log(promotion_mgr.delete_promotion, ctx,
                                           action=md.HistoryAction.DELETE_PROMOTION)


class Promotions(Resource):
    get_promotions_args = base.LIST_OBJECTS_ARGS

    create_promotion_args = {
        # TODO
    }

    @use_args(get_promotions_args, location=LOCATION)
    def get(self, args):
        return do_get_promotions(args=args)

    @auth.login_required
    @use_args(create_promotion_args, location=LOCATION)
    def get(self, args):
        return do_create_promotion(args=args)


class Promotion(Resource):
    get_promotion_args = base.GET_OBJECT_ARGS

    update_promotion_args = {
        # TODO
    }

    delete_promotion_args = {
    }

    @use_args(get_promotion_args, location=LOCATION)
    def get(self, args, promotion_id):
        args['promotion_id'] = promotion_id
        return do_get_promotion(args=args)

    @auth.login_required
    @use_args(update_promotion_args, location=LOCATION)
    def put(self, args, promotion_id):
        args['promotion_id'] = promotion_id
        return do_update_promotion(args=args)

    @auth.login_required
    @use_args(delete_promotion_args, location=LOCATION)
    def delete(self, args, promotion_id):
        args['promotion_id'] = promotion_id
        return do_delete_promotion(args=args)
