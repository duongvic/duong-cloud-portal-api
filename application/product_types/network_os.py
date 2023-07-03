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

ADMIN_ROLES = (md.UserRole.ADMIN, md.UserRole.ADMIN_SALE, md.UserRole.ADMIN_IT)
GET_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
LIST_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
CREATE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)
UPDATE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)
DELETE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)


class OSNetwork(os_base.OSBase):
    """
    Openstack Network
    """

    def __init__(self):
        """
        Initialize Network
        """
        super().__init__()

        # Load config
        # net_config = md.query(md.Configuration,
        #                       type=md.ConfigurationType.NETWORK,
        #                       name='network_config',
        #                       status=md.ConfigurationStatus.ENABLED,
        #                       order_by=md.Configuration.version.desc()).first()
        # if not net_config:
        #     raise ValueError('Config NETWORK/net_config not found in database.')
        # self.net_config = net_config.contents

    @property
    def supported(self):
        return True

    def get_network(self, ctx):
        """
        Get a network being created.

        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_network(ctx)

    def do_get_network(self, ctx):
        """
        Do get a network
        :param ctx:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        data = ctx.data
        listing = self.parse_ctx_listing(ctx)
        error, network = os_client.get_network(network_id=data['network_id'], listing=listing)
        if error:
            ctx.set_error(errors.NET_GET_FAILED, cause=error, status=404)
            return

        ctx.response = network
        return network

    def get_networks(self, ctx):
        """
        Get all networks created by user.

        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=LIST_ROLES):
            return

        return self.do_get_networks(ctx)

    def do_get_networks(self, ctx):
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        listing = self.parse_ctx_listing(ctx)
        error, networks = os_client.get_networks(listing=listing)
        if error:
            ctx.set_error(errors.NET_GET_FAILED, cause=error, status=500)
            return

        ctx.response = networks
        return networks['data']

    def create_network(self, ctx):
        """
        Create a new network.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        self.validate_create_network(ctx)
        if ctx.failed:
            return

        data = ctx.data
        network = {
            'name': data['name'],
            'port_security_enabled': data.get('port_security_enabled'),
            'mtu_size': data.get('mtu_size') or 100,  # TODO
        }
        return self.do_create_network(ctx, network=network)

    def validate_create_network(self, ctx):
        """
        Validate network input
        :param ctx
        :return
        """
        data = ctx.data

        # Validate name
        if 'name' in data and not self.validate_network_name(ctx, name=data['name']):
            return
        # Validate mtu size
        if 'mtu_size' in data and not self.validate_network_mtu_size(ctx, mtu_size=data['mtu_size']):
            return
        return True

    def validate_network_name(self, ctx, name):
        """
        Validate network input
        :param ctx:
        :param name:
        :return:
        """
        name = name.strip() if name else None
        if not name or len(name) > 32:
            e = ValueError('Network name exceeds 32 characters length.')
            LOG.error(e)
            ctx.set_error(errors.NET_NAME_INVALID, cause=e, status=406)
            return
        ctx.data['name'] = name
        return True

    def validate_network_mtu_size(self, ctx, mtu_size):
        """
        Validate network input
        :param ctx:
        :param mtu_size:
        :return:
        """
        return True

    def _execute_client_func(self, ctx, net_obj, func, method, on_result):
        """
        Execute client func.
        :param ctx:
        :param net_obj:
        :param func:
        :param method:
        :param on_result:
        :return:
        """
        def _on_result(ctx, result):
            on_result(ctx=ctx, net_obj=net_obj, result=result)
            # Finish history log for the action (if there is)
            self.finish_action_log(ctx, error=result[0])

        self.execute_client_func(ctx, func=func, method=method, on_result=_on_result)

    def do_create_network(self, ctx, network, method='thread', on_result=None):
        """
        Subclass should override this.
        :param ctx:
        :param network:
        :param method:
        :param on_result:
        :return
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        params = {
            'name': network['name'],
            'port_security_enabled': network['port_security_enabled'],
            'mtu_size': network['mtu_size'],
        }
        return self._execute_client_func(ctx, net_obj=network,
                                         func=functools.partial(os_client.create_network, **params),
                                         method=method,
                                         on_result=on_result or self.on_create_network_result)

    def on_create_network_result(self, ctx, net_obj, result):
        """
        Create network callback.
        :param ctx:
        :param net_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Create network {} failed. Error {}.'.format(net_obj['name'], error))
        else:
            LOG.info('Create network {} succeeded. {}.'.format(net_obj['name'], str(data)))

    def update_network(self, ctx):
        """
        Update a network.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
            return

        self.validate_update_network(ctx)
        if ctx.failed:
            return

        data = ctx.data
        network = {
            'id': data['network_id'],
            'name': data['name'],
            'port_security_enabled': data.get('port_security_enabled'),
            'mtu_size': data.get('mtu_size') or 100  # TODO
        }
        return self.do_update_network(ctx, network=network)

    def validate_update_network(self, ctx):
        """
        Validate network input
        :param ctx
        :return
        """
        data = ctx.data

        # Validate name
        if 'name' in data and not self.validate_network_name(ctx, name=data['name']):
            return
        # Validate mtu size
        if 'mtu_size' in data and not self.validate_network_mtu_size(ctx, mtu_size=data['mtu_size']):
            return
        return True

    def do_update_network(self, ctx,network, method='thread', on_result=None):
        """
        Subclass should override this.
        :param ctx:
        :param network:
        :param method:
        :param on_result:
        :return
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, net_obj=network,
                                         func=functools.partial(os_client.update_network, **network),
                                         method=method,
                                         on_result=on_result or self.on_update_network_result)

    def on_update_network_result(self, ctx, net_obj, result):
        """
        Update network callback.
        :param ctx:
        :param network:
        :param net_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Update network {} failed. Error {}.'.format(net_obj['id'], error))
        else:
            LOG.info('Update network {} succeeded. {}.'.format(net_obj['id'], str(data)))

    def delete_network(self, ctx):
        """
        Delete a network.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
            return

        data = ctx.data
        network = {
            'id': data['network_id'],
        }
        return self.do_delete_network(ctx, network=network)

    def do_delete_network(self, ctx, network, method='thread', on_result=None):
        """
        Do delete network.
        :param ctx:
        :param network:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        params = {
            'id': network['id'],
        }
        return self._execute_client_func(ctx, net_obj=network,
                                         func=functools.partial(os_client.delete_network, **params),
                                         method=method,
                                         on_result=on_result or self.on_delete_network_result)

    def on_delete_network_result(self, ctx, net_obj, result):
        """
        Delete network callback.
        :param ctx:
        :param net_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Delete network {} failed. Error {}.'.format(net_obj['id'], error))
        else:
            LOG.info('Delete network {} succeeded. {}.'.format(net_obj['id'], str(data)))

    def get_subnet(self, ctx):
        """
        Get a subnet being created.

        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_subnet(ctx)

    def do_get_subnet(self, ctx):
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        data = ctx.data
        listing = self.parse_ctx_listing(ctx)
        error, subnet = os_client.get_subnet(subnet_id=data['subnet_id'],
                                             network_id=data['network_id'],
                                             listing=listing)
        if error:
            ctx.set_error(errors.SUBNET_GET_FAILED, cause=error, status=500)
            return

        ctx.response = subnet
        return subnet

    def get_subnets(self, ctx):
        """
        Get all subnets created by user.

        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=LIST_ROLES):
            return

        return self.do_get_subnets(ctx)

    def do_get_subnets(self, ctx):
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        data = ctx.data
        listing = self.parse_ctx_listing(ctx)
        error, subnets = os_client.get_subnets(network_id=data.get('network_id'), listing=listing)
        if error:
            ctx.set_error(errors.SUBNET_GET_FAILED, cause=error, status=404)
            return

        ctx.response = subnets
        return subnets['data']

    def create_subnet(self, ctx):
        """
        Create a new subnet.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        self.validate_subnet_args(ctx)
        if ctx.failed:
            return

        data = ctx.data
        subnet = {
            'network_id': data['network_id'],
            'name': data['name'],
            'cidr': data.get('cidr'),
            'enable_dhcp': data.get('enable_dhcp'),
            'allocation_pools': data.get('allocation_pools'),
            'ip_version': data['ip_version'],
            'disable_gateway_ip': data.get('disable_gateway_ip'),
            'gateway_ip': data.get('gateway_ip'),
        }
        return self.do_create_subnet(ctx, subnet=subnet)

    def do_create_subnet(self, ctx, subnet, method='thread', on_result=None):
        """
        Subclass should override this.
        :param ctx:
        :param subnet:
        :param method:
        :param on_result:
        :return
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, net_obj=subnet,
                                         func=functools.partial(os_client.create_subnet, **subnet),
                                         method=method,
                                         on_result=on_result or self.on_create_subnet_result)

    def on_create_subnet_result(self, ctx, net_obj, result):
        """
        Create subnet callback.
        :param ctx:
        :param net_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Create subnet {}/{} failed. Error {}.'.format(net_obj['network_id'], net_obj['name'], error))
        else:
            LOG.info('Create subnet {}/{} succeeded. {}.'.format(net_obj['network_id'], net_obj['name'], str(data)))

    def validate_subnet_args(self, ctx, for_update=False):
        """
        Validate subnet.
        :param ctx:
        :param for_update:
        :return:
        """
        data = ctx.data

        if 'allocation_pools' in data:
            for pool in data['allocation_pools']:
                start = pool.get('start')
                end = pool.get('end')
                if not start or not end:
                    ctx.set_error(error=errors.SUBNET_POOL_INVALID, status=406)
                    return

                if not ipaddress.ip_address(start) and not ipaddress.ip_address(end):
                    ctx.set_error(error=errors.SUBNET_POOL_INVALID, status=406)
                    return

        disable_gateway_ip = data.get('disable_gateway_ip')
        if not disable_gateway_ip:
            gateway_ip = data.get('gateway_ip')
            if not ipaddress.ip_address(gateway_ip):
                ctx.set_error(error=errors.SUBNET_GATEWAY_INVALID, cause='Gateway IP is required', status=406)
                return
        else:
            if data.get('gateway_ip'):
                data['gateway_ip'] = None

        return True

    def update_subnet(self, ctx):
        """
        Create a new subnet.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
            return

        self.validate_subnet_args(ctx)
        if ctx.failed:
            return

        data = ctx.data
        subnet = {
            'id': data['subnet_id'],
            'name': data.get('name'),
            'enable_dhcp': data.get('enable_dhcp'),
            'allocation_pools': data.get('allocation_pools'),
            'disable_gateway_ip': data.get('disable_gateway_ip') or True,
            'gateway_ip': data.get('gateway_ip'),
        }
        return self.do_update_subnet(ctx, subnet=subnet)

    def do_update_subnet(self, ctx, subnet, method='thread', on_result=None):
        """
        Do update a subnet.
        :param ctx:
        :param subnet:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        params = dict(id=subnet['id'],
                      name=subnet.get('name'),
                      enable_dhcp=subnet.get('enable_dhcp'),
                      allocation_pools=subnet.get('allocation_pools'),
                      disable_gateway_ip=subnet.get('disable_gateway_ip'),
                      gateway_ip=subnet.get('gateway_ip'))
        return self._execute_client_func(ctx, net_obj=subnet,
                                         func=functools.partial(os_client.update_subnet, **params),
                                         method=method,
                                         on_result=on_result or self.on_update_subnet_result)

    def on_update_subnet_result(self, ctx, net_obj, result):
        """
        Update subnet callback.
        :param ctx:
        :param net_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Update subnet {} failed. Error {}.'.format(net_obj['id'], error))
        else:
            LOG.info('Update subnet {} succeeded. {}.'.format(net_obj['id'], str(data)))

    def delete_subnet(self, ctx):
        """
        Delete a subnet.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
            return

        data = ctx.data
        subnet = {
            'id': data['subnet_id'],
        }
        return self.do_delete_subnet(ctx, subnet=subnet)

    def do_delete_subnet(self, ctx, subnet, method='thread', on_result=None):
        """
        Delete a subnet.
        :param ctx:
        :param subnet:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        params = dict(id=subnet['id'])
        return self._execute_client_func(ctx, net_obj=subnet,
                                         func=functools.partial(os_client.delete_subnet, **params),
                                         method=method,
                                         on_result=on_result or self.on_delete_subnet_result)

    def on_delete_subnet_result(self, ctx, net_obj, result):
        """
        Delete subnet callback.
        :param ctx:
        :param net_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Delete subnet {} failed. Error {}.'.format(net_obj['id'], error))
        else:
            LOG.info('Delete subnet {} succeeded. {}.'.format(net_obj['id'], str(data)))

    #################################################
    # Router
    #################################################
    def get_router(self, ctx):
        """
        Get a router being created.

        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_router(ctx)

    def do_get_router(self, ctx):
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        data = ctx.data
        error, router = os_client.get_router(router_id=data['router_id'])
        if error:
            ctx.set_error(errors.ROUTER_GET_FAILED, cause=error, status=500)
            return

        ctx.response = router
        return router

    def get_routers(self, ctx):
        """
        Get all routers created by user.

        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=LIST_ROLES):
            return

        return self.do_get_routers(ctx)

    def do_get_routers(self, ctx):
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        listing = self.parse_ctx_listing(ctx)
        error, routers = os_client.get_routers(listing=listing)
        if error:
            ctx.set_error(errors.ROUTER_GET_FAILED, cause=error, status=404)
            return

        ctx.response = routers
        return routers['data']

    def create_router(self, ctx):
        """
        Create a new router.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        if ctx.failed:
            return

        data = ctx.data
        router = {
            'name': data['name'],
            'ext_gateway_net_id': data.get('ext_gateway_net_id'),
            'enable_snat': data.get('enable_snat'),
        }
        return self.do_create_router(ctx, router=router)

    def do_create_router(self, ctx, router, method='thread', on_result=None):
        """
        :param ctx:
        :param router:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, net_obj=router,
                                         func=functools.partial(os_client.create_router, **router),
                                         method=method,
                                         on_result=on_result or self.on_create_router_result)

    def on_create_router_result(self, ctx, net_obj, result):
        """
        Create router callback.
        :param ctx:
        :param router_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Create router {} failed. Error {}.'.format(net_obj['name'], error))
        else:
            LOG.info('Create router {} succeeded. {}.'.format(net_obj['name'], str(data)))

    def validate_router_args(self, ctx, for_update=False):
        """
        Validate router.
        :param ctx:
        :param for_update:
        :return:
        """
        data = ctx.data

        if 'cidr' in data:
            if not ipaddress.ip_network(data['cidr']):
                ctx.set_error(error=errors.router_CIDR_INVALID, status=406)
                return

        if 'allocation_pools' in data:
            for pool in data['allocation_pools']:
                start = pool['start']
                end = pool['end']
                if not ipaddress.ip_address(start) and not ipaddress.ip_address(end):
                    ctx.set_error(error=errors.router_POOL_INVALID, status=406)
                    return

        disable_gateway_ip = data.get('disable_gateway_ip')
        if not disable_gateway_ip:
            gateway_ip = data.get('gateway_ip')
            if not ipaddress.ip_address(gateway_ip):
                ctx.set_error(error=errors.router_GATEWAY_INVALID, cause='router gateway required', status=406)
                return
        else:
            if data.get('gateway_ip'):
                LOG.warning("gateway_ip is not set when disable_gateway_ip is disable")

        return True

    def update_router(self, ctx):
        """
        Create a new router.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
            return

        data = ctx.data
        router = {
            'id': data['router_id'],
            'name': data['name'],
            'ext_gateway_net_id': data.get('ext_gateway_net_id'),
            'enable_snat': data.get('enable_snat'),
        }
        return self.do_update_router(ctx, router=router)

    def do_update_router(self, ctx, router, method='thread', on_result=None):
        """
        Do update a router.
        :param ctx:
        :param router:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, net_obj=router,
                                         func=functools.partial(os_client.update_router, **router),
                                         method=method,
                                         on_result=on_result or self.on_update_router_result)

    def on_update_router_result(self, ctx, net_obj, result):
        """
        Update router callback.
        :param ctx:
        :param net_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Update router {} failed. Error {}.'.format(net_obj['id'], error))
        else:
            LOG.info('Update router {} succeeded. {}.'.format(net_obj['id'], str(data)))

    def delete_router(self, ctx):
        """
        Delete a router.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
            return

        data = ctx.data
        router = {
            'id': data['router_id'],
        }
        return self.do_delete_router(ctx, router=router)

    def do_delete_router(self, ctx, router, method='thread', on_result=None):
        """
        Delete a router.
        :param ctx:
        :param router:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        params = dict(id=router['id'])
        return self._execute_client_func(ctx, net_obj=router,
                                         func=functools.partial(os_client.delete_router, **params),
                                         method=method,
                                         on_result=on_result or self.on_delete_router_result)

    def on_delete_router_result(self, ctx, net_obj, result):
        """
        Delete router callback.
        :param ctx:
        :param net_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Delete router {} failed. Error {}.'.format(net_obj['id'], error))
        else:
            LOG.info('Delete router {} succeeded. {}.'.format(net_obj['id'], str(data)))

    #################################################
    # Router Interface
    #################################################
    def update_router_interface(self, ctx):
        """
        Create a new router_interface.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
            return

        data = ctx.data
        router_interface = {
            'router_id': data['router_id'],
            'subnet_id': data.get('subnet_id'),
            'port_id': data.get('port_id'),
        }
        return self.do_update_router_interface(ctx, router_interface=router_interface)

    def do_update_router_interface(self, ctx, router_interface, method='sync', on_result=None):
        """
        Do update a router_interface.
        :param ctx:
        :param router_interface:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, net_obj=router_interface,
                                         func=functools.partial(os_client.add_router_interface, **router_interface),
                                         method=method,
                                         on_result=on_result or self.on_update_router_interface_result)

    def on_update_router_interface_result(self, ctx, net_obj, result):
        """
        Update router_interface callback.
        :param ctx:
        :param net_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Update router_interface {} failed. Error {}.'.format(net_obj['router_id'], error))
            ctx.set_error(errors.COMPUTE_ROUTE_INTERFACE_DELETE_FAILED, cause=error, status=500)
        else:
            LOG.info('Update router_interface {} succeeded. {}.'.format(net_obj['router_id'], str(data)))
            ctx.response = data
            return data

    def delete_router_interface(self, ctx):
        """
        Delete a router_interface.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
            return

        data = ctx.data
        router_interface = {
            'router_id': data['router_id'],
            'subnet_id': data.get('subnet_id'),
            'port_id': data.get('port_id'),
        }
        return self.do_delete_router_interface(ctx, router_interface=router_interface)

    def do_delete_router_interface(self, ctx, router_interface, method='sync', on_result=None):
        """
        Delete a router_interface.
        :param ctx:
        :param router_interface:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, net_obj=router_interface,
                                         func=functools.partial(os_client.delete_router_interface, **router_interface),
                                         method=method,
                                         on_result=on_result or self.on_delete_router_interface_result)

    def on_delete_router_interface_result(self, ctx, net_obj, result):
        """
        Delete router_interface callback.
        :param ctx:
        :param net_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Delete router_interface {} failed. Error {}.'.format(net_obj['router_id'], error))
            ctx.set_error(errors.COMPUTE_ROUTE_INTERFACE_DELETE_FAILED, cause=error, status=500)
        else:
            LOG.info('Delete router_interface {} succeeded. {}.'.format(net_obj['router_id'], str(data)))
            ctx.response = data
            return data

    #######################################################
    # SEC GROUP
    #######################################################

    def get_secgroup(self, ctx):
        """
        Get a secgroup being created.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_secgroup(ctx)

    def do_get_secgroup(self, ctx):
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

        error, sec_group = os_client.get_security_group(id=data['secgroup_id'])
        if error:
            ctx.set_error(errors.SG_GET_FAILED, cause=error, status=404)
            return

        rules = []
        if sec_group:
            rules = self._parse_secgroup_rules(sec_group.get('security_group_rules') or [])
        response = {
            'id': sec_group['id'],
            'name': sec_group.get('name'),
            'description': sec_group.get('description'),
            'rules': rules
        }
        ctx.response = response
        return response

    def _parse_secgroup_rules(self, sg_rules):
        """
        """
        rules = []
        for rule in sg_rules:
            rules.append(self._parse_secgroup_rule(rule))
        return rules

    def _parse_secgroup_rule(self, rule):
        if rule:
            port_range_min = rule.get('port_range_min')
            port_range_max = rule.get('port_range_max')
            port_range = 'Any' if not (port_range_min and port_range_max) \
                else '{}:{}'.format(port_range_min, port_range_max)
            remote_ip_prefix = rule.get('remote_ip_prefix')
            return {
                'id': rule['id'],
                'direction': rule.get('direction') or 'Any',
                'ether_type': rule.get('ethertype', 'Any'),
                'port_range': port_range,
                'source_ip': remote_ip_prefix or 'Any',
                'protocol': rule.get('protocol') or 'Any',
            }
        return None

    def get_secgroups(self, ctx):
        """
        Get all secgroups created by user.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=LIST_ROLES):
            return

        return self.do_get_secgroups(ctx)

    def do_get_secgroups(self, ctx):
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

        error, secgroups = os_client.get_security_groups(listing=listing, **filters)
        if error:
            ctx.set_error(errors.SG_GET_FAILED, cause=error, status=404)
            return
        ctx.response = secgroups
        return secgroups['data']

    def create_secgroup(self, ctx):
        """
        Do create new secgroup.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        self.validate_create_secgroup(ctx)
        if ctx.failed:
            return

        data = ctx.data
        secgroup = {
            'name': data['name'],
            'description': data.get('description'),
        }

        return self.do_create_secgroup(ctx, secgroup=secgroup)

    def validate_create_secgroup(self, ctx):
        """
        Validate secgroup
        :param ctx:
        :return:
        """

    def do_create_secgroup(self, ctx, secgroup, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param secgroup:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, net_obj=secgroup,
                                         func=functools.partial(os_client.create_security_group, **secgroup),
                                         method=method,
                                         on_result=on_result or self.on_create_secgroup_result)

    def on_create_secgroup_result(self, ctx, net_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param secgroup_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to create secgroup: {}. Error {}.'.format(net_obj, error))
            ctx.set_error(errors.SG_CREATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def update_secgroup(self, ctx):
        """
        Do update a secgroup.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
            return

        data = ctx.data
        secgroup = {
            'id': data['secgroup_id'],
            'name': data.get('name'),
            'description': data.get('description'),
        }

        return self.do_update_secgroup(ctx, secgroup=secgroup)

    def do_update_secgroup(self, ctx, secgroup, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param secgroup:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, net_obj=secgroup,
                                         func=functools.partial(os_client.update_security_group, **secgroup),
                                         method=method,
                                         on_result=on_result or self.on_update_secgroup_result)

    def on_update_secgroup_result(self, ctx, net_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param secgroup_obj:
        :param result
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to create secgroup: {}. Error {}.'.format(net_obj, error))
            ctx.set_error(errors.SG_UPDATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def delete_secgroup(self, ctx):
        """
        Do delete a secgroup.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
            return

        data = ctx.data
        secgroup = {
            'id': data['secgroup_id'],
        }
        return self.do_delete_secgroup(ctx, secgroup=secgroup)

    def do_delete_secgroup(self, ctx, secgroup, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param secgroup:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, net_obj=secgroup,
                                         func=functools.partial(os_client.delete_security_group, **secgroup),
                                         method=method,
                                         on_result=on_result or self.on_delete_secgroup_result)

    def on_delete_secgroup_result(self, ctx, net_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param secgroup_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to delete secgroup: {}. Error {}.'.format(net_obj, error))
            ctx.set_error(errors.SG_DELETE_FAILED, cause=error, status=500)

        ctx.response = data
        return data

    def get_secgroup_rule(self, ctx):
        """
        Get a secgroup_rule being created.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_secgroup_rule(ctx)

    def do_get_secgroup_rule(self, ctx):
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

        error, secgroup_rule = os_client.get_security_group_rule(id=data['rule_id'], listing=listing)
        if error:
            ctx.set_error(errors.SG_RULE_GET_FAILED, cause=error, status=404)
            return

        ctx.response = secgroup_rule
        return secgroup_rule

    def get_secgroup_rules(self, ctx):
        """
        Get all secgroup_rules created by user.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=LIST_ROLES):
            return

        return self.do_get_secgroup_rules(ctx)

    def do_get_secgroup_rules(self, ctx):
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
        filters['security_group_id'] = data['secgroup_id']

        error, secgroup_rules = os_client.get_security_group_rules(listing=listing, **filters)
        if error:
            ctx.set_error(errors.SG_RULE_GET_FAILED, cause=error, status=404)
            return
        ctx.response = secgroup_rules
        return secgroup_rules['data']

    def create_secgroup_rule(self, ctx):
        """
        Do create new secgroup_rule.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        self.validate_create_secgroup_rule(ctx)
        if ctx.failed:
            return

        data = ctx.data
        port_range = data['port_range']
        if port_range:
            port_range_arr = port_range.split(":")
            max_port = int(port_range_arr[1])
            min_port = int(port_range_arr[0])
            if (min_port > max_port) or (min_port < 1) and (max_port > 65535):
                LOG.warning("Ports out of ranger %s", port_range)
                raise Exception("Ports out of ranger %s", port_range)
        else:
            raise Exception("Ports out of ranger %s", port_range)

        secgroup_rule = {
            'secgroup_id': data['secgroup_id'],
            'protocol': data['protocol'],
            'direction': data['direction'],
            'ethertype': data['ether_type'],
            'port_range_max': max_port,
            'port_range_min': min_port,
            'remote_ip_prefix': data['source_ip']
        }
        return self.do_create_secgroup_rule(ctx, secgroup_rule=secgroup_rule)

    def validate_create_secgroup_rule(self, ctx):
        """
        Validate secgroup_rule
        :param ctx:
        :return:
        """

    def do_create_secgroup_rule(self, ctx, secgroup_rule, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param secgroup_rule:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, net_obj=secgroup_rule,
                                         func=functools.partial(os_client.create_security_group_rule, info=secgroup_rule),
                                         method=method,
                                         on_result=on_result or self.on_create_secgroup_rule_result)

    def on_create_secgroup_rule_result(self, ctx, net_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param secgroup_rule_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to create secgroup_rule: {}. Error {}.'.format(net_obj, error))
            ctx.set_error(errors.SG_RULE_CREATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def update_secgroup_rule(self, ctx):
        """
        Do update a secgroup_rule.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
            return

        data = ctx.data
        secgroup_rule = {

        }

        return self.do_update_secgroup_rule(ctx, secgroup_rule=secgroup_rule)

    def do_update_secgroup_rule(self, ctx, secgroup_rule, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param secgroup_rule:
        :param method:
        :param on_result:
        :return:
        """
        # os_client = self.get_os_client(ctx)
        # if ctx.failed:
        #     return
        #
        # return self._execute_client_func(ctx, net_obj=secgroup_rule,
        #                                  func=functools.partial(os_client.update_secgroup_rule, **secgroup_rule),
        #                                  method=method,
        #                                  on_result=on_result or self.on_update_secgroup_rule_result)

    def on_update_secgroup_rule_result(self, ctx, net_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param secgroup_rule_obj:
        :param result
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to create secgroup_rule: {}. Error {}.'.format(net_obj, error))
            ctx.set_error(errors.SG_RULE_UPDATE_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def delete_secgroup_rule(self, ctx):
        """
        Do delete a secgroup_rule.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
            return

        data = ctx.data
        secgroup_rule = {
            'id': data['rule_id'],
        }
        return self.do_delete_secgroup_rule(ctx, secgroup_rule=secgroup_rule)

    def do_delete_secgroup_rule(self, ctx, secgroup_rule, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param secgroup_rule:
        :param method:
        :param on_result:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, net_obj=secgroup_rule,
                                         func=functools.partial(os_client.delete_security_group_rule, **secgroup_rule),
                                         method=method,
                                         on_result=on_result or self.on_delete_secgroup_rule_result)

    def on_delete_secgroup_rule_result(self, ctx, net_obj, result):
        """
        Subclass should override this method.
        :param ctx:
        :param secgroup_rule_obj:
        :param result:
        :return:
        """
        error, data = result
        if error:
            LOG.error('Failed to delete secgroup_rule: {}. Error {}.'.format(net_obj, error))
            ctx.set_error(errors.SG_RULE_DELETE_FAILED, cause=error, status=500)

        ctx.response = data
        return data


