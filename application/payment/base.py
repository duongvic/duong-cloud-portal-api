#
# Copyright (c) 2020 FTI-CAS
#

from application import app

LOG = app.logger


class Payment(object):
    """
    Base payment class.
    """

    @property
    def supported(self):
        return True

    @property
    def supported_currencies(self):
        return None

    def to_payment_amount(self, amount, currency):
        """
        Convert an amount to the payment equivalent value.
        :param amount:
        :param currency:
        :return:
        """
        return amount, currency

    def from_payment_amount(self, amount, currency):
        """
        Convert an amount of the payment to our value.
        :param amount:
        :param currency:
        :return:
        """
        return amount, currency

    def start_payment(self, ctx, order):
        """
        Start payment process.
        :return:
        """

    def finish_payment(self, ctx, order):
        """
        Finish payment process.
        :return:
        """

    def cancel_payment(self, ctx, order):
        """
        Cancel payment.
        :return:
        """

    def verify_payment(self, ctx, order):
        """
        Verify payment.
        :return:
        """

    def repay_payment(self, ctx, order):
        """
        Repay payment.
        :return:
        """

    def refund_payment(self, ctx, order):
        """
        Refund payment.
        :return:
        """