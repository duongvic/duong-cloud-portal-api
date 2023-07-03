#
# Copyright (c) 2020 FTI-CAS
#

from application.base.context import errors

from .models import *
from .types import *


def get_session():
    return db.session


def load(model_class, id):
    """
    Load model by id.
    :param model_class:
    :param id:
    :return:
    """
    return model_class.query.get(id)


def query(model_class, *args, order_by=None, **kwargs):
    """
    Create query for model class. E.g.
        products = query(md.Product, order_by=md.Product.create_date.desc(),
                         type=<product type>, status='ENABLED').all()
    :param model_class:
    :param args:
    :param order_by:
    :param kwargs:
    :return:
    """
    qry = model_class.query
    for cond in args:
        qry = qry.filter(cond)
    for k, v in kwargs.items():
        qry = qry.filter(getattr(model_class, k) == v)

    if order_by is not None:
        if isinstance(order_by, list):
            qry = qry.order_by(*order_by)
        else:
            qry = qry.order_by(order_by)

    return qry


def paginate(model_class, *args, page=1, page_size=10, error_out=False,
             order_by=None, **kwargs):
    """
    List model objects as pages.
    :param model_class:
    :param args:
    :param page:
    :param page_size:
    :param error_out:
    :param order_by:
    :param kwargs:
    :return:
    """
    q = query(model_class, *args, order_by=order_by, **kwargs)
    return q.paginate(page=page, per_page=page_size, error_out=error_out)
    # Items: result.items
    # Next page: result.has_next, result.next_num
    # Prev page: result.has_prev, result.prev_num


def iterate(model_class, *args, page_size=10, order_by=None, **kwargs):
    """
    Iter objects by page.
    In case we need to iterate over a large number of object, use this.
    Do not use query().all() as it may cause overflow error.
    """
    q = query(model_class, *args, order_by=order_by, **kwargs)
    page = 1
    while True:
        paginating = q.paginate(page=page, per_page=page_size, error_out=False)
        for item in paginating.items:
            yield item
        if paginating.has_next:
            page = paginating.next_num
        else:
            break


def exists(model_class, id):
    """
    Check if a model object exists.
    :param model_class:
    :param id:
    :return:
    """
    return load(model_class, id) is not None


def save_new(objs):
    """
    Save new model objects.
    :param objs:
    :return: an Error object if failed or None.
    """
    try:
        if isinstance(objs, db.Model):
            db.session.add(objs)
        else:
            for obj in objs:
                db.session.add(obj)
        db.session.commit()
    except BaseException as e:
        LOG.error(e)
        db.session.rollback()
        return errors.Error(message=errors.DB_COMMIT_FAILED, cause=e)


def save(objs=None):
    """
    Save model objects.
    :param objs:
    :return: an Error object if failed or None.
    """
    try:
        db.session.commit()
    except BaseException as e:
        LOG.error(e)
        db.session.rollback()
        return errors.Error(message=errors.DB_COMMIT_FAILED, cause=e)


def remove(objs):
    """
    Remove model objs from db.
    :param objs:
    :return: an Error object if failed or None.
    """
    try:
        if isinstance(objs, db.Model):
            db.session.delete(objs)
        else:
            for obj in objs:
                db.session.delete(obj)
        db.session.commit()
    except BaseException as e:
        LOG.error(e)
        db.session.rollback()
        return errors.Error(message=errors.DB_COMMIT_FAILED, cause=e)


def expire(objs):
    """
    Expire object(s).
    :param objs:
    :return:
    """
    if isinstance(objs, db.Model):
        db.session.expire(objs)
    else:
        for obj in objs:
            db.session.expire(obj)


def expire_all():
    """
    Expire all objects of the session.
    :return:
    """
    db.session.expire_all()


def refresh(objs):
    """
    Refresh object(s).
    :param objs:
    :return:
    """
    if isinstance(objs, db.Model):
        db.session.refresh(objs)
    else:
        for obj in objs:
            db.session.refresh(obj)


def load_user(user):
    """
    Load user from user id/name/email or user object.
    :param user: md.User object or user id/name/email.
    :return:
    """
    if user is None:
        return None
    if isinstance(user, User):
        return user
    if isinstance(user, int):
        return load(User, id=user)
    if isinstance(user, str):
        user = user.lower().strip()
        return query(User, (User.user_name == user) | (User.email == user)).first()
    return None


def load_user_group(obj):
    """
    Load user group from id or user group object.
    :param obj: md.UserGroup object or id.
    :return:
    """
    if obj is None:
        return None
    if isinstance(obj, UserGroup):
        return obj
    return load(UserGroup, id=int(obj))


def load_region(obj):
    """
    Load region from id or region object.
    :param obj: md.Region object or region id.
    :return:
    """
    if obj is None:
        return None
    if isinstance(obj, Region):
        return obj
    return load(Region, id=str(obj))


def load_promotion(obj):
    """
    Load promotion from id or promotion object.
    :param obj: md.Promotion object or id.
    :return:
    """
    if obj is None:
        return None
    if isinstance(obj, Promotion):
        return obj
    return load(Promotion, id=int(obj))


def load_product(obj):
    """
    Load product from id or product object.
    :param obj: md.Product object or id.
    :return:
    """
    if obj is None:
        return None
    if isinstance(obj, Product):
        return obj
    return load(Product, id=int(obj))


def load_order_group(obj):
    """
    Load order group from id or order group object.
    :param obj: md.OrderGroup object or id.
    :return:
    """
    if obj is None:
        return None
    if isinstance(obj, OrderGroup):
        return obj
    return load(OrderGroup, id=int(obj))


def load_order(obj):
    """
    Load order item from id or order item object.
    :param obj: md.OrderItem object or id.
    :return:
    """
    if obj is None:
        return None
    if isinstance(obj, Order):
        return obj
    return load(Order, id=int(obj))


def load_balance(obj):
    """
    Load balance from id or balance object.
    :param obj: md.Balance object or id.
    :return:
    """
    if obj is None:
        return None
    if isinstance(obj, Balance):
        return obj
    return load(Balance, id=int(obj))


def load_billing(obj):
    """
    Load billing from id or billing object.
    :param obj: md.Billing object or billing id.
    :return:
    """
    if obj is None:
        return None
    if isinstance(obj, Billing):
        return obj
    return load(Billing, id=int(obj))


def load_history(obj):
    """
    Load history from id or history object.
    :param obj: md.History object or history id.
    :return:
    """
    if obj is None:
        return None
    if isinstance(obj, History):
        return obj
    return load(History, id=int(obj))


def load_report(obj):
    """
    Load report from id or report object.
    :param obj: md.Report object or report id.
    :return:
    """
    if obj is None:
        return None
    if isinstance(obj, Report):
        return obj
    return load(Report, id=int(obj))


def load_ticket(obj):
    """
    Load ticket from id or ticket object.
    :param obj: md.Ticket object or ticket id.
    :return:
    """
    if obj is None:
        return None
    if isinstance(obj, Ticket):
        return obj
    return load(Ticket, id=int(obj))


def load_support(obj):
    """
    Load support from id or support object.
    :param obj: md.Support object or support id.
    :return:
    """
    if obj is None:
        return None
    if isinstance(obj, Support):
        return obj
    return load(Support, id=int(obj))


def load_task(obj):
    """
    Load task from id or task object.
    :param obj: md.Task object or task id.
    :return:
    """
    if obj is None:
        return None
    if isinstance(obj, Task):
        return obj
    return load(Task, id=int(obj))


def load_config(obj):
    """
    Load config from id or config object.
    :param obj: md.Configuration object or config id.
    :return:
    """
    if obj is None:
        return None
    if isinstance(obj, Configuration):
        return obj
    return load(Configuration, id=int(obj))


def load_compute(obj):
    """
    Load compute from id or compute object.
    :param obj: md.Compute object or id.
    :return:
    """
    if obj is None:
        return None
    if isinstance(obj, Compute):
        return obj
    return load(Compute, id=int(obj))


def load_ip(obj):
    """
    Load PublicIP from addr or IP object.
    :param obj: md.PublicIP object or addr.
    :return:
    """
    if obj is None:
        return None
    if isinstance(obj, PublicIP):
        return obj
    return load(PublicIP, id=obj)


def make_and(*conds):
    """
    Make "and" cond used in queries.
    :param conds:
    :return:
    """
    return {
        'op': 'and',
        'v': conds,
    }


def make_or(*conds):
    """
    Make "or" cond used in queries.
    :param conds:
    :return:
    """
    return {
        'op': 'or',
        'v': conds,
    }


def make_op(**kw):
    """
    Make cond used in queries.
    :param kw: is a dict like:
        {
            'op': <eq/ne/gt/egt/lt/elt/in/nin/like/nlike/ilike/nilike/contain/ncontain>,
            'k': <attr>,
            'v': <value to compare>,
        }
    :return:
    """
    return kw
