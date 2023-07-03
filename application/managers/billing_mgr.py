#
# Copyright (c) 2020 FTI-CAS
#

from application import app
from application.base import errors
from application.managers import base as base_mgr, user_mgr
from application import models as md

LOG = app.logger

ADMIN_ROLES = (md.UserRole.ADMIN, md.UserRole.ADMIN_SALE, md.UserRole.ADMIN_IT)
GET_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
LIST_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
CREATE_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
UPDATE_ROLES = (md.UserRole.ADMIN,)
DELETE_ROLES = (md.UserRole.ADMIN,)


def get_billing(ctx):
    """
    Get billing.
    :param ctx: sample ctx data:
        {
            'billing': <billing object>,
            'billing_id': <billing id if billing object is not passed>,
            'fields': <fields to get as a list of str>,
        }
    :return:
    """
    data = ctx.data
    billing = md.load_billing(data.get('billing') or data['billing_id'])
    if not billing:
        ctx.set_error(errors.BILLING_NOT_FOUND, status=404)
        return

    if ctx.request_user.id != billing.user_id:
        ctx.target_user = billing.user
    if not user_mgr.check_user(ctx, roles=GET_ROLES):
        return

    base_mgr.dump_object(ctx, object=billing)
    return billing


def get_billings(ctx):
    """
    Get multiple billings.
    :param ctx: sample ctx data:
        {
            'page': <page index starts from 0>,
            'page_size': <page size>,
            'sort_by': <attr to sort by>,
            'fields': <attrs to get as a list of str>,
            'condition': <reserved, custom query>,
        }
    :return:
    """
    admin_roles = md.UserRole.admin_roles_of(LIST_ROLES)

    # Admin can get billing of a specific user or all users
    if ctx.check_request_user_role(admin_roles):
        user_id = ctx.data.get('user_id')
        override_condition = {'user_id': user_id} if user_id else None
    else:
        # User can only get his billings
        override_condition = {'user_id': ctx.target_user.id}

    return base_mgr.dump_objects(ctx,
                                 model_class=md.Billing,
                                 override_condition=override_condition)


def create_billing(ctx):
    """
    Create billing.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def update_billing(ctx):
    """
    Update billing.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def delete_billing(ctx):
    """
    Delete billing.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)
