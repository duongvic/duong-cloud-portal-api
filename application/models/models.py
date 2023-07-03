#
# Copyright (c) 2020 FTI-CAS
#

from sqlalchemy import or_
from sqlalchemy.orm.attributes import flag_modified, flag_dirty

from application import app, db
from application.base.context import current_context
from application.base import common, objects
from application.models import base, types as mdtypes
from application.utils import data_util, date_util, locale_util, str_util

LOG = app.logger

DB_TYPE_POSTGRESQL = 'postgresql'
DB_TYPE_MARIADB = 'mysql'
DB_TYPE_ALL = (DB_TYPE_POSTGRESQL, DB_TYPE_MARIADB)

DB_TYPE = app.config['DB_TYPE']
if DB_TYPE not in DB_TYPE_ALL:
    raise ValueError('DB_TYPE {} not supported.'.format(DB_TYPE))

if DB_TYPE == DB_TYPE_POSTGRESQL:
    from sqlalchemy.dialects import postgresql
    # If postgresql, use JSONB instead
    DB_JSON_TYPE = postgresql.JSONB
    DB_JSON_TYPE_INDEXING = True
else:
    # Just use regular JSON type
    DB_JSON_TYPE = db.JSON
    DB_JSON_TYPE_INDEXING = False
    

class ModelMixin(object):
    def flag_dirty(self):
        """
        Mark the object as dirty.
        :return:
        """
        flag_dirty(self)

    def flag_modified(self, attr):
        """
        Mark an attribute of the object as modified.
        Call this method when update a JSON column.
        :param attr:
        :return:
        """
        flag_modified(self, attr)

    def to_dict(self, fields=None, extra_fields=None, is_admin=False):
        """
        Convert this model object to dict object.
        :param fields:
        :param extra_fields:
        :param is_admin:
        :return:
        """
        return data_util.dump_value(self, fields=fields, extra_fields=extra_fields,
                                    is_admin=is_admin)

    def to_json(self, **kw):
        """
        Convert this model object to json object.
        :param kw:
        :return:
        """
        return self.to_dict(**kw)

    def to_json_str(self, **kw):
        """
        Convert this model object to json string.
        :param kw:
        :return:
        """
        return common.json_dumps(self.to_json(**kw))

    def get_attr(self, attr, *a):
        """
        Get an attribute of the object.
        :param attr:
        :param a:
        :return:
        """
        return getattr(self, attr, *a)

    def get_datetime_attr(self, attr, format=common.DATE_TIME_FORMAT):
        """
        Format datetime value.
        :param attr:
        :param format:
        :return:
        """
        return date_util.format(getattr(self, attr), format=format)

    @staticmethod
    def encrypt(data, key=None):
        """
        Encrypt data.
        """
        return str_util.jwt_encode_token(data, key=key)

    @staticmethod
    def decrypt(data, key=None):
        """
        Decrypt data.
        """
        if not data:
            return data
        return str_util.jwt_decode_token(data, key=key)

    @classmethod
    def query_join(cls, join_class, join_clause, query=None):
        query = query or cls.query
        if isinstance(join_class, str):
            join_class = MODEL_CLASS_MAP[join_class]

        if isinstance(join_clause, str):
            join_clause = [join_clause]

        condition = []
        for clause in join_clause:
            left_field, right_field = clause.split('==')
            left_class, left_attr = left_field.split('.')
            right_class, right_attr = right_field.split('.')
            left_class = MODEL_CLASS_MAP[left_class.strip()]
            right_class = MODEL_CLASS_MAP[right_class.strip()]
            clause = getattr(left_class, left_attr.strip()) == getattr(right_class, right_attr.strip())
            condition.append(clause)
        if len(condition) > 1:
            condition = or_(*condition)
        else:
            condition = condition[0]

        query = query.join(join_class, condition)
        return query


# class Session(db.Model):
#     __tablename__ = 'session'
#
#     id = db.Column(db.Integer, primary_key=True)
#     session_id = db.Column(db.String(255), unique=True)
#     data = db.Column(db.LargeBinary)
#     expiry = db.Column(db.DateTime)
#
#     def __init__(self, session_id, data, expiry):
#         self.session_id = session_id
#         self.data = data
#         self.expiry = expiry
#
#     def __repr__(self):
#         return '<Session data %s>' % self.data


class Lock(db.Model):
    __tablename__ = 'lock'

    __user_fields__ = ('id', 'timestamp')
    __admin_fields__ = __user_fields__

    id = db.Column(db.String(255), primary_key=True, index=True)
    timestamp = db.Column(db.DateTime)


class Configuration(db.Model, ModelMixin):
    __tablename__ = 'configuration'
    __table_args__ = (
        db.Index('configuration_type_name_version_idx', 'type', 'name', 'version', unique=True),
    )

    __user_fields__ = ('id', 'type', 'name', 'version', 'status', 'create_date',
                       'contents', 'extra')
    __admin_fields__ = __user_fields__

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50), index=True)
    name = db.Column(db.String(100), index=True)
    version = db.Column(db.Integer, index=True)
    status = db.Column(db.String(50), index=True)
    create_date = db.Column(db.DateTime, index=True)
    contents = db.Column(DB_JSON_TYPE)
    extra = db.Column(DB_JSON_TYPE)

    @property
    def version_str(self):
        """
        Convert version code to string in form: XX.XX.XX.
        E.g. ver code 10015 will result in ver str to be 1.0.15
        :return:
        """
        return objects.Version(self.version).get_str() if self.version is not None else None

    def set_version(self, version):
        """
        Set version from a value.
        :param version: an integer like 10000 or a string like 2.0.1
        :return:
        """
        self.version = objects.Version(version).get_code()


class History(db.Model, ModelMixin):
    __tablename__ = 'history'

    __user_fields__ = ('id', 'type', 'action', 'target_user_id', 'request_user_id', 'task_id',
                       'status', 'start_date', 'end_date', 'contents', 'extra')
    __admin_fields__ = __user_fields__

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50), index=True)
    action = db.Column(db.String(50), index=True)
    target_user_id = db.Column(db.ForeignKey('user.id'), index=True)
    request_user_id = db.Column(db.ForeignKey('user.id'), index=True)
    task_id = db.Column(db.ForeignKey('task.id'), index=True)
    status = db.Column(db.String(50), index=True)
    start_date = db.Column(db.DateTime, index=True)
    end_date = db.Column(db.DateTime, index=True)
    contents = db.Column(DB_JSON_TYPE)
    extra = db.Column(DB_JSON_TYPE)

    target_user = db.relationship('User', primaryjoin='History.target_user_id == User.id', backref='history1')
    request_user = db.relationship('User', primaryjoin='History.request_user_id == User.id', backref='history2')
    task = db.relationship('Task', primaryjoin='History.task_id == Task.id', backref='history')

    def __repr__(self):
        return '<History {} request_user={} target_user={}>'.format(self.id, self.request_user_id, self.target_user_id)


class Report(db.Model, ModelMixin):
    __tablename__ = 'report'

    __user_fields__ = ('id', 'type', 'name', 'status', 'start_date', 'end_date',
                       'contents', 'extra')
    __admin_fields__ = __user_fields__

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50), index=True)
    name = db.Column(db.String(100), index=True)
    status = db.Column(db.String(50), index=True)
    start_date = db.Column(db.DateTime, index=True)
    end_date = db.Column(db.DateTime, index=True)
    contents = db.Column(DB_JSON_TYPE)
    extra = db.Column(DB_JSON_TYPE)


class OrderGroup(db.Model, ModelMixin):
    __tablename__ = 'order_group'

    __user_fields__ = ('id', 'type', 'code', 'user_id', 'create_date', 'status',
                       'data', 'notes', 'extra')
    __admin_fields__ = __user_fields__

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50), index=True)
    code = db.Column(db.String(50), index=True)
    user_id = db.Column(db.ForeignKey('user.id'), index=True)
    create_date = db.Column(db.DateTime, index=True)
    status = db.Column(db.String(50), index=True)
    data = db.Column(DB_JSON_TYPE)
    notes = db.Column(db.Text)
    extra = db.Column(DB_JSON_TYPE)

    user = db.relationship('User', primaryjoin='OrderGroup.user_id == User.id', backref='order_group')

    def __repr__(self):
        return '<OrderGroup {} code={} user={}>'.format(self.id, self.code, self.user_id)

    @property
    def orders(self):
        # Should we use md.iterate(condition) instead?
        return Order.query.filter(Order.group_id == self.id).all()


class Order(db.Model, ModelMixin):
    __tablename__ = 'order'
    __table_args__ = {'quote': True}

    __user_fields__ = ('id', 'type', 'product_type', 'code', 'name', 'user_id', 'group_id',
                       'price', 'price_paid', 'amount', 'duration', 'status', 'create_date', 'start_date',
                       'end_date', 'promotion_id', 'discount_code', 'payment_type', 'currency', 'region_id',
                       'data', 'notes', 'extra')
    __admin_fields__ = __user_fields__

    # Fields may be stored in attribute self.data
    __data_fields__ = ('info', 'settings')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50), index=True)
    product_type = db.Column(db.String(50), index=True)
    code = db.Column(db.String(50), index=True)
    name = db.Column(db.String(50))
    user_id = db.Column(db.ForeignKey('user.id'), index=True)
    group_id = db.Column(db.ForeignKey('order_group.id'), index=True)
    price = db.Column(db.BigInteger)
    price_paid = db.Column(db.BigInteger)
    amount = db.Column(db.Integer)
    duration = db.Column(db.String(50))
    status = db.Column(db.String(50), index=True)
    create_date = db.Column(db.DateTime, index=True)
    start_date = db.Column(db.DateTime, index=True)
    end_date = db.Column(db.DateTime, index=True)
    discount_code = db.Column(db.String(100), index=True)
    promotion_id = db.Column(db.ForeignKey('promotion.id'), index=True)
    payment_type = db.Column(db.String(50), index=True)
    currency = db.Column(db.String(10))
    region_id = db.Column(db.ForeignKey('region.id'), index=True)
    data = db.Column(DB_JSON_TYPE)
    notes = db.Column(db.Text)
    extra = db.Column(DB_JSON_TYPE)

    user = db.relationship('User', primaryjoin='Order.user_id == User.id', backref='order')
    order_group = db.relationship('OrderGroup', primaryjoin='Order.group_id == OrderGroup.id', backref='order')
    promotion = db.relationship('Promotion', primaryjoin='Order.promotion_id == Promotion.id', backref='order')
    region = db.relationship('Region', primaryjoin='Order.region_id == Region.id', backref='order')

    def __repr__(self):
        return '<Order {} user={} group={}>'.format(self.id, self.user_id, self.group_id)

    @property
    def order_products(self):
        # Should we use md.iterate(condition) instead?
        return OrderProduct.query.filter(OrderProduct.order_id == self.id).all()

    @property
    def utilization(self):
        from application import product_types
        ctx = current_context
        product_type = product_types.get_product_type(ctx, self.product_type)
        if ctx.failed:
            return
        resp = product_type.get_order_utilization(ctx, order=self)
        if ctx.failed:
            return
        return resp


class OrderProduct(db.Model, ModelMixin):
    __tablename__ = 'order_product'

    __user_fields__ = ('id', 'order_id', 'product_id', 'price', 'price_paid',
                       'data', 'extra')
    __admin_fields__ = __user_fields__

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.ForeignKey('order.id'), index=True)
    product_id = db.Column(db.ForeignKey('product.id'), index=True)
    price = db.Column(db.BigInteger)
    price_paid = db.Column(db.BigInteger)
    data = db.Column(DB_JSON_TYPE)
    extra = db.Column(DB_JSON_TYPE)

    order = db.relationship('Order', primaryjoin='OrderProduct.order_id == Order.id', backref='order_product')
    product = db.relationship('Product', primaryjoin='OrderProduct.product_id == Product.id', backref='order_product')

    def __repr__(self):
        return '<OrderProduct {} order={}>'.format(self.id, self.order_id)

    @property
    def order_group(self):
        return (db.session.query(OrderGroup)
                .join(Order, OrderGroup.id == Order.group_id)
                .filter(Order.id == self.order_id)).first()


class Billing(db.Model, ModelMixin):
    __tablename__ = 'billing'

    __user_fields__ = ('id', 'type', 'code', 'user_id', 'order_id', 'create_date',
                       'end_date', 'status', 'price', 'price_paid', 'currency',
                       'data', 'notes', 'extra')
    __admin_fields__ = __user_fields__

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50), index=True)
    code = db.Column(db.String(50), index=True)
    user_id = db.Column(db.ForeignKey('user.id'), index=True)
    order_id = db.Column(db.ForeignKey('order.id'), index=True)
    create_date = db.Column(db.DateTime, index=True)
    end_date = db.Column(db.DateTime, index=True)
    status = db.Column(db.String(50), index=True)
    price = db.Column(db.BigInteger)
    price_paid = db.Column(db.BigInteger)
    currency = db.Column(db.String(10))
    data = db.Column(DB_JSON_TYPE)
    notes = db.Column(db.Text)
    extra = db.Column(DB_JSON_TYPE)

    user = db.relationship('User', primaryjoin='Billing.user_id == User.id', backref='billing')
    order = db.relationship('Order', primaryjoin='Billing.order_id == Order.id', backref='billing')

    def __repr__(self):
        return '<Billing {} code={} user={} order={}>'.format(
            self.id, self.code, self.user_id, self.order_id)

    @property
    def order_group(self):
        return (db.session.query(OrderGroup)
                .join(Order, OrderGroup.id == Order.group_id)
                .filter(Order.id == self.order_id)).first()


class Balance(db.Model, ModelMixin):
    __tablename__ = 'balance'

    __user_fields__ = ('id', 'user_id', 'type', 'create_date', 'end_date',
                       'status', 'balance', 'currency', 'data', 'notes', 'extra')
    __admin_fields__ = __user_fields__

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.ForeignKey('user.id'), index=True, unique=True)
    type = db.Column(db.String(50), index=True)
    create_date = db.Column(db.DateTime, index=True)
    end_date = db.Column(db.DateTime, index=True)
    status = db.Column(db.String(50), index=True)
    balance = db.Column(db.BigInteger)
    currency = db.Column(db.String(10))
    data = db.Column(DB_JSON_TYPE)
    notes = db.Column(db.Text)
    extra = db.Column(DB_JSON_TYPE)

    user = db.relationship('User', primaryjoin='Balance.user_id == User.id', backref='balance')

    def __repr__(self):
        return '<Balance {} user={}>'.format(self.id, self.user_id)


class Product(db.Model, ModelMixin):
    __tablename__ = 'product'

    __user_fields__ = ('id', 'type', 'code', 'name', 'description', 'create_date', 'end_date',
                       'info', 'status', 'region_id', 'pricing', 'extra')
    __admin_fields__ = __user_fields__

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50), index=True)
    code = db.Column(db.String(100), index=True)
    name = db.Column(db.String(100), index=True)
    description = db.Column(db.Text)
    create_date = db.Column(db.DateTime, index=True)
    end_date = db.Column(db.DateTime, index=True)
    info = db.Column(DB_JSON_TYPE)
    status = db.Column(db.String(50), index=True)
    region_id = db.Column(db.ForeignKey('region.id'), index=True)
    pricing = db.Column(DB_JSON_TYPE)
    extra = db.Column(DB_JSON_TYPE)

    region = db.relationship('Region', primaryjoin='Product.region_id == Region.id', backref='product')

    @property
    def enabled(self):
        if self.status != mdtypes.ProductStatus.ENABLED:
            return False
        if self.expired:
            return False
        return True

    @property
    def expired(self):
        end_date = self.end_date
        return end_date and date_util.utc_now() > end_date

    @property
    def is_compute(self):
        return self.type == mdtypes.ProductType.COMPUTE

    @property
    def is_os(self):
        return self.type == mdtypes.ProductType.OS


class Promotion(db.Model, ModelMixin):
    __tablename__ = 'promotion'

    __user_fields__ = ('id', 'type', 'name', 'description', 'create_date',
                       'start_date', 'end_date', 'status', 'region_id', 'target_product_types',
                       'target_product_ids', 'product_settings', 'user_settings',
                       'settings', 'discount_code', 'extra')
    __admin_fields__ = __user_fields__

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50), index=True)
    name = db.Column(db.String(50))
    description = db.Column(db.Text)
    create_date = db.Column(db.DateTime, index=True)
    start_date = db.Column(db.DateTime, index=True)
    end_date = db.Column(db.DateTime, index=True)
    status = db.Column(db.String(50), index=True)
    region_id = db.Column(db.ForeignKey('region.id'), index=True)
    target_product_types = db.Column(DB_JSON_TYPE, index=DB_JSON_TYPE_INDEXING)
    target_product_ids = db.Column(DB_JSON_TYPE, index=DB_JSON_TYPE_INDEXING)
    product_settings = db.Column(DB_JSON_TYPE)
    user_settings = db.Column(DB_JSON_TYPE)
    settings = db.Column(DB_JSON_TYPE)
    discount_code = db.Column(db.String(100), index=True)
    extra = db.Column(DB_JSON_TYPE)

    region = db.relationship('Region', primaryjoin='Promotion.region_id == Region.id', backref='promotion')

    @property
    def enabled(self):
        if self.status != mdtypes.PromotionStatus.ENABLED:
            return False
        if self.expired:
            return False
        return True

    @property
    def expired(self):
        start_date = self.start_date
        if start_date and date_util.utc_now() < start_date:
            return True
        end_date = self.end_date
        if end_date and date_util.utc_now() > end_date:
            return True
        return False

    def accept_product_type(self, product_type):
        """
        Check if the promotion accepts the product type(s).
        :param product_type: product type or list of product types.
        :return:
        """
        target_types = self.target_product_types
        if target_types is not None:
            check_types = [product_type] if isinstance(product_type, str) else product_type
            if 'ALL' in target_types or check_types is None:
                return True
            for type in check_types:
                if type not in target_types:
                    return False
        return True

    def accept_product_id(self, product_id):
        """
        Check if the promotion accepts the product id(s).
        :param product_id: product id or list of product ids.
        :return:
        """
        target_ids = self.target_product_ids
        if target_ids is not None:
            check_ids = [product_id] if isinstance(product_id, int) else product_id
            if 'ALL' in target_ids or check_ids is None:
                return True
            for id in check_ids:
                if id not in target_ids:
                    return False
        return True


class Region(db.Model, ModelMixin):
    __tablename__ = 'region'

    __user_fields__ = ('id', 'name', 'description', 'create_date', 'status',
                       'address', 'city', 'country_code', 'data', 'extra')
    __admin_fields__ = __user_fields__

    id = db.Column(db.String(50), primary_key=True, index=True)
    name = db.Column(db.String(50), index=True)
    description = db.Column(db.Text)
    create_date = db.Column(db.DateTime, index=True)
    status = db.Column(db.String(50), index=True)
    address = db.Column(db.String(100))
    city = db.Column(db.String(50), index=True)
    country_code = db.Column(db.String(10), index=True)
    data = db.Column(DB_JSON_TYPE)
    extra = db.Column(DB_JSON_TYPE)

    def __repr__(self):
        return '<Region {}>'.format(self.id)


class Temp(db.Model, ModelMixin):
    __tablename__ = 'temp'

    __user_fields__ = ('id', 'name', 'version', 'description', 'date', 'data')
    __admin_fields__ = __user_fields__

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200))
    version = db.Column(db.Integer)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime)
    data = db.Column(DB_JSON_TYPE)


class User(db.Model, ModelMixin):
    __tablename__ = 'user'
    __table_args__ = {'quote': True}

    __user_fields__ = ('id', 'user_name', 'email', 'status', 'create_date', 'end_date', 'role',
                       'group_id', 'group_role', 'full_name', 'workphone', 'cellphone', 'organization',
                       'address', 'city', 'country_code', 'id_number', 'language', 'extra')
    __admin_fields__ = __user_fields__ + ('data',)

    __user_update_fields__ = ('full_name', 'address', 'cellphone', 'workphone', 'organization',
                              'city', 'country_code', 'id_number', 'language')

    __admin_update_fields__ = __user_update_fields__ + ('group_id', 'group_role', 'status', 'role', 'data', 'extra')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    status = db.Column(db.String(50), index=True)
    create_date = db.Column(db.DateTime, index=True)
    end_date = db.Column(db.DateTime)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(1024), index=True, server_default='USER')
    group_id = db.Column(db.ForeignKey('user_group.id'), index=True)
    group_role = db.Column(db.String(1024), index=True)
    full_name = db.Column(db.String(50), index=True)
    workphone = db.Column(db.String(50))
    cellphone = db.Column(db.String(50), index=True)
    organization = db.Column(db.String(1024), index=True)
    address = db.Column(db.String(100))
    city = db.Column(db.String(50), index=True)
    country_code = db.Column(db.String(10), index=True)
    id_number = db.Column(db.String(50), index=True)
    language = db.Column(db.String(10), server_default='vi')
    data = db.Column(DB_JSON_TYPE)
    extra = db.Column(DB_JSON_TYPE)

    group = db.relationship('UserGroup', primaryjoin='User.group_id == UserGroup.id', backref='user')

    def __repr__(self):
        return '<User {} name={}>'.format(self.id, self.user_name)

    def set_password(self, password):
        self.password_hash = str_util.gen_user_password(password)

    def check_password(self, password):
        return str_util.check_user_password(self.password_hash, password)

    @property
    def enabled(self):
        if self.status != mdtypes.UserStatus.ENABLED:
            return False
        if self.expired:
            return False
        return True

    @property
    def expired(self):
        end_date = self.end_date
        return end_date and date_util.utc_now() > end_date

    @property
    def country(self):
        return locale_util.get_country_name(self.country_code)

    def gen_token(self, expires_in=600):
        return str_util.jwt_encode_token(self.id, expires_in=expires_in, algorithm='HS256')
        # return str_util.gen_random(32, base_chars=str_util.ALPHA_DIGIT_CHARS)

    @staticmethod
    def verify_token(token):
        try:
            user_id = str_util.jwt_decode_token(token, algorithms=['HS256'])
            return User.query.get(user_id)
        except BaseException as e:
            LOG.warning(e)

    @property
    def orders(self):
        return Order.query.filter(Order.user_id == self.id).all()


class UserGroup(db.Model, ModelMixin):
    __tablename__ = 'user_group'

    __user_fields__ = ('id', 'type', 'name', 'status', 'description', 'create_date',
                       'data', 'extra')
    __admin_fields__ = __user_fields__

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50), index=True)
    name = db.Column(db.String(100), index=True)
    status = db.Column(db.String(50), index=True)
    description = db.Column(db.Text)
    create_date = db.Column(db.DateTime, index=True)
    data = db.Column(DB_JSON_TYPE)
    extra = db.Column(DB_JSON_TYPE)

    def __repr__(self):
        return '<UserGroup {} name={}>'.format(self.id, self.name)


class Ticket(db.Model, ModelMixin):
    __tablename__ = 'ticket'

    __user_fields__ = ('id', 'type', 'code', 'user_id', 'target_id', 'status', 'level', 'issue',
                       'create_date', 'end_date', 'title', 'data', 'extra')
    __admin_fields__ = __user_fields__

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50), index=True)
    code = db.Column(db.String(50), index=True)
    user_id = db.Column(db.ForeignKey('user.id'), index=True)
    target_id = db.Column(db.Integer, index=True)
    status = db.Column(db.String(50), index=True)
    level = db.Column(db.String(50), index=True)
    issue = db.Column(db.String(255), index=True)
    create_date = db.Column(db.DateTime, index=True)
    end_date = db.Column(db.DateTime, index=True)
    title = db.Column(db.String(255))
    data = db.Column(DB_JSON_TYPE)
    extra = db.Column(DB_JSON_TYPE)

    user = db.relationship('User', primaryjoin='Ticket.user_id == User.id', backref='ticket')

    def __repr__(self):
        return '<Ticket {} user={}>'.format(self.id, self.user_id)


class Support(db.Model, ModelMixin):
    __tablename__ = 'support'

    __user_fields__ = ('id', 'type', 'code', 'user_id', 'target_id', 'status',
                       'issue', 'create_date', 'end_date', 'description', 'data', 'extra')
    __admin_fields__ = __user_fields__

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50), index=True)
    code = db.Column(db.String(50), index=True)
    user_id = db.Column(db.ForeignKey('user.id'), index=True)
    ticket_id = db.Column(db.ForeignKey('ticket.id'), index=True)
    status = db.Column(db.String(50), index=True)
    issue = db.Column(db.String(255), index=True)
    create_date = db.Column(db.DateTime, index=True)
    end_date = db.Column(db.DateTime, index=True)
    description = db.Column(db.String(1024))
    data = db.Column(DB_JSON_TYPE)
    extra = db.Column(DB_JSON_TYPE)

    user = db.relationship('User', primaryjoin='Support.user_id == User.id', backref='support')
    ticket = db.relationship('Ticket', primaryjoin='Support.ticket_id == Ticket.id', backref='support')

    def __repr__(self):
        return '<Support {} user={}>'.format(self.id, self.user_id)


class Compute(db.Model, ModelMixin):
    __tablename__ = 'compute'

    __user_fields__ = ('id', 'type', 'name', 'version', 'user_id', 'order_id',
                       'backend_id', 'backend_status', 'public_ip', 'description',
                       'create_date', 'end_date', 'status', 'region_id',
                       'data', 'extra')
    __admin_fields__ = __user_fields__

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50), index=True)
    name = db.Column(db.String(100), index=True)
    version = db.Column(db.Integer, index=True)
    user_id = db.Column(db.ForeignKey('user.id'), index=True)
    order_id = db.Column(db.ForeignKey('order.id'), index=True)
    backend_id = db.Column(db.String(512), index=True)
    backend_status = db.Column(db.String(255))
    public_ip = db.Column(db.String(512), index=True)
    description = db.Column(db.Text)
    create_date = db.Column(db.DateTime, index=True)
    end_date = db.Column(db.DateTime, index=True)
    status = db.Column(db.String(50), index=True)
    region_id = db.Column(db.ForeignKey('region.id'), index=True)
    data = db.Column(DB_JSON_TYPE)
    extra = db.Column(DB_JSON_TYPE)

    user = db.relationship('User', primaryjoin='Compute.user_id == User.id', backref='compute')
    order = db.relationship('Order', primaryjoin='Compute.order_id == Order.id', backref='compute')
    region = db.relationship('Region', primaryjoin='Compute.region_id == Region.id', backref='compute')

    def __repr__(self):
        return '<Compute {} user={}>'.format(self.id, self.user_id)

    @property
    def enabled(self):
        if self.status != mdtypes.ComputeStatus.ENABLED:
            return False
        if self.expired:
            return False
        return True

    @property
    def locked(self):
        return self.status == mdtypes.ComputeStatus.LOCKED

    @property
    def expired(self):
        end_date = self.end_date
        return end_date and date_util.utc_now() > end_date

    @property
    def order_group(self):
        return (db.session.query(OrderGroup)
                .join(Order, OrderGroup.id == Order.group_id)
                .filter(Order.id == self.order_id)).first()

    @property
    def order_products(self):
        # Should we use md.iterate(condition) instead?
        return OrderProduct.query.filter(OrderProduct.order_id == self.order_id).all()

    @property
    def products(self):
        return (db.session.query(Product)
                .join(OrderProduct, Product.id == OrderProduct.product_id)
                .join(Order, OrderProduct.order_id == Order.id)
                .filter(Order.id == self.order_id)).all()


class PublicIP(db.Model, ModelMixin):
    __tablename__ = 'public_ip'

    __user_fields__ = ('addr', 'type', 'version', 'status', 'create_date', 'start_date', 'end_date',
                       'mac_addr', 'user_id', 'compute_id', 'data', 'extra')
    __admin_fields__ = __user_fields__

    addr = db.Column(db.String(255), primary_key=True)
    type = db.Column(db.String(50), index=True)
    version = db.Column(db.Integer, index=True)
    status = db.Column(db.String(50), index=True)
    create_date = db.Column(db.DateTime, index=True)
    start_date = db.Column(db.DateTime, index=True)
    end_date = db.Column(db.DateTime, index=True)
    mac_addr = db.Column(db.String(50), index=True)
    user_id = db.Column(db.ForeignKey('user.id'), index=True)
    compute_id = db.Column(db.ForeignKey('compute.id'), index=True)
    data = db.Column(DB_JSON_TYPE)
    extra = db.Column(DB_JSON_TYPE)

    user = db.relationship('User', primaryjoin='PublicIP.user_id == User.id', backref='public_ip')
    compute = db.relationship('Compute', primaryjoin='PublicIP.compute_id == Compute.id', backref='public_ip2')

    def __repr__(self):
        return '<PublicIP {} user={}>'.format(self.id, self.user_id)


class Task(db.Model, ModelMixin):
    __tablename__ = 'task'

    __user_fields__ = ('id', 'type', 'name', 'user_id', 'target_id', 'target_entity',
                       'target_time', 'target_date', 'status', 'create_date',
                       'start_date', 'end_date', 'description', 'data', 'extra')
    __admin_fields__ = __user_fields__

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50), index=True)
    name = db.Column(db.String(50), index=True)
    user_id = db.Column(db.ForeignKey('user.id'), index=True)
    target_id = db.Column(db.Integer, index=True)
    target_entity = db.Column(db.String(16384), index=True)
    target_time = db.Column(db.String(255), index=True)
    target_date = db.Column(db.String(255), index=True)
    status = db.Column(db.String(50), index=True)
    create_date = db.Column(db.DateTime, index=True)
    start_date = db.Column(db.DateTime, index=True)
    end_date = db.Column(db.DateTime, index=True)
    description = db.Column(db.String(1024))
    data = db.Column(DB_JSON_TYPE)
    extra = db.Column(DB_JSON_TYPE)

    user = db.relationship('User', primaryjoin='Task.user_id == User.id', backref='task')

    def __repr__(self):
        return '<TaskJob {} user={}>'.format(self.id, self.user_id)


MODEL_CLASS_MAP = {
    User.__tablename__: User,
    UserGroup.__tablename__: UserGroup,
    OrderGroup.__tablename__: OrderGroup,
    Order.__tablename__: Order,
    OrderProduct.__tablename__: OrderProduct,
    Billing.__tablename__: Billing,
    Balance.__tablename__: Balance,
    Product.__tablename__: Product,
    Region.__tablename__: Region,
    Promotion.__tablename__: Promotion,
    Configuration.__tablename__: Configuration,
    Lock.__tablename__: Lock,
    History.__tablename__: History,
    Report.__tablename__: Report,
    Ticket.__tablename__: Ticket,
    Support.__tablename__: Support,
    Compute.__tablename__: Compute,
    PublicIP.__tablename__: PublicIP,
    Task.__tablename__: Task,
}


def get_model_class(name):
    """
    Get model class for the name.
    :param name:
    :return:
    """
    return MODEL_CLASS_MAP[name]
