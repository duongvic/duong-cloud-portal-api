#
# Copyright (c) 2020 FTI-CAS
#

from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args

from application import app
from application.api.v1 import base
from application.base import context
from application.managers import history_mgr
from application.utils import data_util

LOCATION = 'default'
auth = base.auth


#####################################################################
# HISTORY
#####################################################################


def do_get_history(args):
    """
    Do get history.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get history',
        data=args)
    return base.exec_manager_func(history_mgr.get_history, ctx)


def do_get_histories(args):
    """
    Do get multiple histories.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get histories',
        data=args)
    return base.exec_manager_func(history_mgr.get_histories, ctx)


def do_create_history(args):
    """
    Do create history.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create history',
        data=args)
    return base.exec_manager_func(history_mgr.create_history, ctx)


def do_update_history(args):
    """
    Do update history.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update history',
        data=args)
    return base.exec_manager_func(history_mgr.update_history, ctx)


def do_delete_history(args):
    """
    Do delete history.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete history',
        data=args)
    return base.exec_manager_func(history_mgr.delete_history, ctx)


class Histories(Resource):
    get_histories_args = base.LIST_OBJECTS_ARGS

    create_history_args = {
        # TODO
    }

    @auth.login_required
    @use_args(get_histories_args, location=LOCATION)
    def get(self, args):
        return do_get_histories(args=args)

    @auth.login_required(role=('ADMIN', 'ADMIN_LOG'))
    @use_args(create_history_args, location=LOCATION)
    def post(self, args):
        return do_create_history(args=args)


class History(Resource):
    get_history_args = base.GET_OBJECT_ARGS

    update_history_args = {
        # TODO
    }

    delete_history_args = {
    }

    @auth.login_required
    @use_args(get_history_args, location=LOCATION)
    def get(self, args, history_id):
        args['history_id'] = history_id
        return do_get_history(args=args)

    @auth.login_required
    @use_args(update_history_args, location=LOCATION)
    def put(self, args, history_id):
        args['history_id'] = history_id
        return do_update_history(args=args)

    @auth.login_required
    @use_args(delete_history_args, location=LOCATION)
    def delete(self, args, history_id):
        args['history_id'] = history_id
        return do_delete_history(args=args)
