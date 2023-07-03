#
# Copyright (c) 2020 FTI-CAS
#

from flask_restful import Resource
from webargs import fields
from webargs.flaskparser import use_args

from application import app
from application.api.v1 import base
from application.base import context
from application.managers import order_mgr
from application import models as md
from application import payment
from application.payment import vnpay

LOCATION = 'default'
auth = base.auth


#####################################################################
# PAYMENTS
#####################################################################


def do_get_payment(args):
    """
    Do get payment.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get payment',
        check_token=False,
        data=args)
    return base.exec_manager_func(payment.get_payment, ctx)


def do_get_payments(args):
    """
    Do get multiple payments.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get payments',
        check_token=False,
        data=args)
    return base.exec_manager_func(payment.get_payments, ctx)


def do_create_payment(args):
    """
    Do create payment.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create payment',
        data=args)
    return base.exec_manager_func_with_log(payment.create_payment, ctx,
                                           action=md.HistoryAction.CREATE_PAYMENT)


def do_update_payment(args):
    """
    Do update payment.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update payment',
        data=args)
    return base.exec_manager_func_with_log(payment.update_payment, ctx,
                                           action=md.HistoryAction.UPDATE_PAYMENT)


def do_delete_payment(args):
    """
    Do delete payment.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete payment',
        data=args)
    return base.exec_manager_func_with_log(payment.delete_payment, ctx,
                                           action=md.HistoryAction.DELETE_PAYMENT)


class Payments(Resource):
    get_payments_args = base.LIST_OBJECTS_ARGS

    create_payment_args = {
        # TODO
    }

    @use_args(get_payments_args, location=LOCATION)
    def get(self, args):
        return do_get_payments(args=args)

    @auth.login_required
    @use_args(create_payment_args, location=LOCATION)
    def post(self, args):
        return do_create_payment(args=args)


class Payment(Resource):
    get_payment_args = base.GET_OBJECT_ARGS

    update_payment_args = {
        # TODO
    }

    delete_payment_args = {
    }

    @use_args(get_payment_args, location=LOCATION)
    def get(self, args, payment_type):
        args['payment_type'] = payment_type
        return do_get_payment(args=args)

    @auth.login_required
    @use_args(update_payment_args, location=LOCATION)
    def put(self, args, payment_type):
        args['payment_type'] = payment_type
        return do_update_payment(args=args)

    @auth.login_required
    @use_args(delete_payment_args, location=LOCATION)
    def delete(self, args, payment_type):
        args['payment_type'] = payment_type
        return do_delete_payment(args=args)


#####################################################################
# VNPAY
#####################################################################


def do_vnpay_ipn(args):
    """
    Process VNPay IPN request.
    :param args:
    :return:
    """
    args = {
        'order_id': int(args['vnp_TxnRef']),
        'payment_type': md.PaymentType.GATE_VNPAY,
        'payment_info': args,
        'ignore_if_completed': args.get('ignore_if_completed', True),
    }
    ctx = context.create_context(
        task='process VNPay IPN request',
        check_token=False,
        data=args)
    return base.exec_manager_func_with_log(order_mgr.finish_order, ctx,
                                           action=md.HistoryAction.FINISH_PAYMENT)


class VNPayIPN(Resource):
    ipn_args = {k: fields.Str() for k in vnpay.IPN_REQUEST_ARGS}

    @use_args(ipn_args, location=LOCATION)
    def get(self, args):
        return do_vnpay_ipn(args=args)

    @use_args(ipn_args, location=LOCATION)
    def post(self, args):
        return do_vnpay_ipn(args=args)
