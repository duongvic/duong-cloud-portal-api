#
# Copyright (c) 2020 FTI-CAS
#

from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args

from application import app
from application.api.v1 import base
from application.base import context
from application.managers import region_mgr
from application import models as md

LOCATION = 'default'
auth = base.auth


#####################################################################
# REGIONS
#####################################################################

def do_get_region(args):
    """
    Do get region.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get region',
        check_token=False,
        data=args)
    return base.exec_manager_func(region_mgr.get_region, ctx)


def do_get_regions(args):
    """
    Do get multiple regions.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get regions',
        check_token=False,
        data=args)
    return base.exec_manager_func(region_mgr.get_regions, ctx)


def do_create_region(args):
    """
    Do create region.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create region',
        data=args)
    return base.exec_manager_func_with_log(region_mgr.create_region, ctx,
                                           action=md.HistoryAction.CREATE_REGION)


def do_update_region(args):
    """
    Do update region.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update region',
        data=args)
    return base.exec_manager_func_with_log(region_mgr.update_region, ctx,
                                           action=md.HistoryAction.UPDATE_REGION)


def do_delete_region(args):
    """
    Do delete region.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete region',
        data=args)
    return base.exec_manager_func_with_log(region_mgr.delete_region, ctx,
                                           action=md.HistoryAction.DELETE_REGION)


class Regions(Resource):
    get_regions_args = base.LIST_OBJECTS_ARGS

    create_region_args = {
        # TODO
    }

    @use_args(get_regions_args, location=LOCATION)
    def get(self, args):
        return do_get_regions(args=args)

    @auth.login_required
    @use_args(create_region_args, location=LOCATION)
    def post(self, args):
        return do_create_region(args=args)


class Region(Resource):
    get_region_args = base.GET_OBJECT_ARGS

    update_region_args = {
        # TODO
    }

    delete_region_args = {
    }

    @use_args(get_region_args, location=LOCATION)
    def get(self, args, region_id):
        args['region_id'] = region_id
        return do_get_region(args=args)

    @auth.login_required
    @use_args(update_region_args, location=LOCATION)
    def put(self, args, region_id):
        args['region_id'] = region_id
        return do_update_region(args=args)

    @auth.login_required
    @use_args(delete_region_args, location=LOCATION)
    def delete(self, args, region_id):
        args['region_id'] = region_id
        return do_delete_region(args=args)
