#
# Copyright (c) 2020 FTI-CAS
#

from functools import wraps

from application import app, db
from application.base import common, errors
from application.base.context import create_admin_context
from application.managers import base as base_mgr, config_mgr, task_mgr, user_mgr
from application import models as md
from application.utils import date_util

LOG = app.logger

ADMIN_ROLES = (md.UserRole.ADMIN, md.UserRole.ADMIN_SALE, md.UserRole.ADMIN_IT)
GET_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
LIST_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
CREATE_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
UPDATE_ROLES = (md.UserRole.ADMIN,)
DELETE_ROLES = (md.UserRole.ADMIN,)


def get_history(ctx):
    """
    Get history.
    :param ctx: sample ctx data:
        {
            'history': <history object>,
            'history_id': <history id if history object is not passed>,
            'fields': <fields to get as a list of str>,
        }
    :return:
    """
    data = ctx.data
    history = md.load_history(data.get('history') or data['history_id'])
    if not history:
        ctx.set_error(errors.HISTORY_NOT_FOUND, status=404)
        return

    if ctx.request_user.id != history.request_user_id:
        ctx.target_user = history.request_user
    if not user_mgr.check_user(ctx, roles=GET_ROLES):
        return

    on_get_histories(ctx, [history])
    base_mgr.dump_object(ctx, object=history)
    return history


def get_histories(ctx):
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

    # Admin can get history of a specific user or all users
    if ctx.check_request_user_role(admin_roles):
        user_id = ctx.data.get('user_id')
        override_condition = {'target_user_id': user_id} if user_id else None
    else:
        # User can only get his history
        user_id = ctx.target_user.id
        override_condition = {'request_user_id': user_id, 'target_user_id': user_id}

    return base_mgr.dump_objects(ctx,
                                 model_class=md.History,
                                 override_condition=override_condition,
                                 on_loaded_func=on_get_histories)


def on_get_histories(ctx, histories):
    """
    Called when histories loaded in get_histories().
    :param ctx:
    :param histories:
    :return:
    """
    # Check if items are timed out
    try:
        for hist in histories:
            timeout_at = hist.contents.get('action_timeout_at')
            if timeout_at:
                timeout_at = date_util.utc_from_sec(timeout_at)
                if timeout_at < date_util.utc_now():
                    hist.status = md.HistoryStatus.TIMED_OUT
        # Save modified items
        md.save(histories)
    except Exception as e:
        LOG.error('Failed to parse history action time out. Error: {}'.format(e))

    return histories


def create_history(ctx):
    """
    Create history.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def update_history(ctx):
    """
    Update history.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def delete_history(ctx):
    """
    Delete history.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def log_ctx(action, func=None, **kwargs):
    """
    Save history log for an action.
    Usage:

    def log_func(ctx, history):
        history.contents.update({
            <some detailed info>
        })

    @log('I DO SOMETHING', func=log_func)
    def do_something(ctx. *a, **kw):
        return something

    :param action: see md.HistoryAction values
    :param func:
    :return:
    """
    def wrapper(target_func):
        @wraps(target_func)
        def func_wrapper(ctx, *a, **kw):
            try:
                return target_func(ctx, *a, **kw)
            finally:
                _log_ctx_action(ctx, action, func, **kwargs)
        return func_wrapper
    return wrapper


def _log_ctx_action(ctx, action, func, **kw):
    """
    Log context action.
    :param ctx:
    :param action:
    :param func:
    :return:
    """
    if ctx.succeed:
        status = md.HistoryStatus.IN_PROGRESS if ctx.status == 202 else md.HistoryStatus.SUCCEEDED
    else:
        status = md.HistoryStatus.FAILED

    history = md.History(
        status=status,
        type=kw.get('type') or md.HistoryType.USER,
        action=action,
        start_date=date_util.utc_now(),
        target_user_id=ctx.target_user.id if ctx.target_user else None,
        request_user_id=ctx.request_user.id if ctx.request_user else None,
        task_id=kw.get('task_id'),
        contents={},
    )
    # Log error if action failed
    if ctx.failed:
        history.contents.update({
            'error': str(ctx.error),
            'status': ctx.status,
        })
    # Call log func
    try:
        func(ctx, history)
        # Save history log
        error = md.save_new(history)
        if error:
            # TODO
            pass
        else:
            ctx.log_args['log_id'] = history.id
            ctx.log_args['log_status'] = history.status
    except BaseException as e:
        LOG.warning('Exception when saving history: {}'.format(e))


@task_mgr.schedule(id='history_mgr.clear_old_logs', **app.config['JOB_CLEAR_OLD_HISTORY_LOGS'])
def clear_old_logs():
    """
    Clear old history logs in DB.
    :return:
    """
    ctx = create_admin_context(task='clear out-dated history logs')
    app_config = config_mgr.get_app_config(ctx)
    if ctx.failed:
        LOG.error(ctx.error)
        return
    app_config = app_config.contents

    log_expiration = app_config['history_log_expiration_days']
    timestamp = date_util.utc_future(days=-log_expiration)
    md.query(md.History, md.History.create_date < timestamp).delete(synchronize_session=False)
