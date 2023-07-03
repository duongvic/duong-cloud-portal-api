#
# Copyright (c) 2020 FTI-CAS
#

import urlquote

from flask import request

from application import app
from application.base import errors
from application import models as md
from application.payment import base
from application.utils import date_util, hash_util, request_util

LOG = app.logger

LOCALES = {
    'vi': 'vn',
    'en': 'en'
}

IPN_REQUEST_ARGS = [
    'vnp_Amount',
    'vnp_BankCode',
    'vnp_BankTranNo',
    'vnp_CardType',
    'vnp_OrderInfo',
    'vnp_PayDate',
    'vnp_ResponseCode',
    'vnp_TmnCode',
    'vnp_TransactionNo',
    'vnp_TxnRef',
    'vnp_SecureHashType',
    'vnp_SecureHash',
]


class VNPayPayment(base.Payment):
    """
    VNPay payment.
    """

    @property
    def supported(self):
        return True

    @property
    def supported_currencies(self):
        return ('VND',)

    def to_payment_amount(self, amount, currency):
        """
        Convert an amount to the payment equivalent value.
        :param amount:
        :param currency:
        :return:
        """
        return amount * 100, currency

    def from_payment_amount(self, amount, currency):
        """
        Convert an amount of the payment to our value.
        :param amount:
        :param currency:
        :return:
        """
        return amount / 100, currency

    def start_payment(self, ctx, order):
        """
        Start payment process for an order.
        :param ctx:
        :param order:
        :return:
        """
        config = app.config['PAYMENT_VNPAY']
        order_info = '{0} order #{1}'.format(app.config['SERVICE_NAME'], order.id)
        order_type = 'billpayment'
        command = 'pay'
        currency = str(order.currency).upper()
        if currency not in self.supported_currencies:
            ctx.set_error(errors.PAYMENT_CURRENCY_NOT_SUPPORTED, status=406)
            return

        payment_info = {
            'vnp_Version': config['version'],
            'vnp_Command': command,
            'vnp_TmnCode': config['tmn_code'],
            'vnp_Amount': self.to_payment_amount(order.price_paid, currency),
            'vnp_CurrCode': currency,
            'vnp_TxnRef': str(order.id),
            'vnp_OrderInfo': order_info,
            'vnp_OrderType': order_type,
            'vnp_Locale': LOCALES[ctx.target_user.language or 'vi'],
            'vnp_CreateDate': date_util.format(date_util.utc_now(), format='%Y%m%d%H%M%S'),
            'vnp_IpAddr': request_util.get_client_ip(request),
            'vnp_ReturnUrl': config['return_url'],
        }
        # Response
        ctx.response = {
            'url': self._get_payment_url(config=config, payment_info=payment_info),
            'action': 'redirect',
        }

    def finish_payment(self, ctx, order):
        """
        Finish payment process for an order.
        :param ctx:
        :param order:
        :return:
        """
        config = app.config['PAYMENT_VNPAY']
        data = ctx.data
        payment_info = data['payment_info']
        response_code = payment_info['vnp_ResponseCode']

        def _set_response(code, msg):
            ctx.response = {
                'RspCode': code,
                'Message': msg
            }

        # Order already completed
        if order.status == md.OrderStatus.COMPLETED:
            _set_response(code='02', msg='Order Already Update')
            return

        # Not success
        if str(response_code) != '00':
            _set_response(code='00', msg='Confirm Success')
            return

        # Secure hash invalid
        if not self._verify_secure_hash(config=config, payment_info=payment_info):
            _set_response(code='97', msg='Invalid Signature')
            return

        # Success
        _set_response(code='00', msg='Confirm Success')

    def verify_payment(self, ctx, order):
        """
        Verify a payment for validity.
        :param ctx:
        :param order:
        :return:
        """
        config = app.config['PAYMENT_VNPAY']
        data = ctx.data
        payment_info = data['payment_info']
        if not self._verify_secure_hash(config=config, payment_info=payment_info):
            ctx.set_error(errors.PAYMENT_SECURE_CODE_INVALID, status=406)
            return

    def _get_payment_url(self, config, payment_info):
        """
        Construct payment url for the data.
        :param config:
        :param payment_info:
        :return:
        """
        payment_url = config['payment_url']

        query_string = ''
        for key, val in payment_info.items():
            if query_string:
                query_string += '&'
            query_string += '='.join([key, urlquote.quote(val).decode()])

        secure_hash = self._calc_secure_hash(config=config, payment_info=payment_info)
        payment_url += "?" + query_string + '&vnp_SecureHashType=SHA256&vnp_SecureHash=' + secure_hash
        LOG.debug('VNPAY_PAYMENT_URL: ' + payment_url)
        return payment_url

    def _calc_secure_hash(self, config, payment_info):
        """
        Calculate secure hash for the payment.
        :param config:
        :param payment_info:
        :return:
        """
        hashing_fields = sorted(payment_info.keys())
        hashing_exclude = ['vnp_SecureHashType', 'vnp_SecureHash']

        hash_data = ''
        for field in hashing_fields:
            if field in hashing_exclude:
                continue
            if hash_data:
                hash_data += '&'
            hash_data += str(field) + '=' + str(payment_info[field])

        hash_data = config['secret_key'] + hash_data
        return hash_util.hash_as_hex(hash_data.encode('utf-8'), method='sha256')

    def _verify_secure_hash(self, config, payment_info):
        """
        Verify if the secure hash is matching with the generated value.
        :param config:
        :param payment_info:
        :return:
        """
        secure_hash = payment_info['vnp_SecureHash']
        secure_hash_type = payment_info['vnp_SecureHashType']
        gen_hash_value = self._calc_secure_hash(config=config, payment_info=payment_info)
        return secure_hash_type.lower() == 'sha256' and gen_hash_value == secure_hash
