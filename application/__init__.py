#
# Copyright (c) 2020 FTI-CAS
#

import atexit

from flask import Flask
from flask_babel import Babel, lazy_gettext as _l
from flask_caching import Cache
from flask_cors import CORS
from flask_executor import Executor
from flask_limiter import Limiter, util as limiter_util
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler

from application import config


app = Flask(__name__, static_url_path='', static_folder='static')
app.config.from_object(config.Config)
app.secret_key = config.Config.SECRET_KEY
app.logger.setLevel(config.Config.LEVEL_LOGGING)

# CORS
cors = CORS(app, resources={r'/api/*': {'origins': '*'}})

# Scheduler
apscheduler = BackgroundScheduler(timezone='UTC')
apscheduler.start()
atexit.register(lambda: apscheduler.shutdown(wait=False))

# Executor
thread_executor = Executor(app, name='thread')
process_executor = Executor(app, name='process')

# DB
db = SQLAlchemy(app)
from .dao import init_db

# ADMIN user
from application import models as md
admin = md.User.query.filter_by(user_name=app.config['ADMINS'][0]['user_name']).first()
if not admin:
    raise ValueError('App admin user unable to load.')

# Caching
if app.config['CACHE_TYPE'] not in ('null', None):
    cache = Cache(app)

# Custom session (using Flask_Session)
if app.config['SESSION_TYPE'] not in ('null', None):
    if app.config['SESSION_TYPE'] == 'sqlalchemy':
        app.config['SESSION_SQLALCHEMY'] = db
    if app.config['SESSION_TYPE'] == 'redis':
        import redis
        app.config['SESSION_REDIS'] = redis
    session = Session(app)

# API
from .api import v1 as api_v1
api = api_v1

# Babel (localization)
babel = Babel(app)


@babel.localeselector
def get_locale():
    language = 'vi'
    current_user = api.api_auth.current_user()
    if current_user:
        language = current_user.language
    return language


# Limiter
limiter = Limiter(app, key_func=limiter_util.get_remote_address)

# Migration
migrate = Migrate(app, db)

# Json encoder for app
from application.base import common as app_common
app.json_encoder = app_common.AppJSONEncoder

# Init sentry
if app.config['USE_SENTRY']:
    import logging
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration
    sentry_logging = LoggingIntegration(
        level=logging.INFO,
        event_level=logging.ERROR
    )
    sentry_sdk.init(
        dsn=app.config['SENTRY_DNS'],
        integrations=[sentry_logging]
    )
