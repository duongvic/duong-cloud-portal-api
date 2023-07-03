#
# Copyright (c) 2020 FTI-CAS
#

from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args

from application import app
from application.api.v1 import base
from application.base import context
from application.managers import balance_mgr
from application import models as md

LOCATION = 'default'
auth = base.auth


#####################################################################
# BALANCE
#####################################################################


def do_get_balance(args):
    """
    Do get balance.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get balance',
        data=args)
    return base.exec_manager_func(balance_mgr.get_balance, ctx)


def do_get_balances(args):
    """
    Do get multiple balances.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get balances',
        data=args)
    return base.exec_manager_func(balance_mgr.get_balances, ctx)


def do_create_balance(args):
    """
    Do create balance.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create balance',
        data=args)
    return base.exec_manager_func_with_log(balance_mgr.create_balance, ctx,
                                           action=md.HistoryAction.CREATE_BALANCE)


def do_update_balance(args):
    """
    Do update balance.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update balance',
        data=args)
    return base.exec_manager_func_with_log(balance_mgr.update_balance, ctx,
                                           action=md.HistoryAction.UPDATE_BALANCE)


def do_delete_balance(args):
    """
    Do delete balance.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete balance',
        data=args)
    return base.exec_manager_func_with_log(balance_mgr.delete_balance, ctx,
                                           action=md.HistoryAction.DELETE_BALANCE)


class Balances(Resource):
    get_balances_args = base.LIST_OBJECTS_ARGS

    create_balance_args = {
        # TODO
    }

    @auth.login_required
    @use_args(get_balances_args, location=LOCATION)
    def get(self, args):
        return do_get_balances(args=args)

    @auth.login_required
    @use_args(create_balance_args, location=LOCATION)
    def post(self, args):
        return do_create_balance(args=args)


class Balance(Resource):
    get_balance_args = base.GET_OBJECT_ARGS

    update_balance_args = {
        # TODO
    }

    delete_balance_args = {
    }

    @auth.login_required
    @use_args(get_balance_args, location=LOCATION)
    def get(self, args, balance_id):
        args['balance_id'] = balance_id
        return do_get_balance(args=args)

    @auth.login_required
    @use_args(update_balance_args, location=LOCATION)
    def put(self, args, balance_id):
        args['balance_id'] = balance_id
        return do_update_balance(args=args)

    @auth.login_required
    @use_args(delete_balance_args, location=LOCATION)
    def delete(self, args, balance_id):
        args['balance_id'] = balance_id
        return do_delete_balance(args=args)
