#
# Copyright (c) 2020 FTI-CAS
#

from application import app
from application.base import errors
from application import models as md
from application.utils import date_util

LOG = app.logger
DEBUG = app.config['ENV'] in ('dev', 'development', 'debug')

UNIT_KB = 1024
UNIT_MB = UNIT_KB * 1024
UNIT_GB = UNIT_MB * 1024


class ProductType(object):
    """
    Base product type class.
    """
    type = None

    @property
    def supported(self):
        return False

    def get_product_pricing(self, product, months):
        """
        Parse product pricing data if the product contains them.
        The product.pricing should contain below data:
            product.pricing = {
                'currency': <str>,
                'price': <price_monthly>,
                'price_by_month': {
                    '1m': 1 month price,
                    '3m': 3 month price,
                    '6m': 6 month price,
                    '12m': 12 month price,
                    '24m': 24 month price,
                    '36m': 36 month price,
                    '48m': 48 month price,
                }
            }
        :param product: product object
        :param months: months as integer
        :return: a dict such as:
            {
                'price': price_total,
                'price_monthly': price_monthly,
            }
        """
        pricing = product.pricing
        price_total = None
        price_monthly = None

        price_by_month = pricing.get('price_by_month')
        p_total = price_by_month.get(str(months) + 'm') if price_by_month else None
        if p_total:
            price_total = p_total
            price_monthly = price_total // months

        if price_total is None:
            price_monthly = pricing['price']
            price_total = price_monthly * months

        result = {
            'price': price_total,
            'price_monthly': price_monthly,
        }
        return result

    def get_price(self, ctx):
        """
        Get price for the product.
        :param ctx: sample ctx data:
            {
                'product': <product object>,
                'product_id': <product id if product is not passed>,
                'amount': <amount as integer>,
                'duration': <duration as string>,
                'currency': <currency as string>,
                'promotion': <promotion object>,
                'promotion_id': <promotion id if promotion is not passed>,
                'discount_code': <str>,
            }
        :return:
        """
        data = ctx.data
        product = md.load_product(data.get('product') or data['product_id'])
        if not product:
            ctx.set_error(errors.PRODUCT_NOT_FOUND, status=404)
            return

        if product.type != self.type:
            ctx.set_error(errors.PRODUCT_TYPE_INVALID, status=406)
            return

        self.do_get_price(ctx, product=product)
        if ctx.failed:
            return

        pricing = ctx.response

        # Try applying promotion if there is
        promotion = md.load_promotion(data.get('promotion') or data.get('promotion_id'))
        if not promotion:
            return pricing

        promo_ctx = ctx.copy(task='apply promotion')
        promo_ctx.data.update({
            'pricing': pricing,
            'product': product,
            'promotion': promotion,
        })
        self.apply_promotion(promo_ctx)
        if promo_ctx.failed:
            # Just return the current price
            return pricing
        if promo_ctx.warning:
            ctx.copy_warning(promo_ctx)

        ctx.response = promo_ctx.response
        return ctx.response

    def do_get_price(self, ctx, product):
        """
        Subclass should override this method.
        :param ctx:
        :param product:
        :return:
        """

    def validate_get_price(self, ctx, product):
        """
        Subclass should override this method.
        :param ctx:
        :param product:
        :return:
        """
        data = ctx.data
        currency = data['currency']
        amount = data['amount']
        duration = data['duration']

        if not isinstance(amount, int) or amount <= 0:
            ctx.set_error(errors.PRODUCT_AMOUNT_INVALID, status=406)
            return

        if currency.upper() not in app.config['PAYMENT_CURRENCIES']:
            ctx.set_error(errors.PAYMENT_CURRENCY_NOT_SUPPORTED, status=406)
            return

        try:
            dur_value, dur_unit = date_util.parse_duration(duration, target_unit='month')
        except BaseException as e:
            LOG.error(e)
            ctx.set_error(errors.ORDER_DURATION_INVALID, status=406)
            return

        return {
            'currency': currency,
            'amount': amount,
            'duration': {
                'value': dur_value,
                'unit': dur_unit,
            },
        }

    def apply_promotion(self, ctx):
        """
        Try apply promotion for product.
        :param ctx: sample ctx data:
            {
                'pricing': <product price without promotion>,
                'product': <product object>,
                'promotion': <promotion object>,
                'discount_code': <str>,
            }
        :return:
        """
        data = ctx.data
        product = data['product']
        promotion = data['promotion']
        if not promotion:
            ctx.set_error(errors.PROMOTION_NOT_FOUND, status=404)
            return

        if not promotion.accept_product_type(product.type):
            e = ValueError('Product {}/{} not acceptable for promotion "{}".'
                           .format(product.type, product.name, promotion.name))
            LOG.debug(e)
            ctx.set_error(errors.PROMOTION_PRODUCT_NOT_ACCEPTED, cause=e, status=406)
            return

        if not promotion.accept_product_id(product.id):
            e = ValueError('Product {}/{} not acceptable for promotion "{}".'
                           .format(product.type, product.name, promotion.name))
            LOG.debug(e)
            ctx.set_error(errors.PROMOTION_PRODUCT_NOT_ACCEPTED, cause=e, status=406)
            return

        return self.do_apply_promotion(ctx, promotion=promotion)

    def do_apply_promotion(self, ctx, promotion):
        """
        Subclass should override this method.
        :param ctx:
        :param promotion:
        :return:
        """

    def validate_promotion(self, ctx, promotion):
        """
        Validate promotion settings.
        :param ctx:
        :param promotion:
        :return:
        """

    def get_order_utilization(self, ctx, order):
        """
        Get utilization info of the order item.
        :param ctx:
        :param order:
        :return:
        """

    def on_order_changed(self, ctx, order):
        """
        Called when an order has changed.
        :param ctx:
        :param order:
        :return:
        """
