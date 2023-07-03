#
# Copyright (c) 2020 FTI-CAS
#

from application.payment import base


class BankTransferPayment(base.Payment):
    """
    Bank transfer payment.
    """

    @property
    def supported(self):
        return False
