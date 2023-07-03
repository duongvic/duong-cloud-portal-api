#
# Copyright (c) 2020 FTI-CAS
#

from datetime import timedelta
import logging
from os import environ as env


def _env_bool(name):
    val = env.get(name)
    if val is None:
        return val
    return val.lower() in ('true', '1', 'on', 'yes')


class Config(object):
    DEBUG = _env_bool('FLASK_DEBUG') or True
    SECRET_KEY = 'Fti-Cas-82~d9^&(@!#6%1*7'
    ENV = env.get('FLASK_ENV', 'development')
    LEVEL_LOGGING = logging.DEBUG if DEBUG else logging.INFO

    # Home page url
    HOME_PAGE = 'https://foxcloud.vn'

    SERVICE_NAME = 'FoxCloud'
    SERVER_HOST = 'localhost' if DEBUG else env.get('CAS_SERVER_HOST')
    SERVER_PORT = 5000 if DEBUG else env.get('CAS_SERVER_PORT')
    SERVER_HTTP = 'http' if DEBUG else 'https'
    SERVER_URL = '{0}://{1}{2}'.format(SERVER_HTTP, SERVER_HOST, '' if SERVER_PORT in (80, 443) else ':' + str(SERVER_PORT))
    # SERVER_NAME = '{0}:{1}'.format(SERVER_HOST, SERVER_PORT)

    # Session timeout
    PERMANENT_SESSION_LIFETIME = timedelta(days=1000) if DEBUG else timedelta(minutes=10)

    # API
    API_ACCESS_TOKEN_EXPIRATION = timedelta(days=1000) if DEBUG else timedelta(minutes=10)
    API_REFRESH_TOKEN_EXPIRATION = API_ACCESS_TOKEN_EXPIRATION * 2

    # Database
    DB_HOST = 'localhost' if DEBUG else env.get('CAS_DB_HOST')
    DB_PORT = int(env.get('CAS_DB_PORT') or 3306)
    DB_TYPE = 'mysql'
    DB_USER = 'foxcloud-api-user' if DEBUG else env.get('CAS_DB_USER')
    DB_PASSWORD = 'Fti@123' if DEBUG else env.get('CAS_DB_PASSWORD')
    DB_NAME = 'foxcloud' if DEBUG else env.get('CAS_DB_NAME')

    # DB object listing
    DB_MAX_ITEMS_PER_PAGE = 1000
    DB_ITEMS_PER_PAGE = 20

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = '{0}+pymysql://{1}:{2}@{3}:{4}/{5}?charset=utf8mb4'.format(DB_TYPE, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 20,
    }

    # Session
    SESSION_TYPE = 'null'  # null, redis, memcached, filesystem, mongodb, sqlalchemy
    SESSION_REDIS = None   # Need to set to db in app init
    SESSION_SQLALCHEMY = None  # Need to set to redis in app init

    # Caching
    CACHE_TYPE = 'null'  # null, simple, filesystem, uwsgi, memcached, redis
    CACHE_DEFAULT_TIMEOUT = 300
    # Cache redis (affect only when CACHE_TYPE = 'redis')
    CACHE_REDIS_HOST = 'localhost' if DEBUG else env.get('CAS_CACHE_REDIS_HOST')
    CACHE_REDIS_PORT = 6379 if DEBUG else env.get('CAS_CACHE_REDIS_PORT')
    CACHE_REDIS_PASSWORD = 'Fti@123' if DEBUG else env.get('CAS_CACHE_REDIS_PASSWORD')
    CACHE_REDIS_DB = '' if DEBUG else env.get('CAS_CACHE_REDIS_DB')

    # Executor
    THREAD_EXECUTOR_TYPE = 'thread'
    THREAD_EXECUTOR_MAX_WORKERS = 10
    # THREAD_EXECUTOR_FUTURES_MAX_LENGTH = ?
    THREAD_EXECUTOR_PROPAGATE_EXCEPTIONS = False

    PROCESS_EXECUTOR_TYPE = 'process'
    PROCESS_EXECUTOR_MAX_WORKERS = 10
    # PROCESS_EXECUTOR_FUTURES_MAX_LENGTH = ?
    PROCESS_EXECUTOR_PROPAGATE_EXCEPTIONS = False

    # Admins (used in some contexts requiring Admin role)
    ADMINS = [
        {
            'user_name': 'admin.foxcloud.vn',
        },
    ]

    # User
    LANGUAGES = ['en', 'vi']
    PASSWORD_RESET_TIMEOUT = 60 * 60  # 1 hour in seconds
    PASSWORD_REQUIREMENT = {
        'min_len': 8 if not DEBUG else 3,
        'max_len': 32,
        'lowercase': not DEBUG,
        'uppercase': not DEBUG,
        'digit': not DEBUG,
        'symbol': not DEBUG,   # True/False or symbols like '-&%$'
    }

    # Mails
    MAILING = {
        'info': {
            'host': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True,
            'use_ssl': False,
            'usr': 'vc.cas.ftel@gmail.com',
            'pwd': 'Fti@1234',
        },
        'support': {
            'host': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True,
            'use_ssl': False,
            'usr': 'vc.cas.ftel@gmail.com',
            'pwd': 'Fti@1234',
        },
        'service': {
            'host': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True,
            'use_ssl': False,
            'usr': 'vc.cas.ftel@gmail.com',
            'pwd': 'Fti@1234',
        },
        'issue': {
            'host': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True,
            'use_ssl': False,
            'usr': 'vc.cas.ftel@gmail.com',
            'pwd': 'Fti@1234',
        }
    }

    # Payment
    PAYMENT_TYPE = 'GATE_VNPAY'  # AUTO, GATE_VNPAY
    PAYMENT_CURRENCY = 'VND'
    PAYMENT_CURRENCIES = ['VND']
    PAYMENT_VNPAY_CONFIG = {
        'sandbox': {
            'payment_url': 'http://sandbox.vnpayment.vn/paymentv2/vpcpay.html',
            'return_url': SERVER_URL + '/vnpay_return',
            'api_url': 'http://sandbox.vnpayment.vn/merchant_webapi/merchant.html',
            'tmn_code': 'J4M9CIEQ',
            'secret_key': 'BEIWK4GDT7VEHHELFAG63SKRC3168KL8',  # Get from admin dashboard vnpay page
            'version': '2.0.0',
        },
        'default': {
            'payment_url': 'https://',
            'return_url': SERVER_URL + '/vnpay_return',
            'api_url': 'https://',
            'tmn_code': '',
            'secret_key': '',
            'version': '2.0.0',
        }
    }
    PAYMENT_VNPAY = PAYMENT_VNPAY_CONFIG['sandbox' if DEBUG else 'default']

    # Product types
    PRODUCT_TYPE_COMPUTE_TYPE = 'openstack'  # openstack, proxmox

    # Compute requirements
    COMPUTE_PASSWORD_REQUIREMENT = {
        'min_len': 8 if not DEBUG else 3,
        'max_len': 32,
        'lowercase': not DEBUG,
        'uppercase': not DEBUG,
        'digit': not DEBUG,
        'symbol': not DEBUG,
    }

    # Background Jobs
    JOB_CLEAR_OLD_HISTORY_LOGS = {'trigger': 'cron', 'hour': 19, 'minute': 0}      # 2:00 AM daily
    JOB_CLEAR_OLD_REPORTS = {'trigger': 'cron', 'hour': 19, 'minute': 10}          # 2:10 AM daily
    JOB_CLEAR_OLD_SUPPORTS = {'trigger': 'cron', 'hour': 19, 'minute': 20}         # 2:20 AM daily
    JOB_SYNC_COMPUTES_DAILY = {'trigger': 'cron', 'hour': 20, 'minute': 0}         # 3:00 AM daily

    # Sentry config
    USE_SENTRY = False
    SENTRY_DNS = 'https://75a04b42a3b949559fea9bdfc30226ba@o274485.ingest.sentry.io/5311135'

    # Openstack Config
    OS_SERVICES_VERSION = {
        'cinder': '3.55',  # 3.55 (Maximum in Ussuri)
        'neutron': '2',
        'nova': '2.87',  # 2.87 (Maximum in Ussuri)
        'trove': '2',
    }
    PROVIDER_SRIOV = "sriov"
    CURRENT_HEAT_VERSION = 'rocky'
    HEAT_TEMPLATE_VERSIONS = {
        'rocky': '2018-08-31',
        'queen': '',
        'pike': '',
    }
    CEPH = {
        'config_file': '',
        'pool':  '',
        'keyring': '',
    }
