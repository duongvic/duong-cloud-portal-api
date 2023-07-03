#
# Copyright (c) 2020 FTI-CAS
#

from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args

from application import app
from application.api.v1 import base
from application.base import context
from application.managers import config_mgr
from application import models as md

LOCATION = 'default'
auth = base.auth


#####################################################################
# CONFIG
#####################################################################

def do_get_config(args):
    """
    Do get config.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get config',
        data=args)
    return base.exec_manager_func(config_mgr.get_config, ctx)


def do_get_configs(args):
    """
    Do get multiple configs.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get configs',
        data=args)
    return base.exec_manager_func(config_mgr.get_configs, ctx)


def do_create_config(args):
    """
    Do create config.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create config',
        data=args)
    return base.exec_manager_func_with_log(config_mgr.create_config, ctx,
                                           action=md.HistoryAction.CREATE_CONFIG)


def do_update_config(args):
    """
    Do update config.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update config',
        data=args)
    return base.exec_manager_func_with_log(config_mgr.update_config, ctx,
                                           action=md.HistoryAction.UPDATE_CONFIG)


def do_delete_config(args):
    """
    Do delete config.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete config',
        data=args)
    return base.exec_manager_func_with_log(config_mgr.delete_config, ctx,
                                           action=md.HistoryAction.DELETE_CONFIG)


class Configs(Resource):
    get_configs_args = base.LIST_OBJECTS_ARGS

    create_config_args = {
        # TODO
    }

    @auth.login_required
    @use_args(get_configs_args, location=LOCATION)
    def get(self, args):
        return do_get_configs(args=args)

    @auth.login_required
    @use_args(create_config_args, location=LOCATION)
    def post(self, args):
        return do_create_config(args=args)


class Config(Resource):
    get_config_args = base.GET_OBJECT_ARGS

    update_config_args = {
        # TODO
    }

    delete_config_args = {
    }

    @auth.login_required
    @use_args(get_config_args, location=LOCATION)
    def get(self, args, config_id):
        args['config_id'] = config_id
        return do_get_config(args=args)

    @auth.login_required
    @use_args(update_config_args, location=LOCATION)
    def put(self, args, config_id):
        args['config_id'] = config_id
        return do_update_config(args=args)

    @auth.login_required
    @use_args(delete_config_args, location=LOCATION)
    def delete(self, args, config_id):
        args['config_id'] = config_id
        return do_delete_config(args=args)
