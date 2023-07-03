#
# Copyright (c) 2020 FTI-CAS
#

import functools
import ipaddress

from application import app
from application.base import errors
from application import models as md
from application.product_types import base, os_base
from application.product_types.openstack import os_lbaas_api as lbaas_api
from application.managers import user_mgr
from application.utils import net_util

LOG = app.logger

ACTION_GET_LB = 'get lb'
ACTION_GET_LBS = 'get lbs'
ACTION_CREATE_LB = 'create lb'
ACTION_UPDATE_LB = 'update lb'
ACTION_DELETE_LB = 'delete lb'

ACTION_GET_LISTENER = 'get listener'
ACTION_GET_LISTENERS = 'get listeners'
ACTION_CREATE_LISTENER = 'create listener'
ACTION_UPDATE_LISTENER = 'update listener'
ACTION_DELETE_LISTENER = 'delete listener'

ACTION_GET_POOL= 'get pool'
ACTION_GET_POOLS = 'get pools'
ACTION_CREATE_POOL = 'create pool'
ACTION_DELETE_POOL = 'delete pool'

ACTION_GET_POOL_MEMBER = 'get pool member'
ACTION_GET_POOL_MEMBERS = 'get pool members'
ACTION_CREATE_POOL_MEMBER = 'create pool member'
ACTION_DELETE_POOL_MEMBER = 'delete pool member'

ADMIN_ROLES = (md.UserRole.ADMIN, md.UserRole.ADMIN_SALE, md.UserRole.ADMIN_IT)
GET_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
LIST_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
CREATE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)
UPDATE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)
DELETE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)


class OSLbaas(os_base.OSBase):
    """
    Openstack Lbaas
    """
    SUPPORTED_PROTOCOL = ['HTTP', 'HTTPS', 'SCTP', 'TCP', 'TERMINATED_HTTPS', 'UDP']

    def __init__(self):
        """
        Initialize keypair
        """
        super().__init__()

    @property
    def supported(self):
        return True

    def get_os_client(self, ctx, cluster=None, engine='console', services='lbaas'):
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
        return lbaas_api.get_lbaas_client(cluster=cluster, os_config=os_config, engine=engine, services=services)

    def get_lb(self, ctx):
        """
        Get a lb being created.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_lb(ctx)

    def do_get_lb(self, ctx):
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

        error, lb = os_client.get_lb(lb_id=data['lb_id'], listing=listing)
        if error:
            ctx.set_error(errors.LB_GET_FAILED, cause=error, status=404)
            return

        ctx.response = lb
        return lb

    def get_lbs(self, ctx):
        """
        Get all lbs created by user.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=LIST_ROLES):
            return

        return self.do_get_lbs(ctx)

    def do_get_lbs(self, ctx):
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

        error, lbs = os_client.get_lbs(listing=listing, **filters)
        if error:
            ctx.set_error(errors.LB_GET_FAILED, cause=error, status=404)
            return
        ctx.response = lbs
        return lbs['data']

    def create_lb(self, ctx):
        """
        Do create new lb.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        data = ctx.data
        lb = {
            'name': data['name'],
            'description': data.get('description'),
            'subnet_id': data['subnet_id'],
            'wait': data.get('wait') or False,
        }
        vip_address = data.get('vip_address')
        if vip_address:
            lb['vip_address'] = vip_address

        flavor_id = data.get('flavor_id')
        if flavor_id:
            lb['flavor_id'] = flavor_id

        tags = data.get('tags')
        if tags:
            lb['tags'] = tags

        return self.do_create_lb(ctx, lb=lb)

    def do_create_lb(self, ctx, lb, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param lb:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=lb,
                                         func=functools.partial(os_client.create_lb, **lb),
                                         method=method,
                                         on_result=on_result or self.on_create_lb_result)

    def _execute_client_func(self, ctx, lb_obj, func, method, on_result):
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
            on_result(ctx=ctx, lb_obj=lb_obj, result=result)
            # Finish history log for the action (if there is)
            self.finish_action_log(ctx, error=result[0])

        self.execute_client_func(ctx, func=func, method=method, on_result=_on_result)

    def on_create_lb_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param lb_obj:
        :param result:
        :return:
        """
        task = ACTION_CREATE_LB
        error, data = result
        if error:
            LOG.error('Failed to create lb: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.LB_CREATE_FAILED, cause=error, status=400)
            return

        ctx.response = data
        return data

    def update_lb(self, ctx):
        """
        Do update a lb.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
            return

        data = ctx.data
        lb = {
            'id': data['lb_id'],
            'name': data.get('name'),
            'description': data.get('description'),
        }
        tags = data.get('tags')
        if tags:
            lb['tags'] = tags

        return self.do_update_lb(ctx, lb=lb)

    def do_update_lb(self, ctx, lb, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param lb:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=lb,
                                         func=functools.partial(os_client.update_lb, **lb),
                                         method=method,
                                         on_result=on_result or self.on_update_lb_result)

    def on_update_lb_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param lb_obj:
        :param result
        :return:
        """
        task = ACTION_UPDATE_LB
        error, data = result
        if error:
            LOG.error('Failed to create lb: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.LB_CREATE_FAILED, cause=error, status=400)
            return

        ctx.response = data
        return data

    def delete_lb(self, ctx):
        """
        Do delete a lb.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
            return

        data = ctx.data
        lb = {
            'id': data['lb_id'],
        }
        return self.do_delete_lb(ctx, lb=lb)

    def do_delete_lb(self, ctx, lb, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param lb:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=lb,
                                         func=functools.partial(os_client.delete_lb, **lb),
                                         method=method,
                                         on_result=on_result or self.on_delete_lb_result)

    def on_delete_lb_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param lb_obj:
        :param result:
        :return:
        """
        task = ACTION_DELETE_LB
        error, data = result
        if error:
            LOG.error('Failed to delete lb: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.LB_DELETE_FAILED, cause=error, status=400)

        ctx.response = data
        return data

    def get_listener(self, ctx):
        """
        Get a listener being created.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_listener(ctx)

    def do_get_listener(self, ctx):
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

        error, listener = os_client.get_listener(id=data['listener_id'], listing=listing)
        if error:
            ctx.set_error(errors.LISTENER_GET_FAILED, cause=error, status=404)
            return

        ctx.response = listener
        return listener

    def get_listeners(self, ctx):
        """
        Get all listeners created by user.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=LIST_ROLES):
            return

        return self.do_get_listeners(ctx)

    def do_get_listeners(self, ctx):
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

        error, listeners = os_client.get_listeners(listing=listing, **filters)
        if error:
            ctx.set_error(errors.LISTENER_GET_FAILED, cause=error, status=404)
            return
        ctx.response = listeners
        return listeners['data']

    def create_listener(self, ctx):
        """
        Do create new listener.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        data = ctx.data
        listener = {
            'name': data['name'],
            'description': data.get('description'),
            'protocol': data['protocol'],
            'port': data['port'],
            'lb_id': data['lb_id'],
            'wait': data.get('wait') or False,
        }

        timeout_client_data = data.get('timeout_client_data')
        if timeout_client_data:
            listener['timeout_client_data'] = timeout_client_data

        timeout_member_data = data.get('timeout_member_data')
        if timeout_member_data:
            listener['timeout_member_data'] = timeout_member_data

        timeout_member_connect = data.get('timeout_member_connect')
        if timeout_member_connect:
            listener['timeout_member_connect'] = timeout_member_connect

        timeout_tcp_inspect = data.get('timeout_tcp_inspect')
        if timeout_tcp_inspect:
            listener['timeout_tcp_inspect'] = timeout_tcp_inspect

        connection_limit = data.get('connection_limit')
        if connection_limit:
            listener['connection_limit'] = connection_limit

        tags = data.get('tags')
        if tags:
            listener['tags'] = tags

        return self.do_create_listener(ctx, listener=listener)

    def do_create_listener(self, ctx, listener, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param listener:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=listener,
                                         func=functools.partial(os_client.create_listener, **listener),
                                         method=method,
                                         on_result=on_result or self.on_create_listener_result)

    def on_create_listener_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param listener_obj:
        :param result:
        :return:
        """
        task = ACTION_CREATE_LISTENER
        error, data = result
        if error:
            LOG.error('Failed to create listener: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.LISTENER_CREATE_FAILED, cause=error, status=400)
            return

        ctx.response = data
        return data

    def update_listener(self, ctx):
        """
        Do update a listener.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
            return

        data = ctx.data
        listener = {
            'id': data['listener_id'],
            'name': data.get('name'),
            'description': data.get('description'),
        }
        connection_limit = data.get('connection_limit')
        if connection_limit:
            listener['connection_limit'] = connection_limit

        tags = data.get('tags')
        if tags:
            listener['tags'] = tags

        return self.do_update_listener(ctx, listener=listener)

    def do_update_listener(self, ctx, listener, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param listener:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=listener,
                                         func=functools.partial(os_client.update_listener, **listener),
                                         method=method,
                                         on_result=on_result or self.on_update_listener_result)

    def on_update_listener_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param listener_obj:
        :param result
        :return:
        """
        task = ACTION_UPDATE_LB
        error, data = result
        if error:
            LOG.error('Failed to create listener: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.LISTENER_UPDATE_FAILED, cause=error, status=400)
            return

        ctx.response = data
        return data

    def delete_listener(self, ctx):
        """
        Do delete a listener.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
            return

        data = ctx.data
        listener = {
            'id': data['listener_id'],
        }
        return self.do_delete_listener(ctx, listener=listener)

    def do_delete_listener(self, ctx, listener, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param listener:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=listener,
                                         func=functools.partial(os_client.delete_listener, **listener),
                                         method=method,
                                         on_result=on_result or self.on_delete_listener_result)

    def on_delete_listener_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param listener_obj:
        :param result:
        :return:
        """
        task = ACTION_DELETE_LISTENER
        error, data = result
        if error:
            LOG.error('Failed to delete listener: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.LISTENER_DELETE_FAILED, cause=error, status=400)

        ctx.response = data
        return data

    def get_pool(self, ctx):
        """
        Get a pool being created.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_pool(ctx)

    def do_get_pool(self, ctx):
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

        error, pool = os_client.get_pool(pool_id=data['pool_id'], listing=listing)
        if error:
            ctx.set_error(errors.POOL_GET_FAILED, cause=error, status=404)
            return

        ctx.response = pool
        return pool

    def get_pools(self, ctx):
        """
        Get all pools created by user.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=LIST_ROLES):
            return

        return self.do_get_pools(ctx)

    def do_get_pools(self, ctx):
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

        error, pools = os_client.get_pools(listing=listing, **filters)
        if error:
            ctx.set_error(errors.POOL_GET_FAILED, cause=error, status=404)
            return
        ctx.response = pools
        return pools['data']

    def create_pool(self, ctx):
        """
        Do create new pool.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        data = ctx.data
        pool = {
            'name': data['name'],
            'description': data.get('description'),
            'protocol': data['protocol'],
            'lb_algorithm': data['lb_algorithm'],
            'wait': data.get('wait') or False,
        }

        listener_id = data.get('listener_id')
        lb_id = data.get('lb_id')
        if not lb_id and not listener_id:
            error = 'Either listener or load balancer must be specified'
            ctx.set_error(errors.POOL_CREATE_FAILED, error=error, status=400)
            return
        pool['listener_id'] = listener_id
        pool['lb_id'] = lb_id

        session_persistence = data.get('session_persistence')
        if session_persistence:
            pool['session_persistence'] = session_persistence

        tags = data.get('tags')
        if tags:
            pool['tags'] = tags

        return self.do_create_pool(ctx, pool=pool)

    def validate_create_pool(self, ctx):
        """
        Validate pool
        :param ctx:
        :return:
        """
        data = ctx.data

    def do_create_pool(self, ctx, pool, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param pool:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=pool,
                                         func=functools.partial(os_client.create_pool, **pool),
                                         method=method,
                                         on_result=on_result or self.on_create_pool_result)

    def on_create_pool_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param pool_obj:
        :param result:
        :return:
        """
        task = ACTION_CREATE_POOL
        error, data = result
        if error:
            LOG.error('Failed to create pool: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.POOL_CREATE_FAILED, cause=error, status=400)
            return

        ctx.response = data
        return data

    def update_pool(self, ctx):
        """
        Do update a pool.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
            return

        data = ctx.data
        pool = {
            'id': data['pool_id'],
            'name': data.get('name'),
            'description': data.get('description'),
        }

        lb_algorithm = data.get('lb_algorithm')
        if lb_algorithm:
            pool['lb_algorithm'] = lb_algorithm

        session_persistence = data.get('session_persistence')
        if session_persistence:
            pool['session_persistence'] = session_persistence

        tags = data.get('tags')
        if tags:
            pool['tags'] = tags

        return self.do_update_pool(ctx, pool=pool)

    def validate_update_pool(self, ctx):
        """
        Validate pool
        :param ctx:
        :return:
        """

    def do_update_pool(self, ctx, pool, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param pool:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=pool,
                                         func=functools.partial(os_client.update_pool, **pool),
                                         method=method,
                                         on_result=on_result or self.on_update_pool_result)

    def on_update_pool_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param pool_obj:
        :param result
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to create pool: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.POOL_UPDATE_FAILED, cause=error, status=400)
            return

        ctx.response = data
        return data

    def delete_pool(self, ctx):
        """
        Do delete a pool.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
            return

        data = ctx.data
        pool = {
            'id': data['pool_id'],
        }
        return self.do_delete_pool(ctx, pool=pool)

    def do_delete_pool(self, ctx, pool, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param pool:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=pool,
                                         func=functools.partial(os_client.delete_pool, **pool),
                                         method=method,
                                         on_result=on_result or self.on_delete_pool_result)

    def on_delete_pool_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param pool_obj:
        :param result:
        :return:
        """
        task = ACTION_CREATE_POOL
        error, data = result
        if error:
            LOG.error('Failed to delete pool: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.POOL_DELETE_FAILED, cause=error, status=400)

        ctx.response = data
        return data

    def get_pool_member(self, ctx):
        """
        Get a pool_member being created.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_pool_member(ctx)

    def do_get_pool_member(self, ctx):
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

        error, pool_member = os_client.get_pool_member(pool_id=data['pool_id'],
                                                       member_id=data['member_id'],
                                                       listing=listing)
        if error:
            ctx.set_error(errors.POOL_MEMBER_GET_FAILED, cause=error, status=404)
            return

        ctx.response = pool_member
        return pool_member

    def get_pool_members(self, ctx):
        """
        Get all pool_members created by user.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=LIST_ROLES):
            return

        return self.do_get_pool_members(ctx)

    def do_get_pool_members(self, ctx):
        """
        Subclass should override this method.
        :param ctx:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        data = ctx.data
        pool_id = data.get('pool_id')

        listing = self.parse_ctx_listing(ctx)
        filters = data.get('filters') or {}

        error, pool_members = os_client.get_pool_members(pool_id=pool_id, listing=listing, **filters)
        if error:
            ctx.set_error(errors.POOL_MEMBER_GET_FAILED, cause=error, status=404)
            return
        ctx.response = pool_members
        return pool_members['data']

    def create_pool_member(self, ctx):
        """
        Do create new pool_member.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        self.validate_create_pool_member(ctx)
        if ctx.failed:
            return

        data = ctx.data
        pool_member = {
            'name': data['name'],
            'pool_id': data['pool_id'],
            'address': data['address'],
            'port': data['port'],
            'weight': data.get('weight'),
            'wait': data.get('wait') or False,
        }
        monitor_address = data.get('monitor_address')
        if monitor_address:
            pool_member['monitor_address'] = monitor_address

        monitor_port = data.get('monitor_port')
        if monitor_port:
            pool_member['monitor_port'] = monitor_port

        tags = data.get('tags')
        if tags:
            pool_member['tags'] = tags

        return self.do_create_pool_member(ctx, pool_member=pool_member)

    def validate_create_pool_member(self, ctx):
        """
        Validate pool_member
        :param ctx:
        :return:
        """

    def do_create_pool_member(self, ctx, pool_member, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param pool_member:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=pool_member,
                                         func=functools.partial(os_client.create_pool_member, **pool_member),
                                         method=method,
                                         on_result=on_result or self.on_create_pool_member_result)

    def on_create_pool_member_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param pool_member_obj:
        :param result:
        :return:
        """
        task = ACTION_CREATE_POOL_MEMBER
        error, data = result
        if error:
            LOG.error('Failed to create pool_member: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.POOL_MEMBER_CREATE_FAILED, cause=error, status=400)
            return

        ctx.response = data
        return data

    def update_pool_member(self, ctx):
        """
        Do update a pool_member.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
            return

        data = ctx.data
        pool_member = {
            'id': data['member_id'],
            'name': data.get('name'),
        }

        pool_id = data.get('pool_id')
        if pool_id:
            pool_member['pool_id'] = pool_id

        weight = data.get('weight')
        if weight:
            pool_member['weight'] = weight

        monitor_address = data.get('monitor_address')
        if monitor_address:
            pool_member['monitor_address'] = monitor_address

        monitor_port = data.get('monitor_port')
        if monitor_port:
            pool_member['monitor_port'] = monitor_port

        tags = data.get('tags')
        if tags:
            pool_member['tags'] = tags

        return self.do_update_pool_member(ctx, pool_member=pool_member)

    def do_update_pool_member(self, ctx, pool_member, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param pool_member:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=pool_member,
                                         func=functools.partial(os_client.update_pool_member, **pool_member),
                                         method=method,
                                         on_result=on_result or self.on_update_pool_member_result)

    def on_update_pool_member_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param pool_member_obj:
        :param result
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to update pool_member: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.POOL_MEMBER_UPDATE_FAILED, cause=error, status=400)
            return

        ctx.response = data
        return data

    def delete_pool_member(self, ctx):
        """
        Do delete a pool_member.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
            return

        data = ctx.data
        pool_member = {
            'id': data['member_id'],
            'pool_id': data['pool_id'],
        }
        return self.do_delete_pool_member(ctx, pool_member=pool_member)

    def do_delete_pool_member(self, ctx, pool_member, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param pool_member:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=pool_member,
                                         func=functools.partial(os_client.delete_pool_member, **pool_member),
                                         method=method,
                                         on_result=on_result or self.on_delete_pool_member_result)

    def on_delete_pool_member_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param pool_member_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to delete pool_member: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.POOL_MEMBER_DELETE_FAILED, cause=error, status=500)

        ctx.response = data
        return data

    def get_monitor(self, ctx):
        """
        Get a monitor being created.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_monitor(ctx)

    def do_get_monitor(self, ctx):
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

        error, monitor = os_client.get_monitor(monitor_id=data['monitor_id'], listing=listing)
        if error:
            ctx.set_error(errors.MONITOR_GET_FAILED, cause=error, status=404)
            return

        ctx.response = monitor
        return monitor

    def get_monitors(self, ctx):
        """
        Get all monitors created by user.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=LIST_ROLES):
            return

        return self.do_get_monitors(ctx)

    def do_get_monitors(self, ctx):
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

        error, monitors = os_client.get_monitors(listing=listing, **filters)
        if error:
            ctx.set_error(errors.MONITOR_GET_FAILED, cause=error, status=404)
            return
        ctx.response = monitors
        return monitors['data']

    def create_monitor(self, ctx):
        """
        Do create new monitor.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        self.validate_create_monitor(ctx)
        if ctx.failed:
            return

        data = ctx.data
        monitor = {
            'name': data['name'],
            'pool_id': data['pool_id'],
            'delay': data['delay'],
            'timeout': data['timeout'],
            'http_method': data['http_method'],
            'max_retries': data['max_retries'],
            'max_retries_down': data['max_retries_down'],
            'url_path': data['url_path'],
            'expected_codes': data['expected_codes'],
            'wait': data.get('wait') or False,
        }
        tags = data.get('tags')
        if tags:
            monitor['tags'] = tags

        return self.do_create_monitor(ctx, monitor=monitor)

    def validate_create_monitor(self, ctx):
        """
        Validate monitor
        :param ctx:
        :return:
        """
        data = ctx.data
        vip_address = data.get('vip_address')
        if vip_address:
            if not net_util.validate_ipaddress(ip_address=vip_address):
                ctx.set_error(errors.MONITOR_CREATE_FAILED, error=errors.IP_INVALID, status=500)
                return

    def do_create_monitor(self, ctx, monitor, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param monitor:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=monitor,
                                         func=functools.partial(os_client.create_monitor, **monitor),
                                         method=method,
                                         on_result=on_result or self.on_create_monitor_result)

    def on_create_monitor_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param lb_obj:
        :param result:
        :return:
        """
        task = ACTION_CREATE_LB
        error, data = result
        if error:
            LOG.error('Failed to create monitor: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.MONITOR_CREATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def update_monitor(self, ctx):
        """
        Do update a monitor.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
            return

        data = ctx.data
        monitor = {
            'id': data['monitor_id'],
        }
        name = data.get('name')
        if name:
            monitor['name'] = name

        delay = data.get('delay')
        if delay:
            monitor['delay'] = delay

        expected_codes = data.get('expected_codes')
        if expected_codes:
            monitor['expected_codes'] = expected_codes

        http_method = data.get('http_method')
        if http_method:
            monitor['http_method'] = http_method

        max_retries = data.get('max_retries')
        if max_retries:
            monitor['max_retries'] = max_retries

        max_retries_down = data.get('max_retries_down')
        if max_retries_down:
            monitor['max_retries_down'] = max_retries_down

        url_path = data.get('url_path')
        if url_path:
            monitor['url_path'] = url_path

        tags = data.get('tags')
        if tags:
            monitor['tags'] = tags

        return self.do_update_monitor(ctx, monitor=monitor)

    def do_update_monitor(self, ctx, monitor, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param monitor:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=monitor,
                                         func=functools.partial(os_client.update_monitor, **monitor),
                                         method=method,
                                         on_result=on_result or self.on_update_monitor_result)

    def on_update_monitor_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param monitor_obj:
        :param result
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to create monitor: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.MONITOR_UPDATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def delete_monitor(self, ctx):
        """
        Do delete a monitor.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
            return

        data = ctx.data
        monitor = {
            'id': data['monitor_id'],
        }
        return self.do_delete_monitor(ctx, monitor=monitor)

    def do_delete_monitor(self, ctx, monitor, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param monitor:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=monitor,
                                         func=functools.partial(os_client.delete_monitor, **monitor),
                                         method=method,
                                         on_result=on_result or self.on_delete_monitor_result)

    def on_delete_monitor_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param monitor_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to delete monitor: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.MONITOR_DELETE_FAILED, cause=error, status=500)

        ctx.response = data
        return data


    def get_l7policy(self, ctx):
        """
        Get a l7policy being created.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_l7policy(ctx)

    def do_get_l7policy(self, ctx):
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

        error, l7policy = os_client.get_l7policy(l7policy_id=data['l7policy_id'], listing=listing)
        if error:
            ctx.set_error(errors.L7POLICY_GET_FAILED, cause=error, status=404)
            return

        ctx.response = l7policy
        return l7policy

    def get_l7policies(self, ctx):
        """
        Get all l7policies created by user.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=LIST_ROLES):
            return

        return self.do_get_l7policies(ctx)

    def do_get_l7policies(self, ctx):
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

        error, l7policies = os_client.get_l7policies(listing=listing, **filters)
        if error:
            ctx.set_error(errors.L7POLICY_GET_FAILED, cause=error, status=404)
            return
        ctx.response = l7policies
        return l7policies['data']

    def create_l7policy(self, ctx):
        """
        Do create new l7policy.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        self.validate_create_l7policy(ctx)
        if ctx.failed:
            return

        data = ctx.data
        l7policy = {
            'name': data['name'],
            'description': data.get('description'),
            'action': data['action'],
            'listener_id': data['listener_id'],
            'position': data['position'],
            'redirect_http_code': data.get('redirect_http_code'),
            'redirect_pool_id': data.get('redirect_pool_id'),
            'redirect_prefix': data.get('redirect_prefix'),
            'redirect_url': data.get('redirect_url'),
            'wait': data.get('wait') or False,
        }
        tags = data.get('tags')
        if tags:
            l7policy['tags'] = tags

        return self.do_create_l7policy(ctx, l7policy=l7policy)

    def do_create_l7policy(self, ctx, l7policy, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param l7policy:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=l7policy,
                                         func=functools.partial(os_client.create_l7policy, **l7policy),
                                         method=method,
                                         on_result=on_result or self.on_create_l7policy_result)

    def validate_create_l7policy(self, ctx):
        """
        Validata input of l7policy
        :param ctx:
        :return:
        """
        data = ctx.data
        action = data['action']
        if action != 'REDIRECT_TO_URL':
            if data.get('redirect_url'):
                error = 'Redirect url only valid if action is REDIRECT_TO_URL'
                ctx.set_error(errors.L7POLICY_CREATE_FAILED, cause=error, status=400)
                return
        else:
            if not data.get('redirect_url'):
                error = 'Redirect url is required if action is REDIRECT_TO_URL'
                ctx.set_error(errors.L7POLICY_CREATE_FAILED, cause=error, status=400)
                return

        if action in ['REDIRECT_TO_URL', 'REDIRECT_PREFIX']:
            if not data.get('redirect_http_code'):
                error = 'Redirect http code is required if action is REDIRECT_TO_URL or REDIRECT_PREFIX'
                ctx.set_error(errors.L7POLICY_CREATE_FAILED, cause=error, status=400)
                return


    def on_create_l7policy_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param l7policy_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to create l7policy: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.L7POLICY_CREATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def update_l7policy(self, ctx):
        """
        Do update a l7policy.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
            return

        data = ctx.data
        l7policy = {
            'id': data['l7policy_id'],
            'name': data.get('name'),
            'description': data.get('description'),
        }
        tags = data.get('tags')
        if tags:
            l7policy['tags'] = tags

        return self.do_update_l7policy(ctx, l7policy=l7policy)

    def do_update_l7policy(self, ctx, l7policy, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param l7policy:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=l7policy,
                                         func=functools.partial(os_client.update_l7policy, **l7policy),
                                         method=method,
                                         on_result=on_result or self.on_update_l7policy_result)

    def on_update_l7policy_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param l7policy_obj:
        :param result
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to create l7policy: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.L7POLICY_CREATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def delete_l7policy(self, ctx):
        """
        Do delete a l7policy.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
            return

        data = ctx.data
        l7policy = {
            'id': data['l7policy_id'],
        }
        return self.do_delete_l7policy(ctx, l7policy=l7policy)

    def do_delete_l7policy(self, ctx, l7policy, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param l7policy:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=l7policy,
                                         func=functools.partial(os_client.delete_l7policy, **l7policy),
                                         method=method,
                                         on_result=on_result or self.on_delete_l7policy_result)

    def on_delete_l7policy_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param l7policy_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to delete l7policy: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.L7POLICY_DELETE_FAILED, cause=error, status=500)

        ctx.response = data
        return data

    def get_l7rule(self, ctx):
        """
        Get a l7rule being created.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_l7rule(ctx)

    def do_get_l7rule(self, ctx):
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

        error, l7rule = os_client.get_l7rule(l7rule_id=data['l7rule_id'],
                                             l7policy_id=data['l7policy_id'],
                                             listing=listing)
        if error:
            ctx.set_error(errors.L7POLICY_RULE_GET_FAILED, cause=error, status=404)
            return

        ctx.response = l7rule
        return l7rule

    def get_l7rules(self, ctx):
        """
        Get all l7rules created by user.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=LIST_ROLES):
            return

        return self.do_get_l7rules(ctx)

    def do_get_l7rules(self, ctx):
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

        error, l7rules = os_client.get_l7rules(l7policy_id=data['l7policy_id'], listing=listing, **filters)
        if error:
            ctx.set_error(errors.L7POLICY_RULE_GET_FAILED, cause=error, status=404)
            return
        ctx.response = l7rules
        return l7rules['data']

    def create_l7rule(self, ctx):
        """
        Do create new l7rule.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        data = ctx.data
        l7rule = {
            'l7policy_id': data['l7policy_id'],
            'compare_type': data['compare_type'],
            'type': data['type'],
            'value': data['value'],
            'invert': data['invert'],
            'wait': True,
        }
        tags = data.get('tags')
        if tags:
            l7rule['tags'] = tags

        return self.do_create_l7rule(ctx, l7rule=l7rule)

    def do_create_l7rule(self, ctx, l7rule, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param l7rule:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=l7rule,
                                         func=functools.partial(os_client.create_l7rule, **l7rule),
                                         method=method,
                                         on_result=on_result or self.on_create_l7rule_result)

    def on_create_l7rule_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param l7rule_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to create l7rule: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.L7POLICY_RULE_CREATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def update_l7rule(self, ctx):
        """
        Do update a l7rule.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
            return

        data = ctx.data
        l7rule = {
            'l7rule_id': data['l7rule_id'],
            'l7policy_id': data['l7policy_id'],
            'compare_type': data['compare_type'],
            'type': data['type'],
            'value': data['value'],
            'invert': data['invert'],
        }
        tags = data.get('tags')
        if tags:
            l7rule['tags'] = tags

        return self.do_update_l7rule(ctx, l7rule=l7rule)

    def do_update_l7rule(self, ctx, l7rule, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param l7rule:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=l7rule,
                                         func=functools.partial(os_client.update_l7rule, **l7rule),
                                         method=method,
                                         on_result=on_result or self.on_update_l7rule_result)

    def on_update_l7rule_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param l7rule_obj:
        :param result
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to create l7rule: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.L7POLICY_RULE_UPDATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def delete_l7rule(self, ctx):
        """
        Do delete a l7rule.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
            return

        data = ctx.data
        l7rule = {
            'l7rule_id': data['l7rule_id'],
            'l7policy_id': data['l7policy_id'],
        }
        return self.do_delete_l7rule(ctx, l7rule=l7rule)

    def do_delete_l7rule(self, ctx, l7rule, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param l7rule:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, lb_obj=l7rule,
                                         func=functools.partial(os_client.delete_l7rule, **l7rule),
                                         method=method,
                                         on_result=on_result or self.on_delete_l7rule_result)

    def on_delete_l7rule_result(self, ctx, lb_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param l7rule_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to delete l7rule: {}. Error {}.'.format(lb_obj, error))
            ctx.set_error(errors.L7POLICY_RULE_DELETE_FAILED, cause=error, status=500)

        ctx.response = data
        return data

