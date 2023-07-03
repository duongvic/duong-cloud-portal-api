#
# Copyright (c) 2020 FTI-CAS
#

import functools
import ipaddress

from application import app
from application.base import errors
from application import models as md
from application.product_types import base, os_base
from application.product_types.openstack import os_magnum_api as magnum_api
from application.managers import user_mgr
from application.utils import date_util

LOG = app.logger

ADMIN_ROLES = (md.UserRole.ADMIN, md.UserRole.ADMIN_SALE, md.UserRole.ADMIN_IT)
GET_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
LIST_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
CREATE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)
UPDATE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)
DELETE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)


class OSMagnum(os_base.OSBase):
    """
    Openstack Magnum
    """

    def __init__(self):
        """
        Initialize keypair
        """
        super().__init__()

    @property
    def supported(self):
        return True

    def get_os_client(self, ctx, cluster=None, engine='console', services='coe'):
        """
        Get openstack client
        :param ctx:
        :param cluster:
        :param engine:
        :param services:
        :return
        """
        cluster = cluster or self.parse_ctx_cluster(ctx)
        if ctx.failed:
            return
        os_config = self.get_os_config(ctx, cluster=cluster)
        if ctx.failed:
            return
        return magnum_api.get_magnum_client(cluster=cluster, os_config=os_config,
                                              engine=engine, services=services)

    def get_magnum_cluster(self, ctx):
        """
        Get a magnum_cluster being created.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_magnum_cluster(ctx)

    def do_get_magnum_cluster(self, ctx):
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

        error, magnum_cluster = os_client.get_cluster(cluster_id=data['cluster_id'], listing=listing)
        if error:
            ctx.set_error(errors.MAGNUM_CLUSTER_GET_FAILED, cause=error, status=404)
            return

        ctx.response = magnum_cluster
        return magnum_cluster

    def get_magnum_clusters(self, ctx):
        """
        Get all magnum_clusters created by user.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=LIST_ROLES):
            return

        return self.do_get_magnum_clusters(ctx)

    def do_get_magnum_clusters(self, ctx):
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
        filters = data.get('filters') or {}

        error, magnum_clusters = os_client.get_clusters(listing=listing, **filters)
        if error:
            ctx.set_error(errors.MAGNUM_CLUSTER_GET_FAILED, cause=error, status=404)
            return
        ctx.response = magnum_clusters
        return magnum_clusters['data']

    def create_magnum_cluster(self, ctx):
        """
        Do create new magnum_cluster.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        data = ctx.data
        magnum_cluster = {
            'name': data['name'],
            'template_id': data['template_id'],
            'keypair_id': data['keypair_id'],
            'node_flavor_id': data['node_flavor_id'],
            'master_flavor_id': data['master_flavor_id'],
            'node_count': data['node_count'],
            'master_count': data['master_count'],
            'timeout': data['timeout'],
            'floating_ip_enabled': data['floating_ip_enabled'],
            'labels': data.get('labels'),
            'wait': data['wait'],
        }

        network_id = data.get('network_id')
        subnet_id = data.get('subnet_id')
        if not subnet_id and not network_id:
            error = "Network or subnet must be set"
            ctx.set_error(errors.MAGNUM_CLUSTER_CREATE_FAILED, error=error, status=400)
            return
        magnum_cluster['network_id'] = network_id
        magnum_cluster['subnet_id'] = subnet_id

        return self.do_create_magnum_cluster(ctx, magnum_cluster=magnum_cluster)

    def do_create_magnum_cluster(self, ctx, magnum_cluster, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param magnum_cluster:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, magnum_obj=magnum_cluster,
                                         func=functools.partial(os_client.create_cluster, **magnum_cluster),
                                         method=method,
                                         on_result=on_result or self.on_create_magnum_cluster_result)

    def _execute_client_func(self, ctx, magnum_obj, func, method, on_result):
        """
        Execute client func.
        :param ctx:
        :param lb_obj:
        :param func:
        :param method:
        :param on_result:
        :return:
        """

        def _on_result(ctx, result):
            on_result(ctx=ctx, magnum_obj=magnum_obj, result=result)
            # Finish history log for the action (if there is)
            self.finish_action_log(ctx, error=result[0])

        self.execute_client_func(ctx, func=func, method=method, on_result=_on_result)

    def on_create_magnum_cluster_result(self, ctx, magnum_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param magnum_cluster_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to create magnum_cluster: {}. Error {}.'.format(magnum_obj, error))
            ctx.set_error(errors.MAGNUM_CLUSTER_CREATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def update_magnum_cluster(self, ctx):
        """
        Do update a magnum_cluster.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
            return

        data = ctx.data
        magnum_cluster = {
            'id': data['cluster_id'],
            'patch': data.get('patch'),
        }

        return self.do_update_magnum_cluster(ctx, magnum_cluster=magnum_cluster)

    def do_update_magnum_cluster(self, ctx, magnum_cluster, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param magnum_cluster:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, magnum_obj=magnum_cluster,
                                         func=functools.partial(os_client.update_cluster, **magnum_cluster),
                                         method=method,
                                         on_result=on_result or self.on_update_magnum_cluster_result)

    def on_update_magnum_cluster_result(self, ctx, magnum_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param magnum_cluster_obj:
        :param result
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to create magnum_cluster: {}. Error {}.'.format(magnum_obj, error))
            ctx.set_error(errors.MAGNUM_CLUSTER_UPDATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def delete_magnum_cluster(self, ctx):
        """
        Do delete a magnum_cluster.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
            return

        data = ctx.data
        magnum_cluster = {
            'id': data['cluster_id'],
        }
        return self.do_delete_magnum_cluster(ctx, magnum_cluster=magnum_cluster)

    def do_delete_magnum_cluster(self, ctx, magnum_cluster, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param magnum_cluster:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, magnum_obj=magnum_cluster,
                                         func=functools.partial(os_client.delete_cluster, **magnum_cluster),
                                         method=method,
                                         on_result=on_result or self.on_delete_magnum_cluster_result)

    def on_delete_magnum_cluster_result(self, ctx, magnum_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param magnum_cluster_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to delete magnum_cluster: {}. Error {}.'.format(magnum_obj, error))
            ctx.set_error(errors.MAGNUM_CLUSTER_DELETE_FAILED, cause=error, status=500)
            return
        ctx.response = data
        return data

    def get_magnum_cluster_template(self, ctx):
        """
        Get a magnum_cluster_template being created.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_magnum_cluster_template(ctx)

    def do_get_magnum_cluster_template(self, ctx):
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

        error, magnum_cluster_template = os_client.get_cluster_template(template_id=data['template_id'],
                                                                        listing=listing)
        if error:
            ctx.set_error(errors.MAGNUM_CLUSTER_TEMPLATE_GET_FAILED, cause=error, status=404)
            return

        ctx.response = magnum_cluster_template
        return magnum_cluster_template

    def get_magnum_cluster_templates(self, ctx):
        """
        Get all magnum_cluster_templates created by user.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=LIST_ROLES):
            return

        return self.do_get_magnum_cluster_templates(ctx)

    def do_get_magnum_cluster_templates(self, ctx):
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
        filters = data.get('filters') or {}

        error, magnum_cluster_templates = os_client.get_cluster_templates(listing=listing, **filters)
        if error:
            ctx.set_error(errors.MAGNUM_CLUSTER_TEMPLATE_GET_FAILED, cause=error, status=404)
            return
        ctx.response = magnum_cluster_templates
        return magnum_cluster_templates['data']

    def create_magnum_cluster_template(self, ctx):
        """
        Do create new magnum_cluster_template.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        data = ctx.data
        cluster_template = {
            'name': data['name'],
            'keypair_id': data['keypair_id'],
            'docker_volume_size': data['docker_volume_size'],
            'external_network_id': data['external_network_id'],
            'image_id': data['image_id'],
            'coe': data['coe'],
            'network_driver': data['network_driver'],
            'dns': data.get('dns'),
            'master_lb_enabled': data['master_lb_enabled'],
            'floating_ip_enabled': data['floating_ip_enabled'],
            'volume_driver': data['volume_driver'],
            'tls_disabled': data['tls_disabled'],
            'is_public': data['is_public'],
            'hidden': data['hidden'],
            'labels': data.get('labels'),
            # 'wait': data['wait'],
        }

        return self.do_create_magnum_cluster_template(ctx, cluster_template=cluster_template)

    def do_create_magnum_cluster_template(self, ctx, cluster_template, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param magnum_cluster_template:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, magnum_obj=cluster_template,
                                         func=functools.partial(os_client.create_cluster_template,
                                                                **cluster_template),
                                         method=method,
                                         on_result=on_result or self.on_create_magnum_cluster_template_result)

    def on_create_magnum_cluster_template_result(self, ctx, magnum_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param magnum_cluster_template_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to create magnum_cluster_template: {}. Error {}.'.format(magnum_obj, error))
            ctx.set_error(errors.MAGNUM_CLUSTER_TEMPLATE_CREATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def update_magnum_cluster_template(self, ctx):
        """
        Do update a magnum_cluster_template.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
            return

        data = ctx.data
        cluster_template = {
            'id': data['template_id'],
            'patch': data.get('patch') or [],
        }

        return self.do_update_magnum_cluster_template(ctx, cluster_template=cluster_template)

    def validate_update_template(self, ctx):
        data = ctx.data
        patch = data.get('patch')

    def do_update_magnum_cluster_template(self, ctx, cluster_template, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param magnum_cluster_template:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, magnum_obj=cluster_template,
                                         func=functools.partial(os_client.update_cluster_template,
                                                                **cluster_template),
                                         method=method,
                                         on_result=on_result or self.on_update_magnum_cluster_template_result)

    def on_update_magnum_cluster_template_result(self, ctx, magnum_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param magnum_cluster_template_obj:
        :param result
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to create magnum_cluster_template: {}. Error {}.'.format(magnum_obj, error))
            ctx.set_error(errors.MAGNUM_CLUSTER_TEMPLATE_UPDATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def delete_magnum_cluster_template(self, ctx):
        """
        Do delete a magnum_cluster_template.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
            return

        data = ctx.data
        cluster_template = {
            'id': data['template_id'],
        }
        return self.do_delete_magnum_cluster_template(ctx, cluster_template=cluster_template)

    def do_delete_magnum_cluster_template(self, ctx, cluster_template, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param magnum_cluster_template:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, magnum_obj=cluster_template,
                                         func=functools.partial(os_client.delete_cluster_template,
                                                                **cluster_template),
                                         method=method,
                                         on_result=on_result or self.on_delete_magnum_cluster_template_result)

    def on_delete_magnum_cluster_template_result(self, ctx, magnum_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param magnum_cluster_template_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to delete magnum_cluster_template: {}. Error {}.'.format(magnum_obj, error))
            ctx.set_error(errors.MAGNUM_CLUSTER_TEMPLATE_DELETE_FAILED, cause=error, status=500)

        ctx.response = data
        return data

