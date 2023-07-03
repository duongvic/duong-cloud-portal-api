#
# Copyright (c) 2020 FTI-CAS
#

from foxcloud import exceptions as fox_exc

from application import app
from application.utils.data_util import valid_kwargs

LOG = app.logger


class OSNetworkMixin(object):

    def get_network_quotas(self, project_id, details=False, listing={}):
        """
        Delete quota for a network
        :param project_id:
        :param details:
        :returns:
        """
        try:
            q = self.client.shade.get_network_quotas(name_or_id=project_id, details=details)
            return self.parse(q, **listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_network_quotas(%s)]: %s.", project_id, e)
            return self.fail(e)

    @valid_kwargs('floatingip', 'network', 'port', 'rbac_policy', 'router',
                  'security_group', 'security_group_rule', 'subnet', 'subnetpool')
    def set_network_quotas(self, project_id, listing={}, **kwargs):
        """
        Set a network quota in a project

        :param project_id: project name or id
        :param kwargs: key/value pairs of quota name and quota value
        """
        try:
            q = self.client.shade.set_network_quotas(name_or_id=project_id, **kwargs)
            return self.parse(q, **listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [set_network_quotas(%s)]: %s.", project_id, e)
            return self.fail(e)

    def get_network(self, network_id, listing={}, filters={}):
        """
        Get a specific network
        :param network_id:
        :param filters:
        :return:
        """
        try:
            data = self.client.shade.get_neutron_network(network_id=network_id,
                                                         **filters)
            return data.parse(extra_field_getter=self._get_network_extra_field, **listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_networks()]: %s.", e)
            return self.fail(e)

    def _get_network_extra_field(self, network, field):
        if field == 'subnets':
            subnets = []
            for subnet_id in network['subnets'] or []:
                result = self.client.shade.get_neutron_subnet(subnet_id=subnet_id)
                err, data = result.parse()
                if err:
                    return self.fail(err)
                subnets.append(data)
            return None, subnets

        return self.fail('Unknown extra field "%s".' % field)

    def get_networks(self, listing={}, filters={}):
        try:
            data = self.client.shade.get_neutron_networks(**filters)
            return data.parse(extra_field_getter=self._get_network_extra_field, **listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_networks()]: %s.", e)
            return self.fail(e)

    def create_network(self, name, shared=False, port_security_enabled=True,
                       admin_state_up=True, external=False, provider=None,
                       project_id=None, mtu_size=None):
        """
        Create a neutron network.

        :param name:
        :param shared:
        :param port_security_enabled:
        :param admin_state_up:
        :param external:
        :param provider:
        :param project_id:
        :param mtu_size:
        :returns: Network object
        """
        try:
            data = self.client.shade.create_neutron_network(name=name, shared=shared,
                                                            admin_state_up=admin_state_up,
                                                            port_security_enabled=port_security_enabled,
                                                            mtu_size=mtu_size, external=external,
                                                            provider=provider, project_id=project_id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_network(%s)]: %s.", name, e)
            return self.fail(e)

    def update_network(self, id, name, shared=False, port_security_enabled=True,
                       admin_state_up=True, external=False, provider=None,
                       project_id=None, mtu_size=None, availability_zone_hints=None):

        try:
            data = self.client.shade.update_neutron_network(network_id=id,
                                                            name=name,
                                                            shared=shared,
                                                            admin_state_up=admin_state_up,
                                                            external=external,
                                                            provider=provider,
                                                            project_id=project_id,
                                                            availability_zone_hints=availability_zone_hints,
                                                            port_security_enabled=port_security_enabled,
                                                            mtu_size=mtu_size)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_network(%s)]: %s.", id, e)
            return self.fail(e)

    def delete_network(self, id):
        """
        Delete a network being created

        :param id
        :return
        """
        try:
            data = self.client.shade.delete_neutron_network(id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_network(%s)]: %s.", id, e)
            return self.fail(e)

    def get_subnet(self, subnet_id, network_id=None, listing={}, filters={}):
        """
        Get a specific subnet
        :param subnet_id:
        :param network_id:
        :param filters:
        :return:
        """
        try:
            data = self.client.shade.get_neutron_subnet(subnet_id=subnet_id, **filters)
            error, result = data.parse(**listing)
            if not error:
                if result['network_id'] == network_id:
                    return None, result
                else:
                    return None, {}
            return error, result
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_subnet(%s)]: %s.", subnet_id, e)
            return self.fail(e)

    def get_subnets(self, network_id=None, listing={}):
        """
        List all subnets
        :param network_id:
        :param listing:
        :return:
        """
        try:
            filters = {}
            if network_id:
                filters['network_id'] = network_id
            data = self.client.shade.get_neutron_subnets(**filters)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_subnets()]: %s.", e)
            return self.fail(e)

    def create_subnet(self, network_id, name, cidr, ip_version=4, enable_dhcp=True,
                      tenant_id=None, allocation_pools=None, gateway_ip=None,
                      disable_gateway_ip=True, dns=None, host_routes=None,
                      ipv6_ra_mode=None, ipv6_address_mode=None, default_subnet_pool=None):

        try:
            data = self.client.shade.create_neutron_subnet(network_id=network_id,
                                                           cidr=cidr,
                                                           ip_version=ip_version,
                                                           enable_dhcp=enable_dhcp,
                                                           name=name,
                                                           tenant_id=tenant_id,
                                                           allocation_pools=allocation_pools,
                                                           gateway_ip=gateway_ip,
                                                           disable_gateway_ip=disable_gateway_ip,
                                                           dns=dns, host_routes=host_routes,
                                                           ipv6_ra_mode=ipv6_ra_mode,
                                                           ipv6_address_mode=ipv6_address_mode,
                                                           default_subnet_pool=default_subnet_pool)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_neutron_subnet(%s)]: %s.", network_id, e)
            return self.fail(e)

    def update_subnet(self, id, name, enable_dhcp=None, gateway_ip=None,
                      disable_gateway_ip=None, allocation_pools=None,
                      dns=None, host_routes=None):
        try:
            data = self.client.shade.update_neutron_subnet(subnet_id=id, name=name,
                                                           enable_dhcp=enable_dhcp,
                                                           gateway_ip=gateway_ip,
                                                           disable_gateway_ip=disable_gateway_ip,
                                                           allocation_pools=allocation_pools,
                                                           dns=dns,
                                                           host_routes=host_routes)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [update_subnet(%s)]: %s.", id, e)
            return self.fail(e)

    def delete_subnet(self, id):
        """
        Delete a specific subnet
        :param id:
        :return:
        """
        try:
            data = self.client.shade.delete_neutron_subnet(id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_subnet(%s)]: %s.", id, e)
            return self.fail(e)

    def get_router(self, router_id, listing={}, filters={}):
        """
        Get a specific router
        :param router_id:
        :param filters:
        :return:
        """
        try:
            data = self.client.shade.get_neutron_router(router_id=router_id, **filters)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_router(%s)]: %s.", router_id, e)
            return self.fail(e)

    def get_routers(self, listing={}, filters={}):
        """
        List all routers
        :param listing:
        :param filters:
        :return:
        """
        try:
            data = self.client.shade.get_neutron_routers(**filters)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_routers()]: %s.", e)
            return self.fail(e)

    def create_router(self, name=None, admin_state_up=True,
                      ext_gateway_net_id=None, enable_snat=None,
                      ext_fixed_ips=None, project_id=None,
                      availability_zone_hints=None):
        """
        Create a new router
        :param name:
        :param admin_state_up:
        :param ext_gateway_net_id:
        :param enable_snat:
        :param ext_fixed_ips:
        :param project_id:
        :param availability_zone_hints:
        :return:
        """
        try:
            data = self.client.shade.create_neutron_router(name=name, admin_state_up=admin_state_up,
                                                           ext_gateway_net_id=ext_gateway_net_id,
                                                           enable_snat=enable_snat,
                                                           ext_fixed_ips=ext_fixed_ips,
                                                           project_id=project_id,
                                                           availability_zone_hints=availability_zone_hints)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_neutron_router(%s)]: %s.", name, e)
            return self.fail(e)

    def update_router(self, id, name=None, admin_state_up=True,
                      ext_gateway_net_id=None, enable_snat=True,
                      ext_fixed_ips=None, routes=None, revision_number=None):
        try:
            data = self.client.shade.update_neutron_router(router_id=id,
                                                           name=name,
                                                           admin_state_up=admin_state_up,
                                                           ext_gateway_net_id=ext_gateway_net_id,
                                                           enable_snat=enable_snat,
                                                           ext_fixed_ips=ext_fixed_ips,
                                                           routes=routes,
                                                           revision_number=revision_number)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_neutron_router(%s)]: %s.", name, e)
            return self.fail(e)

    def delete_router(self, id):
        """
        Delete a neutron router
        :param id: ID of the Router
        :return:
        """
        try:
            data = self.client.shade.delete_neutron_router(id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_router(%s)]: %s.", id, e)
            return self.fail(e)

    def delete_gateway_router(self, router_id):
        """
        Delete gateway route
        :param router_id
        :return
        """
        try:
            data = self.client.shade.remove_gateway_router(router_id)
            return data.parse()
        except Exception as e:
            LOG.error("Error [delete_gateway_router(%s)]: %s.", router_id, e)
            return self.fail(e)

    def get_port(self, port_id, listing={}, filters={}):
        """
        Get a specific port
        :param port_id:
        :param filters:
        :return:
        """
        try:
            data = self.client.shade.get_neutron_port(port_id=port_id, **filters)
            return data.parse(**listing)
        except Exception as e:
            LOG.error("Error [get_port(%s)]: %s.", port_id, e)
            return self.fail(e)

    def get_ports(self, listing={}, filters={}):
        """
        List all ports
        :param filters:
        :return:
        """
        try:
            data = self.client.shade.get_neutron_ports(**filters)
            return data.parse(**listing)
        except Exception as e:
            LOG.error("Error [get_ports()]: %s.", e)
            return self.fail(e)

    def create_port(self, network_id, **kwargs):
        """
        Create a new port
        :param network_id:
        :param kwargs:
        :return:
        """
        try:
            data = self.client.shade.create_neutron_port(network_id == network_id, **kwargs)
            return data.parse()
        except Exception as e:
            LOG.error("Error [create_port(%s)]: %s.", network_id, e)
            return self.fail(e)

    def update_port(self, port_id, **kwargs):
        """
        Update a existing port
        :param port_id:
        :param kwargs:
        :return:
        """
        try:
            data = self.client.shade.update_neutron_port(port_id, **kwargs)
            return data.parse()
        except Exception as e:
            LOG.error("Error [create_port(%s)]: %s.", port_id, e)
            return self.fail(e)

    def delete_port(self, port_id):
        """
        Delete a existing port
        :param port_id:
        :return:
        """
        try:
            data = self.client.shade.delete_neutron_port(port_id)
            return data.parse()
        except Exception as e:
            LOG.error("Error [create_port(%s)]: %s.", port_id, e)
            return self.fail(e)

    def add_router_interface(self, router_id, subnet_id=None, port_id=None):
        """
        Add new router interface
        :param router_id:
        :param subnet_id:
        :param port_id:
        :return:
        """
        try:
            data = self.client.shade.add_router_interface(router_id=router_id,
                                                          subnet_id=subnet_id,
                                                          port_id=port_id)
            return data.parse()
        except Exception as e:
            LOG.error("Error [delete_gateway_router(%s)]: %s.", router_id, e)
            return self.fail(e)

    def delete_router_interface(self, router_id, subnet_id=None, port_id=None):
        """
        Detach a subnet from an internal router interface.
        :param router_id:
        :param subnet_id:
        :param port_id:
        :return:
        """
        try:
            data = self.client.shade.remove_router_interface(
                router_id=router_id, subnet_id=subnet_id, port_id=port_id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_router_interface(%s, %s)]: %s.", subnet_id, port_id, e)
            return self.fail(e)

    def create_floating_ip(self, network_name_or_id=None, server=None,
                           fixed_address=None, nat_destination=None,
                           port=None, wait=False, timeout=60):
        """
        Allocate a new floating IP from a network or a pool.

        :param network_name_or_id:
        :param server:
        :param fixed_address:
        :param nat_destination:
        :param port:
        :param wait:
        :param timeout:
        :return:
        """
        try:
            fip = self.client.shade.create_floating_ip(network=network_name_or_id, server=server,
                                                       fixed_address=fixed_address,
                                                       nat_destination=nat_destination,
                                                       port=port, wait=wait, timeout=timeout)
            fip = {'fip_addr': fip['floating_ip_address'], 'fip_id': fip['id']}
            return None, fip
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_floating_ip(%s)]: %s.", network_name_or_id, e)
            return self.fail(e)

    def delete_floating_ip(self, floating_ip_id, retry=1):
        try:
            fip = self.client.shade.delete_floating_ip(floating_ip_id=floating_ip_id,
                                                       retry=retry)
            return self.parse(fip)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_floating_ip(%s)]: %s.", floating_ip_id, e)
            return self.fail(e)
