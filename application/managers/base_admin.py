#
# Copyright (c) 2020 FTI-CAS
#

from flask import request

from application import app, db
from application.base import errors, common
from application.managers import base
from application import models as md
from application.utils import data_util, date_util, str_util

LOG = app.logger


def run_util_func(ctx):
    """
    Run utility function.
    """
    data = ctx.data
    action = data['action']
    user_data = data['data']

    if action == 'token_encrypt':
        params = user_data.get('params') or {}
        ctx.response = {
            'data': str_util.jwt_encode_token(user_data['value'],
                                              key=params.get('key') or None,
                                              expires_in=params.get('expires_in') or None,
                                              algorithm=params.get('algorithm') or None),
        }
        return

    if action == 'token_decrypt':
        params = user_data.get('params') or {}
        ctx.response = {
            'data': str_util.jwt_decode_token(user_data['value'],
                                              key=params.get('key') or None,
                                              algorithms=params.get('algorithms') or None),
        }
        return

    if action == 'password_gen':
        ctx.response = {
            'data': str_util.gen_user_password(user_data['value']),
        }
        return

    if action == 'password_check':
        ctx.response = {
            'data': str_util.check_user_password(user_data['hash'], user_data['value']),
        }
        return

    if action == 'db_exec_sql':
        sql_execute(ctx)
        return

    e = ValueError('Admin util action "{}" invalid.'.format(action))
    ctx.set_error(errors.REQUEST_PARAM_INVALID, cause=e, status=406)


def do_server_action(ctx):
    """
    Perform server action.
    :param ctx:
    :return:
    """
    data = ctx.data
    action = data['action']
    user_data = data.get('data') or {}

    if action == 'shutdown':
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        ctx.response = {}
        return

    e = ValueError('Admin server action "{}" invalid.'.format(action))
    ctx.set_error(errors.REQUEST_PARAM_INVALID, cause=e, status=406)


def get_model_object(ctx):
    """
    Get model object.
    :param ctx:
    :return:
    """
    if not ctx.is_super_admin_request:
        ctx.set_error(errors.USER_ACTION_NOT_ALLOWED, status=403)
        return

    data = ctx.data
    model_class = data['class']
    user_data = data['data']
    fields = data.get('fields')
    extra_fields = data.get('extra_fields')

    model_class = md.get_model_class(model_class)
    model_obj = model_class.query.get(user_data['id'])

    return base.dump_object(ctx, object=model_obj, fields=fields, extra_fields=extra_fields)


def get_model_objects(ctx):
    """
    Get model objects.
    :param ctx:
    :return:
    """
    if not ctx.is_super_admin_request:
        ctx.set_error(errors.USER_ACTION_NOT_ALLOWED, status=403)
        return

    data = ctx.data
    model_class = data['class']
    model_class = md.get_model_class(model_class)

    return base.dump_objects(ctx, model_class=model_class)


def create_model_object(ctx):
    """
    Create model object.
    :param ctx:
    :return:
    """
    if not ctx.is_super_admin_request:
        ctx.set_error(errors.USER_ACTION_NOT_ALLOWED, status=403)
        return

    data = ctx.data
    model_class = data['class']
    user_data = data['data']

    model_class = md.get_model_class(model_class)
    model_obj = model_class()

    for k, v in user_data.items():
        k_items = k.split('__')
        if len(k_items) == 2:
            k = k_items[0]
            v_type = k_items[1]
            v = base.parse_condition_value(v, v_type)
        setattr(model_obj, k, v)

    error = md.save_new(model_obj)
    if error:
        ctx.set_error(error, status=500)
        return


def update_model_object(ctx):
    """
    Update model object.
    :param ctx:
    :return:
    """
    if not ctx.is_super_admin_request:
        ctx.set_error(errors.USER_ACTION_NOT_ALLOWED, status=403)
        return

    data = ctx.data
    model_class = data['class']
    user_data = data['data']

    model_class = md.get_model_class(model_class)
    model_obj = model_class.query.get(user_data['id'])

    for k, v in user_data.items():
        if k == 'id':
            continue
        k_items = k.split('__')
        if len(k_items) == 2:
            k = k_items[0]
            v_type = k_items[1]
            v = base.parse_condition_value(v, v_type)
        setattr(model_obj, k, v)

    error = md.save(model_obj)
    if error:
        ctx.set_error(error, status=500)
        return


def delete_model_object(ctx):
    """
    Delete model object.
    :param ctx:
    :return:
    """
    if not ctx.is_super_admin_request:
        ctx.set_error(errors.USER_ACTION_NOT_ALLOWED, status=403)
        return

    data = ctx.data
    model_class = data['class']
    user_data = data['data']

    model_class = md.get_model_class(model_class)
    model_obj = model_class.query.get(user_data['id'])

    error = md.remove(model_obj)
    if error:
        ctx.set_error(error, status=500)


def sql_execute(ctx):
    if not ctx.is_super_admin_request:
        ctx.set_error(errors.USER_ACTION_NOT_ALLOWED, status=403)
        return

    data = ctx.data
    user_data = data['data']
    sql = user_data['sql']

    try:
        with db.engine.connect() as conn:
            rs = conn.execute(sql)
            ctx.response = {
                'data': str(rs),
            }
    except Exception as e:
        ctx.set_error(errors.DB_COMMIT_FAILED, cause=e, status=500)
