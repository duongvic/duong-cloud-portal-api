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
CREATE_ROLES = (md.UserRole.ADMIN,)
UPDATE_ROLES = (md.UserRole.ADMIN,)
DELETE_ROLES = (md.UserRole.ADMIN,)


def get_region(ctx):
    """
    Get region.
    :param ctx: sample ctx data:
        {
            'region': <region object>,
            'region_id': <region id if region object is not passed>,
            'fields': <fields to get as a list of str>,
        }
    :return:
    """
    data = ctx.data
    region = md.load_region(data.get('region') or data['region_id'])
    if not region:
        ctx.set_error(errors.REGION_NOT_FOUND, status=404)
        return

    # Everyone can get region info

    base_mgr.dump_object(ctx, object=region)
    return region


def get_regions(ctx):
    """
    Get multiple regions.
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
    return base_mgr.dump_objects(ctx, model_class=md.Region, roles_required=LIST_ROLES)


def create_region(ctx):
    """
    Create region.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def update_region(ctx):
    """
    Update region.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def delete_region(ctx):
    """
    Delete region.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)
