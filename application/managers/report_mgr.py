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
GET_ROLES = ADMIN_ROLES
LIST_ROLES = ADMIN_ROLES
CREATE_ROLES = (md.UserRole.ADMIN,)
UPDATE_ROLES = (md.UserRole.ADMIN,)
DELETE_ROLES = (md.UserRole.ADMIN,)


def get_report(ctx):
    """
    Get report.
    :param ctx: sample ctx data:
        {
            'report': <report object>,
            'report_id': <report id if report object is not passed>,
            'fields': <fields to get as a list of str>,
        }
    :return:
    """
    if not user_mgr.check_user(ctx, roles=GET_ROLES):
        return

    data = ctx.data
    report = md.load_report(data.get('report') or data['report_id'])
    if not report:
        ctx.set_error(errors.REPORT_NOT_FOUND, status=404)
        return

    base_mgr.dump_object(ctx, object=report)
    return report


def get_reports(ctx):
    """
    Get multiple reports.
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
    return base_mgr.dump_objects(ctx, model_class=md.Report, roles_required=LIST_ROLES)


def create_report(ctx):
    """
    Create report.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def update_report(ctx):
    """
    Update report.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def delete_report(ctx):
    """
    Delete report.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


@task_mgr.schedule(id='report_mgr.clear_old_reports', **app.config['JOB_CLEAR_OLD_REPORTS'])
def clear_old_reports():
    """
    Clear old reports in DB.
    :return:
    """
    ctx = create_admin_context(task='clear out-dated reports')
    app_config = config_mgr.get_app_config(ctx)
    if ctx.failed:
        LOG.error(ctx.error)
        return
    app_config = app_config.contents

    expiration = app_config['report_expiration_days']
    timestamp = date_util.utc_future(days=-expiration)
    md.query(md.Report, md.Report.start_date < timestamp).delete(synchronize_session=False)
