#
# Copyright (c) 2020 FTI-CAS
#

import os

from sqlalchemy import text

from application import app, db
from application import models as md
from application.utils import file_util

LOG = app.logger
DEBUG = app.config['ENV'] in ('dev', 'development', 'debug')


def init_db():
    # if app.config['ENV'] in ('dev', 'development', 'debug'):
    #     sql_path = os.path.join(app.root_path, 'db')
    #     db_name = 'postgresql'
    #
    #     try:
    #         create_db_sql = file_util.read_content(os.path.join(sql_path, db_name + '_create.sql'))
    #         db.session.execute(text(create_db_sql))
    #         db.session.commit()
    #     except BaseException as e:
    #         db.session.rollback()
    #         LOG.debug(e)
    #
    #     try:
    #         data_test_db_sql = file_util.read_content(os.path.join(sql_path, db_name + '_test_data.sql'))
    #         db.session.execute(text(data_test_db_sql))
    #         db.session.commit()
    #     except BaseException as e:
    #         db.session.rollback()
    #         LOG.debug(e)

    try:
        db.create_all()
        db.session.commit()
    except BaseException as e:
        LOG.error(e)

    try:
        if DEBUG:
            from . import init_data_debug
            init_data_debug.create_all()
        else:
            from . import init_data
            init_data.create_all()
    except BaseException as e:
        LOG.error(e)


# Init DB
init_db()
