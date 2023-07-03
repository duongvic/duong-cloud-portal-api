#
# Copyright (c) 2020 FTI-CAS
#

from application import app
from application.base import errors
from application.managers import base as base_mgr, user_mgr
from application import models as md
from application import product_types
from application.utils import date_util

LOG = app.logger

ADMIN_ROLES = (md.UserRole.ADMIN, md.UserRole.ADMIN_SALE, md.UserRole.ADMIN_IT)
GET_ROLES = ()
LIST_ROLES = ()
CREATE_ROLES = (md.UserRole.ADMIN,)
UPDATE_ROLES = (md.UserRole.ADMIN,)
DELETE_ROLES = (md.UserRole.ADMIN,)


def get_product(ctx):
    """
    Get product attributes.
    :param ctx: sample ctx data:
        {
            'product': <product object>,
            'product_id': <product id if product object is not passed>,
            'fields': <fields to get as a list of str>,
        }
    :return:
    """
    data = ctx.data
    product = md.load_product(data.get('product') or data['product_id'])
    if not product:
        ctx.set_error(errors.PRODUCT_NOT_FOUND, status=404)
        return

    # Everyone can get product info

    base_mgr.dump_object(ctx, object=product)
    return product


def get_products(ctx):
    """
    Get multiple products.
    :param ctx: sample ctx data:
        {
            'page': <page index starts from 0>,
            'page_size': <page size>,
            'sort_by': <attr to sort by>,
            'fields': <attrs to get as a list of str>,
            'condition': <reserved, custom query>,
        }
    :return:
    """
    return base_mgr.dump_objects(ctx, model_class=md.Product, roles_required=LIST_ROLES)


def create_product(ctx):
    """
    Create product.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def update_product(ctx):
    """
    Update product.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def delete_product(ctx):
    """
    Delete product.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def get_product_price(ctx):
    """
    Get product price.
    :param ctx: sample ctx data:
        {
            'product': <product object>,
            'product_id': <product id if product object is not passed>,
            'amount': <int>,
            'duration': <str>,
            'currency': <str>,
            'data': <dict>,
            'promotion': <promotion object>,
            'promotion_id': <promotion id if promotion object is not passed>,
            'discount_code': <str>,
        }

        Custom data should contain such below info:
        {
            'cpu': <cpu>,
            'mem': <mem>,
            'disk': <disk>,
            'snapshot_size_max': <snapshot_size_max>,
            'backup_size_max': <backup_size_max>,
        }
    :return:
    """
    data = ctx.data
    product = md.load_product(data.get('product') or data['product_id'])
    if not product:
        ctx.set_error(errors.PRODUCT_NOT_FOUND, status=404)
        return

    if not product.enabled:
        ctx.set_error(errors.PRODUCT_NOT_ENABLED, status=406)
        return

    # Get product type
    product_type = product_types.get_product_type(ctx, product_type=product.type)
    if ctx.failed:
        return

    data['product'] = product
    return product_type.get_price(ctx)


def get_products_price(ctx):
    """
    Get multiple products price.
    :param ctx: sample ctx data:
        {
            'products': [
                {
                    'product': <product object>,
                    'product_id': <product id if product object is not passed>,
                    'data': <dict>,
                },
                {
                    <<ANOTHER PRODUCT>>
                },
            ],
            'amount': <int>,
            'duration': <str>,
            'currency': <str>,
            'promotion': <promotion object>,
            'promotion_id': <promotion id if promotion object is not passed>,
            'discount_code': <str>,
        }

        Custom data should contain such below info:
        {
            'cpu': <cpu>,
            'mem': <mem>,
            'disk': <disk>,
            'snapshot_size_max': <snapshot_size_max>,
            'backup_size_max': <backup_size_max>,
        }
    :return:
    """
    data = ctx.data
    products = data['products']
    amount = data['amount']
    duration = data['duration']
    currency = data['currency']
    promotion = md.load_promotion(data.get('promotion') or data.get('promotion_id'))
    discount_code = data.get('discount_code')

    products_result = []
    price_total = 0
    price_deal = 0
    promotion_type = None
    amount_actual = None
    duration_actual = None

    for product in products:
        item_ctx = ctx.copy(task='get product price',
                            data=dict(product))
        item_ctx.data.update({
            'amount': amount,
            'duration': duration,
            'currency': currency,
            'promotion': promotion,
            'discount_code': discount_code,
        })
        resp = get_product_price(item_ctx)
        if item_ctx.failed:
            ctx.copy_error(item_ctx)
            return
        if item_ctx.warning:
            ctx.copy_warning(item_ctx)

        products_result.append(resp)
        price = resp['price']
        price_total += price
        price_deal += resp.get('price_deal', price)
        promotion_type = resp.get('promotion_type')
        amount_actual = resp['amount']
        duration_actual = resp['duration']

    duration_val = date_util.parse_duration(duration, target_unit='month')
    price_monthly = price_deal / duration_val[0]

    # Specific process on VND (rounds the prices)
    if currency.upper() == 'VND':
        round_step = 1000
        price_total = int(price_total)
        price_total = (price_total // round_step) * round_step
        price_deal = int(price_deal)
        price_deal = (price_deal // round_step) * round_step
        price_monthly = int(price_monthly)
        price_monthly = (price_monthly // round_step) * round_step

    result = {
        'price': price_total,
        'price_monthly': price_monthly,
        'amount': amount_actual,
        'duration': duration_actual,
        'currency': currency,
        'products': products_result,
    }
    if promotion:
        result.update({
            'price_deal': price_deal,
            'promotion_type': promotion_type,
            'discount_code': discount_code,
        })

    ctx.response = result
    return result
