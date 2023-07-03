#
# Copyright (c) 2020 FTI-CAS
#

from functools import wraps

from application import app, db
from application.base import common, errors
from application.base.context import create_admin_context
from application.managers import base as base_mgr, user_mgr
from application import models as md
from application.utils import date_util

LOG = app.logger

ADMIN_ROLES = (md.UserRole.ADMIN, md.UserRole.ADMIN_SALE, md.UserRole.ADMIN_IT)
GET_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
LIST_ROLES = ADMIN_ROLES
CREATE_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
UPDATE_ROLES = (md.UserRole.ADMIN,)
DELETE_ROLES = (md.UserRole.ADMIN,)


def get_balance(ctx):
    """
    Get balance.
    :param ctx: sample ctx data:
        {
            'balance': <balance object>,
            'balance_id': <balance id if balance object is not passed>,
            'fields': <fields to get as a list of str>,
        }
    :return:
    """
    data = ctx.data
    balance = md.load_balance(data.get('balance') or data['balance_id'])
    if not balance:
        ctx.set_error(errors.USER_BALANCE_NOT_FOUND, status=404)
        return

    if ctx.request_user.id != balance.user_id:
        ctx.target_user = balance.user
    if not user_mgr.check_user(ctx, roles=GET_ROLES):
        return

    base_mgr.dump_object(ctx, object=balance)
    return balance


def get_balances(ctx):
    """
    Get multiple balances.
    :param ctx: sample ctx data:
        {
            'page': <page index starts from 0>,
            'page_size': <page size>,
            'sort_by': <attr to sort by, includes __asc, __desc>,
            'fields': <attrs to get as a list of str>,
            'condition': <reserved, custom query>,
        }
    :return:
    """
    admin_roles = md.UserRole.admin_roles_of(LIST_ROLES)

    # Admin can get balances of a specific user or all users
    if ctx.check_request_user_role(admin_roles):
        user_id = ctx.data.get('user_id')
        override_condition = {'user_id': user_id} if user_id else None
    else:
        # User can only get his balances
        override_condition = {'user_id': ctx.target_user.id}

    return base_mgr.dump_objects(ctx,
                                 model_class=md.Balance,
                                 override_condition=override_condition)


def create_balance(ctx):
    """
    Create balance.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def update_balance(ctx):
    """
    Update balance.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def delete_balance(ctx):
    """
    Delete balance.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)
