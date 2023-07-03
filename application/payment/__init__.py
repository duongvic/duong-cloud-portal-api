#
# Copyright (c) 2020 FTI-CAS
#

from application import app
from application.base import errors
from application import models as md
from application.payment import cash, bank_transfer, credit_card, vnpay

LOG = app.logger


PAYMENTS = {
    md.PaymentType.CASH: cash.CashPayment(),
    md.PaymentType.BANK_TRANSFER: bank_transfer.BankTransferPayment(),
    md.PaymentType.CREDIT_CARD: credit_card.CreditCardPayment(),
    md.PaymentType.GATE_VNPAY: vnpay.VNPayPayment(),
}


def get_payment(ctx, payment_type=None, check_support=True):
    """
    Get payment gate for the type.
    :param ctx:
    :param payment_type: one of md.PaymentType values
    :param check_support:
    :return:
    """
    data = ctx.data
    payment_type = payment_type or data['payment_type']
    check_support = check_support if check_support is not None else data['check_support']

    payment = PAYMENTS.get(payment_type)
    if not payment:
        ctx.set_error(errors.PAYMENT_NOT_FOUND, status=404)
        return

    if check_support and not payment.supported:
        ctx.set_error(errors.PAYMENT_TYPE_NOT_SUPPORTED, status=406)
        return

    ctx.response = {
        'payment': payment,
    }
    return payment


def get_payments(ctx):
    """
    Get multiple payments.
    :param ctx:
    :return:
    """
    payments = []
    for k, v in PAYMENTS.items():
        payments.append({
            'type': k.lower(),
            'supported': v.supported,
        })
    ctx.response = {
        'data': payments,
        'has_more': False,
    }
    return payments


def create_payment(ctx):
    """
    Create payment.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def update_payment(ctx):
    """
    Update payment.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def delete_payment(ctx):
    """
    Delete payment.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)
