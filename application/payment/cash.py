#
# Copyright (c) 2020 FTI-CAS
#

from application.payment import base


class CashPayment(base.Payment):
    """
    Cash payment.
    """

    @property
    def supported(self):
        return False
