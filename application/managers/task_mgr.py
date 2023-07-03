#
# Copyright (c) 2020 FTI-CAS
#

from functools import wraps

from application import app, apscheduler
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


def get_scheduler():
    """
    Get scheduler.
    :return:
    """
    return apscheduler


def schedule(trigger, **kwargs):
    """
    Schedule a background task.
    Usage:

    @schedule('cron', hour=1, minute=1)
    def do_something():
        <do something>

    :param trigger: 'cron', 'interval', ...
    :param kwargs:
    :return:
    """
    def wrapper(target_func):
        apscheduler.add_job(target_func, trigger=trigger, **kwargs)
    return wrapper


def get_task(ctx):
    """
    Get task.
    :param ctx: sample ctx data:
        {
            'task': <history object>,
            'task_id': <task id if task object is not passed>,
            'fields': <fields to get as a list of str>,
        }
    :return:
    """
    data = ctx.data
    task = md.load_task(data.get('task') or data['task_id'])
    if not task:
        ctx.set_error(errors.TASK_NOT_FOUND, status=404)
        return

    if ctx.request_user.id != task.user_id:
        ctx.target_user = task.user
    if not user_mgr.check_user(ctx, roles=GET_ROLES):
        return

    base_mgr.dump_object(ctx, object=task)
    return task


def get_tasks(ctx):
    """
    Get multiple histories.
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

    # Admin can get tasks of a specific user or all users
    if ctx.check_request_user_role(admin_roles):
        user_id = ctx.data.get('user_id')
        override_condition = {'user_id': user_id} if user_id else None
    else:
        # User can only get his tasks
        override_condition = {'user_id': ctx.target_user.id}

    return base_mgr.dump_objects(ctx,
                                 model_class=md.Task,
                                 override_condition=override_condition)


def create_task(ctx):
    """
    Create task.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def update_task(ctx):
    """
    Update task.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def delete_task(ctx):
    """
    Delete task.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)
