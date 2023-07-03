#
# Copyright (c) 2020 FTI-CAS
#

from application import app
from application.base import errors, common
from application.managers import base as base_mgr, product_mgr, user_mgr
from application import models as md
from application import payment
from application import product_types
from application.utils import data_util, date_util, mail_util

LOG = app.logger

ADMIN_ROLES = (md.UserRole.ADMIN, md.UserRole.ADMIN_SALE, md.UserRole.ADMIN_IT)
GET_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
LIST_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
CREATE_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
UPDATE_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
DELETE_ROLES = (md.UserRole.USER,) + ADMIN_ROLES

APPROVE_ORDER_ROLES = (md.UserRole.ADMIN, md.UserRole.ADMIN_SALE)
COMPLETE_ORDER_ROLES = (md.UserRole.ADMIN, md.UserRole.ADMIN_IT)


def get_order(ctx):
    """
    Get order.
    :param ctx: sample ctx data:
        {
            'order': <order object>,
            'order_id': <order id if order object is not passed>,
            'fields': <fields to get as a list of str>,
            'extra_fields': <extra fields to get as a list of str>,
        }
    :return:
    """
    data = ctx.data
    order = data.get('order') or data.get('order_id')
    if order:
        order = md.load_order(order)
        if not order:
            ctx.set_error(errors.ORDER_NOT_FOUND, status=404)
            return
    else:
        order = md.load_order_group(data.get('order_group') or data['order_group_id'])
        if not order:
            ctx.set_error(errors.ORDER_GROUP_NOT_FOUND, status=404)
            return

    if ctx.request_user.id != order.user_id:
        ctx.target_user = order.user
    if not user_mgr.check_user(ctx, roles=GET_ROLES):
        return

    base_mgr.dump_object(ctx, object=order)
    return order


def get_orders(ctx):
    """
    Get multiple orders.
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
    admin_roles = md.UserRole.admin_roles_of(LIST_ROLES)

    # Admin can get orders of a specific user or all users
    if ctx.check_request_user_role(admin_roles):
        user_id = ctx.data.get('user_id')
        override_condition = {'user_id': user_id} if user_id else None
    else:
        # User can only get his orders
        override_condition = {'user_id': ctx.target_user.id}

    return base_mgr.dump_objects(ctx,
                                 model_class=md.Order,
                                 override_condition=override_condition)


def create_order(ctx):
    """
    Create order.
    :param ctx: sample ctx data:
        {
            "groups": [
                // For creating an order group
            ],
            "type": "TRIAL/BUY",
            "code": "XXX",   # Admin only
            "status": "XXX",  # Admin only
            "payment_type": "AUTO",
            "currency": "VND",
            "region_id": "VN_HN",
            "notes": "order notes",
            "products": [
                {
                    "product_id": <COMPUTE product>,
                    "data": { custom cpu/mem/disk },
                },
                {
                    "product_id": <OS product>
                }
            ],
            "amount": 2,
            "duration": "3 months",
            "settings": {
                "auto_create_compute": true/false,
            }
        }
    :return:
    """
    if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
        return
    if not can_create_order(ctx):
        return
    user = ctx.target_user

    # To prevent race condition, acquire a lock in DB
    @base_mgr.with_lock(ctx, id='user:{}:create_order'.format(user.id), timeout=5)
    def _create_order():
        data = ctx.data
        is_admin = data['is_admin']
        groups = data.get('groups')
        price_total = 0
        price_paid_total = 0

        # Create order group object if item count larger than 1
        if groups and len(groups) > 1:
            is_group = True
            order_grp = md.OrderGroup()
            order_grp.code = data.get('code')
            order_grp.user_id = user.id
            order_grp.notes = data.get('notes') or None
            order_grp.create_date = date_util.utc_now()
        else:
            order_grp = None
            groups = groups or [data]
            is_group = False

        all_objects = []
        orders = []
        for item in groups:
            order = md.Order()
            order.group = order_grp
            order.user_id = user.id
            order.type = item.get('type') or md.OrderType.BUY
            order.name = item.get('name') or None
            order.create_date = date_util.utc_now()
            order.status = md.OrderStatus.CREATED
            order.promotion_id = item.get('promotion_id')
            order.discount_code = item.get('discount_code')
            order.amount = int(item.get('amount') or 1)
            order.duration = item['duration']
            order.payment_type = item.get('payment_type')
            order.currency = item.get('currency')
            order.region_id = item['region_id']
            order.data = {
                'settings': item.get('settings'),
            }
            order.notes = item.get('notes')
            orders.append(order)

            order_products = []
            for prod_item in item['products']:
                order_prod = md.OrderProduct()
                order_prod.order = order
                order_prod.product_id = prod_item['product_id']
                order_prod.data = prod_item.get('data')
                all_objects.append(order_prod)
                order_products.append(order_prod)

            item_ctx = ctx.copy(task='process order')
            _process_order(item_ctx,
                           order=order,
                           group_orders=orders,
                           order_products=order_products)
            if item_ctx.failed:
                ctx.copy_error(item_ctx)
                return

            if is_admin:
                # Set status
                status = item.get('status')
                if status:
                    _update_order_status(ctx, order, status)
                    if ctx.failed:
                        return

                if 'code' in item:
                    order.code = item['code']
                if 'price' in item:
                    order.price = item['price']
                if 'price_paid' in item:
                    order.price_paid = item['price_paid']

            # If order price_paid is ZERO, complete it now
            if order.price_paid == 0:
                order.payment_type = None  # No payment required
                if not is_admin:
                    order.status = md.OrderStatus.COMPLETED

            price_total += order.price
            price_paid_total += order.price_paid

        # Save objects to DB
        error = md.save_new(all_objects)
        if error:
            ctx.set_error(error, status=500)
            return

        order_1st = orders[0]

        # Update order code if not yet set
        if not order_1st.code:
            code = 'DH%06d' % order_1st.id
            for order in orders:
                order.code = code
            if order_grp:
                order_grp.code = code
            error = md.save()
            if error:
                ctx.set_error(error, status=500)
                return

        # Start payment process if needs to
        payment_type = order_1st.payment_type
        need_payment = False
        for order in orders:
            if order.status == md.OrderStatus.CREATED:
                need_payment = True
                break

        if payment_type and need_payment:
            payment_gate = payment.get_payment(ctx, payment_type=payment_type)
            if ctx.failed:
                return
            payment_gate.start_payment(ctx, order=order_grp if order_grp else order_1st)
            if ctx.failed:
                return

        # Return the order data to user
        if order_grp:
            ctx.data = {
                'order_group': order_grp,
                'extra_fields': ['orders'],
            }
            get_order(ctx)
            return order_grp
        else:
            ctx.data = {
                'order': order_1st,
            }
            get_order(ctx)
            return order_1st

    # Execute the function
    return _create_order()


def _update_order_status(ctx, order, status):
    """
    Update order status.
    :param ctx:
    :param order:
    :param status:
    :return:
    """
    curr_status = order.status
    if curr_status == status:
        return

    data = ctx.data
    is_admin = data['is_admin']

    if is_admin:
        # status is to COMPLETE order
        if status == md.OrderStatus.COMPLETED:
            if curr_status not in (md.OrderStatus.APPROVED,):
                e = ValueError('Order in status {} cannot move to status {}.'
                               .format(curr_status, status))
                LOG.error(e)
                ctx.set_error(errors.USER_ACTION_NOT_ALLOWED, cause=e, status=403)
                return

            # User doesn't have required role
            if not ctx.check_request_user_role(COMPLETE_ORDER_ROLES):
                e = ValueError('Role {} is not allowed to COMPLETE order.'.format(ctx.request_user.role))
                LOG.error(e)
                ctx.set_error(errors.USER_ACTION_NOT_ALLOWED, cause=e, status=403)
                return

        # status is to APPROVE order
        elif status == md.OrderStatus.APPROVED:
            if curr_status not in (None, md.OrderStatus.CREATED, md.OrderStatus.PENDING):
                e = ValueError('Order in status {} cannot move to status {}.'
                               .format(curr_status, status))
                LOG.error(e)
                ctx.set_error(errors.USER_ACTION_NOT_ALLOWED, cause=e, status=403)
                return

            # User doesn't have required role
            if not ctx.check_request_user_role(APPROVE_ORDER_ROLES):
                e = ValueError('Role {} is not allowed to APPROVE order.'.format(ctx.request_user.role))
                LOG.error(e)
                ctx.set_error(errors.USER_ACTION_NOT_ALLOWED, cause=e, status=403)
                return

        order.status = status

    else:  # USER mode
        # Order is not update-able
        if order.status not in (md.OrderStatus.CREATED, md.OrderStatus.PENDING,
                                md.OrderStatus.FAILED):
            ctx.set_error(errors.ORDER_ALREADY_FINISHED, status=406)
            return

        # User cancels order
        if status == md.OrderStatus.CANCELLED:
            order.status = status

        else:
            ctx.set_error(errors.ORDER_STATUS_INVALID, status=406)
            return


def can_create_order(ctx):
    """
    Check if user can create an order.
    :param ctx:
    :return:
    """
    user = ctx.target_user
    data = ctx.data
    admin_roles = md.UserRole.admin_roles_of(CREATE_ROLES)
    is_admin = ctx.check_request_user_role(admin_roles)
    data['is_admin'] = is_admin

    groups = data.get('groups')
    if groups and len(groups) > 1:
        is_group = True
    else:
        is_group = False
        groups = groups or [data]

    # User has too much orders in queue
    unfinished_count = md.query(md.Order,
                                user_id=user.id,
                                status=md.OrderStatus.CREATED).count()
    if not is_admin and unfinished_count > 3:
        ctx.set_error(errors.ORDER_CREATED_TOO_MANY, status=403)
        return

    order_type = None
    payment_type = None
    currency = None

    for item in groups:
        # Validate order type
        _order_type = item.get('type') or md.OrderType.BUY
        if not md.OrderType.is_valid(_order_type):
            e = ValueError('Order type {} invalid.'.format(_order_type))
            LOG.error(e)
            ctx.set_error(errors.ORDER_TYPE_INVALID, cause=e, status=406)
            return
        if order_type and order_type != _order_type:
            e = ValueError('One order does not support multiple order types.')
            LOG.error(e)
            ctx.set_error(errors.ORDER_TYPE_INVALID, cause=e, status=406)
            return
        order_type = _order_type

        # Validate currency
        _currency = item['currency']
        if _currency not in app.config['PAYMENT_CURRENCIES']:
            e = ValueError('Currency {} invalid.'.format(_currency))
            LOG.error(e)
            ctx.set_error(errors.PAYMENT_CURRENCY_INVALID, cause=e, status=406)
            return
        if currency and currency != _currency:
            e = ValueError('One order does not support multiple currencies.')
            LOG.error(e)
            ctx.set_error(errors.PAYMENT_CURRENCY_INVALID, cause=e, status=406)
            return
        currency = _currency

        # Validate payment type
        _payment_type = item.get('payment_type') or None
        _payment_type = app.config['PAYMENT_TYPE'] if str(_payment_type).upper() == 'AUTO' else _payment_type
        if _payment_type:
            payment.get_payment(ctx, payment_type=_payment_type)
            if ctx.failed:
                return
        if payment_type and payment_type != _payment_type:
            e = ValueError('One order does not support multiple payment types.')
            LOG.error(e)
            ctx.set_error(errors.PAYMENT_TYPE_INVALID, cause=e, status=406)
            return
        payment_type = _payment_type

        # Validate region
        region_id = item.get('region_id')
        if not md.RegionId.is_valid(region_id):
            e = ValueError('Region {} invalid.'.format(region_id))
            LOG.error(e)
            ctx.set_error(errors.REGION_NOT_FOUND, cause=e, status=404)
            return

        item['type'] = order_type
        item['currency'] = currency
        item['payment_type'] = payment_type
        item['region_id'] = region_id

    return True


def update_order(ctx):
    """
    Update order.
    :param ctx:
    :return:
    """
    data = ctx.data
    order = md.load_order(data.get('order') or data['order_id'])
    if not order:
        ctx.set_error(errors.ORDER_NOT_FOUND, status=404)
        return

    user = order.user
    ctx.target_user = user
    if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
        return

    admin_roles = md.UserRole.admin_roles_of(UPDATE_ROLES)
    is_admin = ctx.check_request_user_role(admin_roles)
    data['is_admin'] = is_admin

    status = data.get('status')
    # Do not update DELETED here, call delete_order() instead
    if status == md.OrderStatus.DELETED:
        ctx.set_error(errors.ORDER_STATUS_INVALID, status=406)
        return
    elif status:
        _update_order_status(ctx, order, status)
        if ctx.failed:
            return

    # Updates order notes
    if 'notes' in data:
        order.notes = data['notes']

    # Fields updated by ADMIN
    if is_admin:
        if 'type' in data:
            order.type = data['type']
        if 'code' in data:
            order.code = data['code']
        if 'payment_type' in data:
            order.payment_type = data['payment_type']
        if 'price' in data:
            order.price = data['price']
        if 'price_paid' in data:
            order.price_paid = data['price_paid']
        if 'notes' in data:
            order.notes = data['notes']

        if 'amount' in data:
            order.amount = data['amount']
        if 'duration' in data:
            order.duration = data['duration']
        if 'start_date' in data:
            order.start_date = date_util.parse(data['start_date'], common.DATE_TIME_FORMAT)

        # Copy order item data to override
        if not order.data:
            order.data = {}
        upd_data = {}
        for field in md.Order.__data_fields__:
            if field in data:
                upd_data[field] = data[field]
        data_util.merge_dicts(order.data, upd_data, create_new=False, deep=True)
        order.flag_modified('data')

    # Save objects in DB
    error = md.save(order)
    if error:
        ctx.set_error(error, status=500)
        return


def delete_order(ctx):
    """
    Delete order.
    :param ctx:
    :return:
    """
    data = ctx.data
    order = md.load_order(data.get('order') or data['order_id'])
    if not order:
        ctx.set_error(errors.ORDER_NOT_FOUND, status=404)
        return

    user = order.user
    ctx.target_user = user
    if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
        return

    admin_roles = md.UserRole.admin_roles_of(DELETE_ROLES)
    is_admin = ctx.check_request_user_role(admin_roles)
    data['is_admin'] = is_admin

    curr_status = order.status
    if not is_admin:
        # Order is not deletable
        if curr_status not in (md.OrderStatus.CREATED, md.OrderStatus.PENDING,
                               md.OrderStatus.FAILED):
            ctx.set_error(errors.ORDER_ALREADY_FINISHED, status=406)
            return

    # Already deleted
    if curr_status == md.OrderStatus.DELETED:
        return

    # Change status to DELETED
    order.status = md.OrderStatus.DELETED

    # Save object in DB
    error = md.save(order)
    if error:
        ctx.set_error(error, status=500)
        return


def finish_order(ctx):
    """
    Complete an order.
    :param ctx:
    :return:
    """
    data = ctx.data
    order = md.load_order_group(data.get('order') or data['order_id'])
    if not order:
        ctx.set_error(errors.ORDER_GROUP_NOT_FOUND, status=404)
        return

    ignore_if_completed = data.get('ignore_if_completed')
    if order.status != md.OrderStatus.CREATED:
        if not ignore_if_completed:
            ctx.set_error(errors.ORDER_ALREADY_FINISHED, status=406)
        return

    user = order.user
    ctx.target_user = user
    ctx.request_user = ctx.request_user or user
    if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
        return

    payment_type = data['payment_type']
    payment_info = data['payment_info']

    # Get payment gate
    payment_gate = payment.get_payment(ctx, payment_type=payment_type)
    if ctx.failed:
        return

    # Finish payment
    payment_gate.finish_payment(ctx, order=order)
    if ctx.failed:
        return

    # Complete order
    if order.status != md.OrderStatus.COMPLETED:
        order.status = md.OrderStatus.COMPLETED
        if not order.extra:
            order.extra = {}
        order.extra.update({'payment_info': payment_info})

        # Save order to DB
        error = md.save(order)

        # NOTE: in case order has failed to complete
        # This situation should not happen!
        # Send an e-mail to ADMIN to report the issue?
        if error:
            ctx.set_error(error, status=500)
            try:
                issue = ctx.error.get_message()
                mail_util.send_mail_order_issue(user=user, order=order, issue=issue)
            except BaseException as e:
                LOG.error(e)
            return

        # Send notification e-mail to user
        try:
            mail_util.send_mail_order_complete(user=user, order=order)
        except BaseException as e:
            LOG.error(e)
            # NOTE: We consider this is not an error, simply ignore it
            return


def repay_order(ctx):
    """
    Retry an order if it has failed the payment.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def refund_order(ctx):
    """
    Refund an order.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def renew_order(ctx):
    """
    Renew an order.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def get_order_utilization(ctx):
    """
    Get utilization info of order or order item.
    :param ctx:
    :return: for order input, returns:
        {
            'order_id': <order id>,
            'total_count': <total count>,
            'used_count': <count of uses>,
            'available_count': <count of available uses>,
        }
        For order group input, returns:
        {
            'orders': [
                {
                    <use info of order like above>
                },
                ...
            ]
        }
    """
    data = ctx.data
    order = data.get('order') or data.get('order_id')
    order = md.load_order(order) if order else None
    if order:
        ctx.response = order.utilization
        if ctx.failed:
            return
        return ctx.response

    order_group = data.get('order_group') or data.get('order_group_id')
    order_group = md.load_order_group(order_group) if order_group else None
    if order_group:
        ctx.response = response = {}
        response['orders'] = orders = []
        for order in order_group.orders:
            resp = order.utilization
            if ctx.failed:
                return
            resp['order_id'] = order.id
            orders.append(resp)
        return response

    ctx.set_error(errors.ORDER_NOT_FOUND, status=404)
    return


def _process_order(ctx, order, group_orders, order_products):
    """
    Process an order item.
    :param ctx:
    :param order:
    :param group_orders:
    :param order_products:
    :return:
    """
    # Load all products for faster performance
    all_prod_ids = set([op.product_id for op in order_products])
    all_prods = md.query(md.Product, md.Product.id.in_(all_prod_ids)).all()
    product_map = {prod.id: prod for prod in all_prods}
    order_prod_type = None

    # Check products availability
    for order_product in order_products:
        product = product_map.get(order_product.product_id)
        if product is None:
            e = ValueError('Product id {} not found.'.format(order_product.product_id))
            LOG.error(e)
            ctx.set_error(errors.PRODUCT_NOT_FOUND, cause=e, status=404)
            return
        if product.status != md.ProductStatus.ENABLED:
            e = ValueError('Product id {} not enabled.'.format(order_product.product_id))
            LOG.error(e)
            ctx.set_error(errors.PRODUCT_NOT_ENABLED, cause=e, status=406)
            return

        # If only one product in the item, then order type is product type
        if len(order_products) == 1:
            order_prod_type = product.type
        else:
            if product.type == md.ProductType.COMPUTE:
                # If there is a COMPUTE product in the item,
                # then the type of the order is COMPUTE.
                order_prod_type = md.ProductType.COMPUTE

    # Failed to detect order product type
    if not order_prod_type:
        ctx.set_error(errors.ORDER_PRODUCT_TYPE_NOT_FOUND, status=404)
        return

    # Product type of the order
    order.type = order.type or md.OrderType.BUY
    order.product_type = order_prod_type

    # If order is for TRIAL mode, find the TRIAL promotion
    promotion = None
    if not order.promotion_id and order.type == md.OrderType.TRIAL:
        promotion = _find_trial_promotion(ctx, order=order, products=all_prods)
        if ctx.failed:
            return
        order.promotion_id = promotion.id

    # Load promotion
    if not promotion and order.promotion_id:
        promotion = md.load_promotion(order.promotion_id)

    if promotion:
        # If promotion is TRIAL
        if promotion.type == md.PromotionType.TRIAL:
            order.type = md.OrderType.TRIAL
        # Validate the promotion
        _validate_promotion(ctx, order=order, group_orders=group_orders,
                            promotion=promotion)
        if ctx.failed:
            if order.type == md.OrderType.TRIAL:
                return
            else:
                # Remove the promotion and continue
                order.promotion = promotion = None
                order.discount_code = None

    # Calculate order price
    _calc_order_price(ctx, order=order,
                      order_products=order_products,
                      promotion=promotion)


def _calc_order_price(ctx, order, order_products, promotion):
    """
    Calculate order price.
    :param ctx:
    :param order:
    :param order_products:
    :param promotion:
    :return:
    """
    price_ctx = ctx.copy(task='get product price')
    price_ctx.data = {
        'products': [],
        'amount': order.amount,
        'duration': order.duration,
        'currency': order.currency,
    }
    if promotion:
        price_ctx.data.update({
            'promotion': promotion,
            'discount_code': order.discount_code,
        })
    for order_product in order_products:
        price_ctx.data['products'].append({
            'product_id': order_product.product_id,
            'data': order_product.data,
        })
    product_mgr.get_products_price(price_ctx)
    if price_ctx.failed:
        return

    resp = price_ctx.response
    order.price = order_price = resp['price']
    order.price_paid = order_price_paid = resp.get('price_deal', order_price)
    order.amount = resp['amount']
    order.duration = resp['duration']
    order.data['info'] = {}

    index = 0
    for order_product in order_products:
        product_result = resp['products'][index]
        order_product.price = product_result['price']
        order_product.price_paid = product_result.get('price_deal', order_product.price)

        order_product.data = {
            'info': product_result['info'],
        }
        data_util.merge_dicts(order.data['info'], product_result['info'],
                              create_new=False, deep=True)
        index += 1

    order.flag_modified('data')


def _validate_promotion(ctx, order, group_orders, promotion):
    """
    Validate promotion for the order.
    :param ctx:
    :param order:
    :param promotion:
    :return:
    """
    if not promotion.enabled:
        e = ValueError('Promotion id {} not enabled.'.format(promotion.id))
        LOG.error(e)
        ctx.set_error(errors.PROMOTION_NOT_ENABLED, cause=e, status=406)
        return

    promo_name = promotion.name
    base_name = promo_name.split('#')[0]

    user = ctx.target_user
    user_settings = promotion.user_settings or {}

    max_uses_per_user = user_settings.get('max_uses_per_user')
    max_uses_across_regions = user_settings.get('max_uses_across_regions')

    # Number of promotions for this kind must not exceed the max value
    if max_uses_per_user or max_uses_across_regions:
        # Number of uses in DB
        promo_count = 0
        for o in md.iterate(md.Order,
                            md.Order.status != md.OrderStatus.DELETED,
                            md.Order.user_id == user.id):
            if o.promotion_id == promotion.id:
                promo_count += 1
                continue

            if max_uses_across_regions and o.promotion_id:
                o_promo = o.promotion
                if o_promo.name == promotion.name:
                    promo_count += 1
                    continue

        # Number of uses in this order group (if there is)
        for o in group_orders:
            if o != order and o.promotion_id == promotion.id:
                promo_count += 1

        if (max_uses_per_user and promo_count >= max_uses_per_user) or \
                (max_uses_across_regions and promo_count >= max_uses_across_regions):
            e = ValueError('Promotion "{}" exceeds for user id "{}". Max uses allowed: {}.'
                           .format(promotion.name, user.id, max_uses_per_user))
            LOG.error(e)
            ctx.set_error(errors.PROMOTION_USE_EXCEEDED, cause=e, status=406)
            return


def _find_trial_promotion(ctx, order, products):
    """
    Find trial promotion for order and products.
    :param ctx:
    :param order:
    :param products:
    :return:
    """
    promo_list = []
    prod_types = [prod.type for prod in products]
    prod_ids = [prod.id for prod in products]
    for promo in md.iterate(md.Promotion,
                            type=md.PromotionType.TRIAL,
                            status=md.PromotionStatus.ENABLED,
                            region_id=order.region_id,
                            order_by=md.Promotion.create_date.desc()):
        if not promo.enabled:
            continue
        if not promo.accept_product_type(prod_types) or not promo.accept_product_id(prod_ids):
            continue
        promo_list.append(promo)

    if not promo_list:
        e = ValueError('TRIAL mode not found for order.')
        LOG.error(e)
        ctx.set_error(errors.PROMOTION_NOT_FOUND, cause=e, status=404)
        return

    if len(promo_list) > 1:
        LOG.warning('Found multiple promotions of TRIAL type.')

    promotion = promo_list[0]
    return promotion
