#
# Copyright (c) 2020 FTI-CAS
#

import functools
import ipaddress

from application import app
from application.base import errors
from application import models as md
from application.product_types import base, os_base
from application.product_types.openstack import os_api
from application.managers import user_mgr
from application.utils import date_util

LOG = app.logger

ACTION_GET_KEYPAIR= 'get keypair'
ACTION_GET_KEYPAIRS = 'get keypairs'
ACTION_CREATE_KEYPAIR= 'create keypair'
ACTION_DELETE_KEYPAIR= 'delete keypair'

ADMIN_ROLES = (md.UserRole.ADMIN, md.UserRole.ADMIN_SALE, md.UserRole.ADMIN_IT)
GET_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
LIST_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
CREATE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)
UPDATE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)
DELETE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)


class OSKeypair(os_base.OSBase):
    """
    Openstack keypair
    """

    def __init__(self):
        """
        Initialize keypair
        """
        super().__init__()

        # Load config
        # net_config = md.query(md.Configuration,
        #                       type=md.ConfigurationType.keypair,
        #                       name='keypair_config',
        #                       status=md.ConfigurationStatus.ENABLED,
        #                       order_by=md.Configuration.version.desc()).first()
        # if not net_config:
        #     raise ValueError('Config keypair/net_config not found in database.')
        # self.net_config = net_config.contents

    @property
    def supported(self):
        return True

    #######################################################
    # KEYPAIR
    #######################################################

    def get_keypair(self, ctx):
        """
        Get a keypair being created.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_keypair(ctx)

    def do_get_keypair(self, ctx):
        """
        Subclass should override this method.
        :param ctx:
        :return:
        """
        data = ctx.data
        listing = self.parse_ctx_listing(ctx)

        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        error, keypair = os_client.get_keypair(keypair_id=data['keypair_id'],
                                               user_id=data.get('user_id'),
                                               listing=listing)
        if error:
            ctx.set_error(errors.KEYPAIR_GET_FAILED, cause=error, status=404)
            return

        ctx.response = keypair
        return keypair

    def get_keypairs(self, ctx):
        """
        Get all keypairs created by user.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=LIST_ROLES):
            return

        return self.do_get_keypairs(ctx)

    def do_get_keypairs(self, ctx):
        """
        Subclass should override this method.
        :param ctx:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        data = ctx.data
        listing = self.parse_ctx_listing(ctx)
        error, keypairs = os_client.get_keypairs(user_id=data.get('user_id'),
                                                 listing=listing)
        if error:
            ctx.set_error(errors.KEYPAIR_GET_FAILED, cause=error, status=404)
            return
        data = [keypair['keypair'] for keypair in keypairs.pop('data')]
        keypairs['data'] = data
        ctx.response = keypairs
        return keypairs

    def create_keypair(self, ctx):
        """
        Do create new compute keypair.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        self.validate_create_keypair(ctx)
        if ctx.failed:
            return

        data = ctx.data
        keypair = {
            'name': data['name'],
            'public_key': data['public_key'],
            'key_type': data['key_type'],
            'user_id': data.get('user_id'),
        }

        return self.do_create_keypair(ctx, keypair=keypair)

    def validate_create_keypair(self, ctx):
        """
        Validate keypair
        :param ctx:
        :return:
        """

    def do_create_keypair(self, ctx, keypair, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param keypair:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        # TODO
        _, keypair_info = os_client.get_keypair(keypair_id=keypair['name'])

        if keypair_info:
            error = 'Already exists a keypair named {}'.format(keypair['name'])
            ctx.set_error(errors.KEYPAIR_CREATE_FAILED, cause=error, status=500)
            return

        return self._execute_client_func(ctx, keypair_obj=keypair,
                                         func=functools.partial(os_client.create_keypair, **keypair),
                                         method=method,
                                         on_result=on_result or self.on_create_keypair_result)

    def _execute_client_func(self, ctx, keypair_obj, func, method, on_result):
        """
        Execute client func.
        :param ctx:
        :param keypair_obj:
        :param func:
        :param method:
        :param on_result:
        :return:
        """
        def _on_result(ctx, result):
            on_result(ctx=ctx, keypair_obj=keypair_obj, result=result)
            # Finish history log for the action (if there is)
            self.finish_action_log(ctx, error=result[0])

        self.execute_client_func(ctx, func=func, method=method, on_result=_on_result)

    def on_create_keypair_result(self, ctx, keypair_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param keypair_obj:
        :param result:
        :return:
        """
        task = ACTION_CREATE_KEYPAIR
        error, data = result
        if error:
            LOG.error('Failed to create keypair: {}. Error {}.'.format(keypair_obj, error))
            ctx.set_error(errors.KEYPAIR_CREATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def update_keypair(self, ctx):
        """
        Do update a compute keypair.
        :param ctx:
        :return:
        """
        ctx.set_error(errors.KEYPAIR_UPDATE_FAILED, cause=errors.METHOD_NOT_SUPPORTED, status=405)
        return

    def do_update_keypair(self, ctx, keypair):
        """
        Subclass should override this method.
        :param ctx:
        :param keypair:
        :return:
        """

    def on_update_keypair_result(self, ctx, keypair, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def delete_keypair(self, ctx):
        """
        Do delete a compute keypair.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
            return

        data = ctx.data
        keypair = {
            'keypair_id': data['keypair_id'],
            'user_id': data.get('user_id'),
        }
        return self.do_delete_keypair(ctx, keypair=keypair)

    def do_delete_keypair(self, ctx, keypair, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param keypair:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, keypair_obj=keypair,
                                         func=functools.partial(os_client.delete_keypair, **keypair),
                                         method=method,
                                         on_result=on_result or self.on_delete_keypair_result)

    def on_delete_keypair_result(self, ctx, keypair_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param keypair_obj:
        :param result:
        :return:
        """
        task = ACTION_CREATE_KEYPAIR
        error, data = result
        if error:
            LOG.error('Failed to delete keypair: {}. Error {}.'.format(keypair_obj, error))
            ctx.set_error(errors.KEYPAIR_DELETE_FAILED, cause=error, status=500)

        ctx.response = data
        return data
