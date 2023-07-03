#
# Copyright (c) 2020 FTI-CAS
#

from application.payment import base


class CreditCardPayment(base.Payment):
    """
    Credit Card payment.
    """

    @property
    def supported(self):
        return False
