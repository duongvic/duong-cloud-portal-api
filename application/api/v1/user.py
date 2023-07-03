#
# Copyright (c) 2020 FTI-CAS
#

from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args

from application import app
from application.api.v1 import base
from application.base import context
from application.managers import history_mgr, user_mgr
from application import models as md
from application.utils import request_util

LOCATION = 'default'
auth = base.auth


#####################################################################
# USERS
#####################################################################

def do_get_user(args):
    """
    Do get user.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get user',
        data=args)
    return base.exec_manager_func(user_mgr.get_user, ctx)


def do_get_users(args):
    """
    Do get multiple users.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get users',
        data=args)
    return base.exec_manager_func(user_mgr.get_users, ctx)


def do_create_user(args):
    """
    Do create user.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create user',
        check_token=False,
        data=args)
    return base.exec_manager_func(user_mgr.create_user, ctx)


def do_update_user(args):
    """
    Do update user.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update user',
        data=args)
    return base.exec_manager_func_with_log(user_mgr.update_user, ctx,
                                           action=md.HistoryAction.UPDATE_USER)


def do_delete_user(args):
    """
    Do delete user.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete user',
        data=args)
    return base.exec_manager_func_with_log(user_mgr.delete_user, ctx,
                                           action=md.HistoryAction.DELETE_USER)


class Users(Resource):
    get_users_args = base.LIST_OBJECTS_ARGS

    create_user_args = {
        'user_name': fields.Str(required=True),
        'email': fields.Str(required=True),
        'password': fields.Str(required=True),
        'full_name': fields.Str(required=True, allow_none=True),
        'id_number': fields.Str(required=False, allow_none=True),
        'cellphone': fields.Str(required=True, allow_none=True),
        'workphone': fields.Str(required=False, allow_none=True),
        'organization': fields.Str(required=False, allow_none=True),
        'address': fields.Str(required=False, allow_none=True),
        'city': fields.Str(required=False, allow_none=True),
        'country_code': fields.Str(required=False, missing='VN'),
        'language': fields.Str(required=False, allow_none=True),
        # ADMIN set role, status
        'role': fields.Str(required=False),  # role in form role1,role2,role3
        'status': fields.Str(required=False),
        'group_id': fields.Int(required=False),
    }

    @auth.login_required
    @use_args(get_users_args, location=LOCATION)
    def get(self, args):
        return do_get_users(args=args)

    @use_args(create_user_args, location=LOCATION)
    def post(self, args):
        return do_create_user(args=args)


class User(Resource):
    get_user_args = base.GET_OBJECT_ARGS

    update_user_args = {
        'password': fields.Str(required=False),  # Requires old_password if change this (except admins do)
        'old_password': fields.Str(required=False),
        'full_name': fields.Str(required=False, allow_none=True),
        'id_number': fields.Str(required=False, allow_none=True),
        'cellphone': fields.Str(required=False, allow_none=True),
        'workphone': fields.Str(required=False, allow_none=True),
        'organization': fields.Str(required=False, allow_none=True),
        'address': fields.Str(required=False, allow_none=True),
        'city': fields.Str(required=False, allow_none=True),
        'country_code': fields.Str(required=False, allow_none=True),
        'language': fields.Str(required=False, allow_none=True),
        # ADMIN update role, status
        'role': fields.Str(required=False),      # role in form of 'role1,role2,role3'
        'status': fields.Str(required=False),
        'group_id': fields.Int(required=False),
    }

    delete_user_args = {
    }

    @auth.login_required
    @use_args(get_user_args, location=LOCATION)
    def get(self, args, user_id=None):
        args['user_id'] = user_id
        return do_get_user(args=args)

    @auth.login_required
    @use_args(update_user_args, location=LOCATION)
    def put(self, args, user_id=None):
        args['user_id'] = user_id
        return do_update_user(args=args)

    @auth.login_required
    @use_args(delete_user_args, location=LOCATION)
    def delete(self, args, user_id=None):
        args['user_id'] = user_id
        return do_delete_user(args=args)


#####################################################################
# AUTH
#####################################################################

def do_login(args):
    """
    Do login user.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='login user',
        check_token=False,
        data=args)

    def _log_func(ctx, history):
        if ctx.succeed and ctx.is_user_request:
            raise ValueError('User login successfully. Skip logging this action.')
        data = base.default_log_filter(ctx)
        data['ip'] = ctx.request.access_route
        history.contents.update(data)

    return base.exec_manager_func_with_log(user_mgr.login, ctx,
                                           action=md.HistoryAction.LOGIN,
                                           log_func=_log_func)


def do_logout(args):
    """
    Do logout user.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='logout user',
        data=args)
    return base.exec_manager_func(user_mgr.logout, ctx)


class Auth(Resource):
    login_args = {
        'user_name': fields.Str(required=True),
        'password': fields.Str(required=True),
        'remember_me': fields.Bool(required=False, missing=False),
        'get_user_data': fields.Bool(required=False),
        'user_data_fields': fields.List(fields.Str(), required=False),
    }

    logout_args = {
    }

    @use_args(login_args, location=LOCATION)
    def post(self, args):
        return do_login(args=args)

    @auth.login_required
    @use_args(logout_args, location=LOCATION)
    def delete(self, args):
        return do_logout(args=args)


#####################################################################
# TOKENS
#####################################################################

def do_refresh_token(args):
    """
    Do refresh token.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='refresh user token',
        data=args)
    return base.exec_manager_func(user_mgr.refresh_token, ctx)


class RefreshToken(Resource):
    refresh_token_args = {
    }

    @auth.login_required
    @use_args(refresh_token_args, location=LOCATION)
    def post(self, args):
        return do_refresh_token(args=args)


#####################################################################
# ACTIVATION
#####################################################################

def do_activate(args):
    """
    Do activate user.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='activate user',
        check_token=False,
        data=args)
    ctx.clear_error()
    return base.exec_manager_func(user_mgr.activate_user, ctx)


class Activate(Resource):
    activate_args = {
        'token': fields.Str(required=True),
    }

    @use_args(activate_args, location=LOCATION)
    def post(self, args):
        return do_activate(args=args)


#####################################################################
# RESET PASSWORD
#####################################################################

def do_forgot_password(args):
    """
    Request resetting password for user.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='request reset password',
        check_token=False,
        data=args)
    ctx.clear_error()
    return base.exec_manager_func(user_mgr.request_reset_password, ctx)


class ForgotPassword(Resource):
    forgot_password_args = {
        'user_name': fields.Str(required=True),
    }

    @use_args(forgot_password_args, location=LOCATION)
    def post(self, args):
        return do_forgot_password(args=args)


#####################################################################
# RESET PASSWORD
#####################################################################

def do_reset_password(args):
    """
    Do reset password for user.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='reset password',
        check_token=False,
        data=args)
    ctx.clear_error()
    return base.exec_manager_func(user_mgr.reset_password, ctx)

    # return base.exec_manager_func_with_log(user_mgr.reset_password, ctx,
    #                                        action=md.HistoryAction.RESET_USER_PASSWORD)


class ResetPassword(Resource):
    reset_password_args = {
        'token': fields.Str(required=True),
    }

    @use_args(reset_password_args, location=LOCATION)
    def post(self, args):
        return do_reset_password(args=args)
