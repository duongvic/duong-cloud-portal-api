#
# Copyright (c) 2020 FTI-CAS
#

from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args

from application import app
from application.api.v1 import base
from application.base import context
from application.managers import billing_mgr
from application import models as md

LOCATION = 'default'
auth = base.auth


#####################################################################
# BILLINGS
#####################################################################

def do_get_billing(args):
    """
    Do get billing.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get billing',
        check_token=False,
        data=args)
    return base.exec_manager_func(billing_mgr.get_billing, ctx)


def do_get_billings(args):
    """
    Do get multiple billings.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get billings',
        check_token=False,
        data=args)
    return base.exec_manager_func(billing_mgr.get_billings, ctx)


def do_create_billing(args):
    """
    Do create billing.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create billing',
        data=args)
    return base.exec_manager_func_with_log(billing_mgr.create_billing, ctx,
                                           action=md.HistoryAction.CREATE_BILLING)


def do_update_billing(args):
    """
    Do update billing.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update billing',
        data=args)
    return base.exec_manager_func_with_log(billing_mgr.update_billing, ctx,
                                           action=md.HistoryAction.UPDATE_BILLING)


def do_delete_billing(args):
    """
    Do delete billing.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete billing',
        data=args)
    return base.exec_manager_func_with_log(billing_mgr.delete_billing, ctx,
                                           action=md.HistoryAction.DELETE_BILLING)


class Billings(Resource):
    get_billings_args = base.LIST_OBJECTS_ARGS

    create_billing_args = {
        # TODO
    }

    @use_args(get_billings_args, location=LOCATION)
    def get(self, args):
        return do_get_billings(args=args)

    @auth.login_required
    @use_args(create_billing_args, location=LOCATION)
    def post(self, args):
        return do_create_billing(args=args)


class Billing(Resource):
    get_billing_args = base.GET_OBJECT_ARGS

    update_billing_args = {
        # TODO
    }

    delete_billing_args = {
    }

    @use_args(get_billing_args, location=LOCATION)
    def get(self, args, billing_id):
        args['billing_id'] = billing_id
        return do_get_billing(args=args)

    @auth.login_required
    @use_args(update_billing_args, location=LOCATION)
    def put(self, args, billing_id):
        args['billing_id'] = billing_id
        return do_update_billing(args=args)

    @auth.login_required
    @use_args(delete_billing_args, location=LOCATION)
    def delete(self, args, billing_id):
        args['billing_id'] = billing_id
        return do_delete_billing(args=args)
