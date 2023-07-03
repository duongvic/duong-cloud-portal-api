#
# Copyright (c) 2020 FTI-CAS
#

from application import app
from application.base import errors
from application.managers import base as base_mgr, user_mgr
from application import models as md

LOG = app.logger

ADMIN_ROLES = (md.UserRole.ADMIN, md.UserRole.ADMIN_SALE, md.UserRole.ADMIN_IT)
GET_ROLES = ADMIN_ROLES
LIST_ROLES = ADMIN_ROLES
CREATE_ROLES = (md.UserRole.ADMIN,)
UPDATE_ROLES = (md.UserRole.ADMIN,)
DELETE_ROLES = (md.UserRole.ADMIN,)


def get_config(ctx):
    """
    Get config.
    :param ctx: sample ctx data:
        {
            'config': <config object>,
            'config_id': <config id if config object is not passed>,
            'fields': <fields to get as a list of str>,
        }
    :return:
    """
    if not user_mgr.check_user(ctx, roles=GET_ROLES):
        return

    data = ctx.data
    config = md.load_config(data.get('config') or data['config_id'])
    if not config:
        ctx.set_error(errors.CONFIG_NOT_FOUND, status=404)
        return

    base_mgr.dump_object(ctx, object=config)
    return config


def get_configs(ctx):
    """
    Get multiple configs. Only ADMIN can do this action.
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
    return base_mgr.dump_objects(ctx,
                                 model_class=md.Configuration,
                                 roles_required=LIST_ROLES)


def create_config(ctx):
    """
    Create config.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def update_config(ctx):
    """
    Update config.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def delete_config(ctx):
    """
    Delete config.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def get_app_config(ctx, config_name=None):
    """
    Get App config from DB.
    :param ctx:
    :param config_name:
    :return:
    """
    app_config = md.query(md.Configuration,
                          type=md.ConfigurationType.APP,
                          **({'name': config_name} if config_name else {}),
                          status=md.ConfigurationStatus.ENABLED,
                          order_by=md.Configuration.version.desc()).first()
    if not app_config:
        e = ValueError('Config APP/{} not found in database.'
                       .format(config_name or ''))
        LOG.error(e)
        ctx.set_error(errors.CONFIG_NOT_FOUND, cause=e, status=404)
        return

    ctx.response = app_config
    return app_config
