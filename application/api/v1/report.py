#
# Copyright (c) 2020 FTI-CAS
#

from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args

from application import app
from application.api.v1 import base
from application.base import context
from application.managers import report_mgr
from application import models as md

LOCATION = 'default'
auth = base.auth


#####################################################################
# REPORTS
#####################################################################

def do_get_report(args):
    """
    Do get report.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get report',
        data=args)
    return base.exec_manager_func(report_mgr.get_report, ctx)


def do_get_reports(args):
    """
    Do get multiple reports.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get reports',
        data=args)
    return base.exec_manager_func(report_mgr.get_reports, ctx)


def do_create_report(args):
    """
    Do create report.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create report',
        data=args)
    return base.exec_manager_func_with_log(report_mgr.create_report, ctx,
                                           action=md.HistoryAction.CREATE_REPORT)


def do_update_report(args):
    """
    Do update report.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update report',
        data=args)
    return base.exec_manager_func_with_log(report_mgr.update_report, ctx,
                                           action=md.HistoryAction.UPDATE_REPORT)


def do_delete_report(args):
    """
    Do delete report.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete report',
        data=args)
    return base.exec_manager_func_with_log(report_mgr.delete_report, ctx,
                                           action=md.HistoryAction.DELETE_REPORT)


class Reports(Resource):
    get_reports_args = base.LIST_OBJECTS_ARGS

    create_report_args = {
        # TODO
    }

    @auth.login_required
    @use_args(get_reports_args, location=LOCATION)
    def get(self, args):
        return do_get_reports(args=args)

    @auth.login_required
    @use_args(create_report_args, location=LOCATION)
    def post(self, args):
        return do_create_report(args=args)


class Report(Resource):
    get_report_args = base.GET_OBJECT_ARGS

    update_report_args = {
        # TODO
    }

    delete_report_args = {
    }

    @auth.login_required
    @use_args(get_report_args, location=LOCATION)
    def get(self, args, report_id):
        args['report_id'] = report_id
        return do_get_report(args=args)

    @auth.login_required
    @use_args(update_report_args, location=LOCATION)
    def put(self, args, report_id):
        args['report_id'] = report_id
        return do_update_report(args=args)

    @auth.login_required
    @use_args(delete_report_args, location=LOCATION)
    def delete(self, args, report_id):
        args['report_id'] = report_id
        return do_delete_report(args=args)
