#
# Copyright (c) 2020 FTI-CAS
#

from functools import wraps

from application import app
from application.base import errors
from application.base.context import create_admin_context
from application.managers import base as base_mgr, config_mgr, task_mgr, user_mgr
from application import models as md
from application.utils import date_util

LOG = app.logger

ADMIN_ROLES = (md.UserRole.ADMIN, md.UserRole.ADMIN_SALE, md.UserRole.ADMIN_IT)
GET_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
LIST_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
CREATE_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
UPDATE_ROLES = ADMIN_ROLES
DELETE_ROLES = ADMIN_ROLES


def get_ticket(ctx):
    """
    Get ticket.
    :param ctx: sample ctx data:
        {
            'ticket': <ticket object>,
            'ticket_id': <ticket id if ticket object is not passed>,
            'fields': <fields to get as a list of str>,
        }
    :return:
    """
    data = ctx.data
    ticket = md.load_ticket(data.get('ticket') or data['ticket_id'])
    if not ticket:
        ctx.set_error(errors.TICKET_NOT_FOUND, status=404)
        return

    if ctx.request_user.id != ticket.user_id:
        ctx.target_user = ticket.user
    if not user_mgr.check_user(ctx, roles=GET_ROLES):
        return

    base_mgr.dump_object(ctx, object=ticket)
    return ticket


def get_tickets(ctx):
    """
    Get multiple tickets.
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

    # Admin can get tickets of a specific user or all users
    if ctx.check_request_user_role(admin_roles):
        user_id = ctx.data.get('user_id')
        override_condition = {'user_id': user_id} if user_id else None
    else:
        # User can only get his tickets
        override_condition = {'user_id': ctx.target_user.id}

    return base_mgr.dump_objects(ctx,
                                 model_class=md.Ticket,
                                 override_condition=override_condition)


def create_ticket(ctx):
    """
    Create ticket.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def update_ticket(ctx):
    """
    Update ticket.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def delete_ticket(ctx):
    """
    Delete ticket.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def get_support(ctx):
    """
    Get support.
    :param ctx: sample ctx data:
        {
            'support': <support object>,
            'support_id': <support id if support object is not passed>,
            'fields': <fields to get as a list of str>,
        }
    :return:
    """
    data = ctx.data
    support = md.load_support(data.get('support') or data['support_id'])
    if not support:
        ctx.set_error(errors.SUPPORT_NOT_FOUND, status=404)
        return

    if ctx.request_user.id != support.user_id:
        ctx.target_user = support.user
    if not user_mgr.check_user(ctx, roles=GET_ROLES):
        return

    base_mgr.dump_object(ctx, object=support)
    return support


def get_supports(ctx):
    """
    Get multiple supports.
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

    # Admin can get supports of a specific user or all users
    if ctx.check_request_user_role(admin_roles):
        user_id = ctx.data.get('user_id')
        override_condition = {'user_id': user_id} if user_id else None
    else:
        # User can only get his supports
        override_condition = {'user_id': ctx.target_user.id}

    return base_mgr.dump_objects(ctx,
                                 model_class=md.Support,
                                 override_condition=override_condition)


def create_support(ctx):
    """
    Create support.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def update_support(ctx):
    """
    Update support.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def delete_support(ctx):
    """
    Delete support.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


@task_mgr.schedule(id='support_mgr.clear_old_supports', **app.config['JOB_CLEAR_OLD_SUPPORTS'])
def clear_old_supports():
    """
    Clear old supports in DB.
    :return:
    """
    ctx = create_admin_context(task='clear out-dated supports')
    app_config = config_mgr.get_app_config(ctx)
    if ctx.failed:
        LOG.error(ctx.error)
        return
    app_config = app_config.contents

    expiration = app_config['support_expiration_days']
    timestamp = date_util.utc_future(days=-expiration)

    # TODO: only clear CLOSED/COMPLETED supports
    md.query(md.Support, md.Support.create_date < timestamp).delete(synchronize_session=False)
    md.query(md.Ticket, md.Ticket.create_date < timestamp).delete(synchronize_session=False)
