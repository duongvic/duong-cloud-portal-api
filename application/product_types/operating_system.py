#
# Copyright (c) 2020 FTI-CAS
#

from application import app
from application.base import errors
from application import models as md
from application.product_types import base
from application.utils import date_util

LOG = app.logger


class OSType(base.ProductType):
    """
    Operating System product type.
    """
    type = md.ProductType.OS

    @property
    def supported(self):
        return True

    def get_os_list(self, ctx):
        """
        Get OS names for type.
        :param ctx: sample ctx data:
            {
                'os_type': <optional, one of md.OSType values>,
                'region_id': <region_id>,
            }
        :return:
        """
        data = ctx.data
        all_os = md.query(md.Product,
                          type=self.type,
                          status=md.ProductStatus.ENABLED,
                          region_id=data['region_id']).all()
        os_type = data.get('os_type')
        filters = lambda x: not os_type or x.info['type'].upper() == os_type.upper()
        os_list = {prod.name: prod.info for prod in all_os if filters(prod)}
        ctx.response = os_list
        return os_list

    def do_get_price(self, ctx, product):
        """
        Override super class method.
        :param ctx:
        :param product:
        :return:
        """
        parsed_info = self.validate_get_price(ctx, product=product)
        if ctx.failed:
            return

        product_info = product.info
        currency = parsed_info['currency']
        amount = parsed_info['amount']
        duration = parsed_info['duration']
        duration_str = '{} {}'.format(duration['value'], duration['unit'])
        pricing = product.pricing

        ctx.response = {
            'id': product.id,
            'info': {
                'os_name': product.name,
                'os_type': product_info['type'],
                'os_arch': product_info.get('arch') or 'x86_64',
                'os_distro': product_info.get('distro'),
            },
            'price': pricing['price'],  # Lifetime license
            'price_monthly': None,  # No monthly price for lifetime OS license
            'currency': currency,
            'amount': amount,
            'duration': duration_str,
            'promotion_type': None,
        }
        return ctx.response

    def do_apply_promotion(self, ctx, promotion):
        """
        Override super class method.
        :param ctx:
        :param promotion:
        :return:
        """
        self.validate_promotion(ctx, promotion=promotion)
        if ctx.failed:
            return

        data = ctx.data
        pricing = data['pricing']
        promo_settings = promotion.settings

        # TRIAL mode
        if promotion.type == md.PromotionType.TRIAL:
            pricing['promotion_type'] = md.PromotionType.TRIAL
            pricing['price_deal'] = 0
            if 'amount' in promo_settings:
                pricing['amount'] = promo_settings['amount']
            if 'duration' in promo_settings:
                pricing['duration'] = promo_settings['duration']

            info = pricing['info']
            info['trial_info'] = dict(info)

        # DISCOUNT mode
        if promotion.type == md.PromotionType.DISCOUNT:
            pricing['promotion_type'] = md.PromotionType.DISCOUNT
            pricing['discount_code'] = data.get('discount_code')

            discount_rate = promo_settings['discount_rate']
            pricing['price_deal'] = int(pricing['price'] * (1.0 - discount_rate))
            if pricing.get('price_monthly') is not None:
                pricing['price_monthly'] = int(pricing['price_monthly'] * (1.0 - discount_rate))

        ctx.response = pricing
        return pricing

    def validate_promotion(self, ctx, promotion):
        """
        Override super class method.
        :param ctx:
        :param promotion:
        :return:
        """
        parsed_info = super().validate_promotion(ctx, promotion=promotion)
        if ctx.failed:
            return

        # TODO

    def get_order_utilization(self, ctx, order):
        """
        Get utilization info of the referenced order item.
        :param ctx:
        :param order:
        :return:
        """
        data = ctx.data
        order = order or md.load_order(data.get('order') or data.get('order_id'))
        if order:
            total_count = order.amount
            ctx.response = {
                'used_count': None,
                'available_count': total_count,
                'total_count': total_count,
            }
            return ctx.response

        ctx.set_error(errors.ORDER_GROUP_NOT_FOUND, status=404)
        return

    def on_order_changed(self, ctx, order):
        """
        Called when an order item has changed.
        :param ctx:
        :param order:
        :return:
        """
