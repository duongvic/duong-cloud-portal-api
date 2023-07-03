#
# Copyright (c) 2020 FTI-CAS
#

from flask import request
from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args

from application import app
from application.api.v1 import base
from application.base import context, common
from application.managers import base_admin as admin_mgr
from application import models as md

LOCATION = 'default'
auth = base.auth


#####################################################################
# MAINTENANCE MODE
#####################################################################

def do_get_maint_mode():
    """
    Do get maintenance mode.
    :return:
    """
    return {"maintenance": base.maintenance}, 200


def do_set_maint_mode(mode):
    """
    Do set maintenance mode.
    :param mode:
    :return:
    """
    base.maintenance = True if mode else False
    return {"maintenance": base.maintenance}, 200


class Maintenance(Resource):
    def get(self):
        return do_get_maint_mode()

    @auth.login_required(role=('ADMIN', 'ADMIN_IT'))
    def post(self):
        return do_set_maint_mode(mode=True)

    @auth.login_required(role=('ADMIN', 'ADMIN_IT'))
    def delete(self):
        return do_set_maint_mode(mode=False)


#####################################################################
# SERVER ACTIONS
#####################################################################

def do_server_action(args):
    """
    Do shutdown server.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='do server action',
        data=args)
    return base.exec_manager_func_with_log(admin_mgr.do_server_action, ctx,
                                           action=md.HistoryAction.PERFORM_SERVER_ACTION)


class ServerActions(Resource):
    server_action_args = {
        'action': fields.Str(required=True),
        'data': fields.Dict(required=False),
    }

    @auth.login_required(role='ADMIN')
    @use_args(server_action_args, location=LOCATION)
    def post(self, args):
        return do_server_action(args=args)


#####################################################################
# MODEL OBJECTS
#####################################################################


def do_get_model_object(args):
    """
    Get any model object.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get model object',
        data=args)
    return base.exec_manager_func_with_log(admin_mgr.get_model_object, ctx,
                                           action=md.HistoryAction.GET_MODEL_OBJECT)


def do_get_model_objects(args):
    """
    Get model objects.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get model objects',
        data=args)
    return base.exec_manager_func_with_log(admin_mgr.get_model_objects, ctx,
                                           action=md.HistoryAction.GET_MODEL_OBJECTS)


def do_create_model_object(args):
    """
    Create model object.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create model object',
        data=args)
    return base.exec_manager_func_with_log(admin_mgr.create_model_object, ctx,
                                           action=md.HistoryAction.CREATE_MODEL_OBJECT)


def do_update_model_object(args):
    """
    Update any model object.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update model object',
        data=args)
    return base.exec_manager_func_with_log(admin_mgr.update_model_object, ctx,
                                           action=md.HistoryAction.UPDATE_MODEL_OBJECT)


def do_delete_model_object(args):
    """
    Delete model object.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete model object',
        data=args)
    return base.exec_manager_func_with_log(admin_mgr.delete_model_object, ctx,
                                           action=md.HistoryAction.DELETE_MODEL_OBJECT)


class ModelObjects(Resource):
    get_objs_args = base.LIST_OBJECTS_ARGS

    @auth.login_required(role='ADMIN')
    @use_args(get_objs_args, location=LOCATION)
    def get(self, args, model_class=None):
        args['class'] = model_class
        return do_get_model_objects(args=args)


class ModelObject(Resource):
    get_obj_args = {
        'data': fields.Dict(required=True),
        'fields': fields.List(fields.Str(), required=False),
        'extra_fields': fields.List(fields.Str(), required=False),
    }

    create_obj_args = {
        'data': fields.Dict(required=True),
    }

    update_obj_args = {
        'data': fields.Dict(required=True),  # data must contains 'id' attr
    }

    delete_obj_args = {
        'data': fields.Dict(required=True),
    }

    @auth.login_required(role='ADMIN')
    @use_args(get_obj_args, location=LOCATION)
    def get(self, args, model_class=None):
        args['class'] = model_class
        return do_get_model_object(args=args)

    @auth.login_required(role='ADMIN')
    @use_args(create_obj_args, location=LOCATION)
    def post(self, args, model_class=None):
        args['class'] = model_class
        return do_create_model_object(args=args)

    @auth.login_required(role='ADMIN')
    @use_args(update_obj_args, location=LOCATION)
    def put(self, args, model_class=None):
        args['class'] = model_class
        return do_update_model_object(args=args)

    @auth.login_required(role='ADMIN')
    @use_args(delete_obj_args, location=LOCATION)
    def delete(self, args, model_class=None):
        args['class'] = model_class
        return do_delete_model_object(args=args)


#####################################################################
# MODEL OBJECTS
#####################################################################


def do_utility_function(args):
    """
    Run a utility function.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='run utility function',
        data=args)
    return base.exec_manager_func(admin_mgr.run_util_func, ctx)


class Utilities(Resource):
    utility_args = {
        'action': fields.Str(required=True),  # encrypt, decrypt
        'data': fields.Dict(required=True),
    }

    @auth.login_required(role=('ADMIN', 'ADMIN_IT'))
    @use_args(utility_args, location=LOCATION)
    def post(self, args):
        return do_utility_function(args=args)
