#
# Copyright (c) 2020 FTI-CAS
#

from application import app
from application.base import errors
from application.managers import base as base_mgr
from application import models as md

LOG = app.logger

ADMIN_ROLES = (md.UserRole.ADMIN, md.UserRole.ADMIN_SALE, md.UserRole.ADMIN_IT)
GET_ROLES = ()
LIST_ROLES = ()
CREATE_ROLES = ADMIN_ROLES
UPDATE_ROLES = ADMIN_ROLES
DELETE_ROLES = ADMIN_ROLES


def get_promotion(ctx):
    """
    Get promotion.
    :param ctx: sample ctx data:
        {
            'promotion': <promotion object>,
            'promotion_id': <promotion id if promotion object is not passed>,
            'fields': <fields to get as a list of str>,
        }
    :return:
    """
    data = ctx.data
    promotion = md.load_promotion(data.get('promotion') or data['promotion_id'])
    if not promotion:
        ctx.set_error(errors.PROMOTION_NOT_FOUND, status=404)
        return

    # Everyone can get promotion info

    base_mgr.dump_object(ctx, object=promotion)
    return promotion


def get_promotions(ctx):
    """
    Get multiple promotions.
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
    return base_mgr.dump_objects(ctx, model_class=md.Promotion, roles_required=LIST_ROLES)


def create_promotion(ctx):
    """
    Create promotion.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def update_promotion(ctx):
    """
    Update promotion.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def delete_promotion(ctx):
    """
    Delete promotion.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def get_promotions_for_products(ctx):
    """
    Get all promotions for the products.
    :param ctx: ctx data sample:
        {
            'product_types': [list of product types, can be None],
            'product_ids': [list of product ids, can be None],
            'promotion_type': <promotion type, None to get all>,
        }
    :return:
    """
    data = ctx.data
    product_types = data.get('product_types')
    product_ids = data.get('product_ids')
    promotion_type = data.get('promotion_type')

    query_cond = {
        'status': md.PromotionStatus.ENABLED,
    }
    if promotion_type:
        query_cond['type'] = promotion_type

    promotion_data = []
    promotions = md.query(md.Promotion, **query_cond).all()
    for promo in promotions:
        if (promo.enabled or
                (product_types and promo.accept_product_type(product_types)) or
                (product_ids and promo.accept_product_id(product_ids))):
            promo_data = base_mgr.dump_object(ctx, object=promo)
            if ctx.failed:
                return
            promotion_data.append(promo_data)

    ctx.response = {
        'promotions': promotion_data,
    }
    return ctx.response
