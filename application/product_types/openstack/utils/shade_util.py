#
# Copyright (c) 2020 FTI-CAS
#

import copy
import os

import shade
from shade import exc

from application import app
from application.utils.data_util import valid_kwargs

LOG = app.logger

DEFAULT_HEAT_API_VERSION = '1'


def get_heat_api_version():
    try:
        api_version = os.environ['HEAT_API_VERSION']
    except KeyError:
        return DEFAULT_HEAT_API_VERSION
    else:
        LOG.info("HEAT_API_VERSION is set in env as '%s'", api_version)
        return api_version


def get_shade_client(**os_cloud_config):
    """
    Get Shade OpenStack cloud client
    By default, the input parameters given to "shade.openstack_cloud" method
    are stored in "OS_CLOUD_DEFAULT_CONFIG". The input parameters
    passed in this function, "os_cloud_config", will overwrite the default
    ones.
    :param os_cloud_config:
    :return:
    """
    return shade.openstack_cloud(**os_cloud_config)


def get_shade_operator_client(**os_cloud_config):
    """
    Get Shade Operator cloud client

    :return:
    """
    params = copy.deepcopy(app.config['OS_CLOUD_DEFAULT_CONFIG'])
    params.update(os_cloud_config)
    return shade.operator_cloud(**params)


def get_keypair(shade_client, name_or_id):
    """
    Get an existed keypair.

    :param shade_client
    :param name_or_id: Name of the keypair being created.
    :return:
    """
    try:
        return shade_client.get_keypair(name_or_id=name_or_id)
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [get_keypair(shade_client)]. "
                  "Exception message, '%s'", o_exc.orig_message)


def get_keypairs(shade_client):
    """
    Get all keypairs

    :param shade_client
    :return: A list of ``munch.Munch`` containing keypair info.
    """
    try:
        return shade_client.list_keypairs()
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [get_keypairs(shade_client)]. "
                  "Exception message, '%s'", o_exc.orig_message)


def create_keypair(shade_client, name, public_key=None):
    """
    Create a new keypair.

    :param shade_client:
    :param name: Name of the keypair being created.
    :param public_key: Public key for the new keypair.

    :return:
    """
    try:
        return shade_client.create_keypair(name, public_key=public_key)
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [create_keypair(shade_client)]. "
                  "Exception message, '%s'", o_exc.orig_message)


def delete_keypair(shade_client, name):
    """
    Delete a keypair.

    :param shade_client:
    :param name: Name of the keypair to delete.
    :returns: True if delete succeeded, False otherwise.
    """
    try:
        return shade_client.delete_keypair(name)
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [delete_neutron_router(shade_client, '%s')]. "
                  "Exception message: %s", name, o_exc.orig_message)
        return False


def get_instance(shade_client, instance_name_or_id=None, detailed=False, bare=False,
                 all_projects=False, filters=None):
    """
    Get a server by name or ID.

    :param shade_client:
    :param instance_name_or_id: ID of the server.
    :param filters:
    :param detailed: Whether or not to add detailed additional information.
                    Defaults to False.
    :param bare: Whether to skip adding any additional information to the
                 server record. Defaults to False, meaning the addresses
                 dict will be populated as needed from neutron. Setting
                 to True implies detailed = False.
    :param all_projects: Whether to get server from all projects or just
                         the current auth scoped project.

    :returns: A server ``munch.Munch`` or None if no matching server is
              found.
    """
    try:
        return shade_client.get_server(name_or_id=instance_name_or_id, detailed=detailed, bare=bare,
                                       all_projects=all_projects, filters=filters)
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [get_server(shade_client)]. "
                  "Exception message, '%s'", o_exc.orig_message)


def get_instances(shade_client, detailed=False, all_projects=False, bare=False,
                  filters=None):
    """
    Get a server by name or ID.

    :param shade_client:
    :param filters:
    :param detailed: Whether or not to add detailed additional information.
                    Defaults to False.
    :param bare: Whether to skip adding any additional information to the
                 server record. Defaults to False, meaning the addresses
                 dict will be populated as needed from neutron. Setting
                 to True implies detailed = False.
    :param all_projects: Whether to get server from all projects or just
                         the current auth scoped project.

    :returns: A server ``munch.Munch`` or None if no matching server is
              found.
    """
    try:
        return shade_client.list_servers(detailed=detailed, bare=bare,
                                         all_projects=all_projects, filters=filters)
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [list_servers(shade_client)]. "
                  "Exception message, '%s'", o_exc.orig_message)


def create_instance_and_wait_for_active(shade_client, name, image,
                                        flavor, auto_ip=True, ips=None,
                                        ip_pool=None, root_volume=None,
                                        terminate_volume=False, wait=True,
                                        timeout=180, reuse_ips=True,
                                        network=None, boot_from_volume=False,
                                        volume_size='20', boot_volume=None,
                                        volumes=None, nat_destination=None,
                                        **kwargs):
    """
    Create a virtual server instance.

    :param shade_client:
    :param name:
    :param image:
    :param flavor:
    :param auto_ip:
    :param ips:
    :param ip_pool:
    :param root_volume:
    :param terminate_volume:
    :param wait:
    :param timeout:
    :param reuse_ips:
    :param network:
    :param boot_from_volume:
    :param volume_size:
    :param boot_volume:
    :param volumes:
    :param nat_destination:
    :param kwargs:
    :return:
    """
    try:
        return shade_client.create_server(
            name, image, flavor, auto_ip=auto_ip, ips=ips, ip_pool=ip_pool,
            root_volume=root_volume, terminate_volume=terminate_volume,
            wait=wait, timeout=timeout, reuse_ips=reuse_ips, network=network,
            boot_from_volume=boot_from_volume, volume_size=volume_size,
            boot_volume=boot_volume, volumes=volumes,
            nat_destination=nat_destination, **kwargs)
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [create_instance(shade_client)]. "
                  "Exception message, '%s'", o_exc.orig_message)


def attach_volume_to_instance(shade_client, instance_name_or_id, volume_name_or_id,
                              device=None, wait=True, timeout=None):
    """
    Attach a volume to a server.

    This will attach a volume, described by the passed in volume
    dict, to the server described by the passed in server dict on the named
    device on the server.

    If the volume is already attached to the server, or generally not
    available, then an exception is raised. To re-attach to a server,
    but under a different device, the user must detach it first.

    :param shade_client:
    :param instance_name_or_id:(string) The server name or id to attach to.
    :param volume_name_or_id:(string) The volume name or id to attach.
    :param device:(string) The device name where the volume will attach.
    :param wait:(bool) If true, waits for volume to be attached.
    :param timeout: Seconds to wait for volume attachment. None is forever.

    :returns: True if attached successful, False otherwise.
    """
    try:
        server = shade_client.get_server(name_or_id=instance_name_or_id)
        volume = shade_client.get_volume(volume_name_or_id)
        shade_client.attach_volume(
            server, volume, device=device, wait=wait, timeout=timeout)
        return True
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [attach_volume_to_server(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)
        return False


def delete_instance(shade_client, name_or_id, wait=False, timeout=180,
                    delete_ips=False, delete_ip_retry=1):
    """
    Delete a server instance.

    :param shade_client:
    :param name_or_id: name or ID of the server to delete
    :param wait:(bool) If true, waits for server to be deleted.
    :param timeout:(int) Seconds to wait for server deletion.
    :param delete_ips:(bool) If true, deletes any floating IPs associated with
                      the instance.
    :param delete_ip_retry:(int) Number of times to retry deleting
                           any floating ips, should the first try be
                           unsuccessful.
    :returns: True if delete succeeded, False otherwise.
    """
    try:
        return shade_client.delete_server(
            name_or_id, wait=wait, timeout=timeout, delete_ips=delete_ips,
            delete_ip_retry=delete_ip_retry)
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [delete_instance(shade_client, '%s')]. "
                  "Exception message: %s", name_or_id,
                  o_exc.orig_message)
        return False


def create_flavor(shade_client, name, ram, vcpus, disk, flavor_id="auto",
                  ephemeral=0, swap=0, rxtx_factor=1.0, is_public=True):
    """
    Create a new flavor

    :param shade_client:
    :param name: Descriptive name of the flavor
    :param ram: Memory in MB for the flavor
    :param vcpus: Number of VCPUs for the flavor
    :param disk: Size of local disk in GB
    :param flavorid: ID for the flavor (optional)
    :param ephemeral: Ephemeral space size in GB
    :param swap: Swap space in MB
    :param rxtx_factor: RX/TX factor
    :param is_public: Make flavor accessible to the public

    :returns: A ``munch.Munch`` describing the new flavor.

    :raises: OpenStackCloudException on operation error.
    """
    try:
        return shade_client.create_flavor(name=name, ram=ram, vcpus=vcpus, disk=disk,
                                          flavorid=flavor_id, ephemeral=ephemeral,
                                          swap=swap, rxtx_factor=rxtx_factor, is_public=is_public)
    except exc.OpenStackCloudException as o_exc:
        LOG.exception("Error [create_flavor(nova_client, %s, %s, %s, %s, %s)]"
                      "Exception message: %s", name, ram, disk, vcpus, o_exc.orig_message)
        return None


def get_flavor(shade_client, name_or_id, filters=None, get_extra=True):
    """
    Get a flavor by name or ID.

    :param shade_client:
    :param name_or_id: Name or ID of the flavor.
    :param filters: A dictionary of meta data to use for further filtering.
    :param get_extra: Whether or not the list_flavors call should get the extra
    flavor specs.

    :returns:
    """
    try:
        return shade_client.get_flavor(name_or_id, filters=filters,
                                       get_extra=get_extra)
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [get_flavor(shade_client, '%s')]. "
                  "Exception message: %s", name_or_id, o_exc.orig_message)


def delete_flavor(shade_client, name_or_id):
    """
    Delete a flavor

    :param shade_client:
    :param name_or_id:
    :return:
    """
    try:
        return shade_client.delete_flavor(name_or_id=name_or_id)
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [delete_flavor(shade_client, '%s')]. "
                  "Exception message: %s", name_or_id, o_exc.orig_message)

# *********************************************
#   NEUTRON
# *********************************************


def get_project_quotas(shade_client, project_id):
    """
    Get quota for a project

    :param shade_client:
    :param project_id:
    :returns:
    """
    return shade_client.get_compute_quotas(name_or_id=project_id)


def set_project_quotas(shade_client, project_id, quotas: dict):
    """
    Set a quota in a project.
    Refer: https://docs.openstack.org/api-ref/compute/?expanded=update-quotas-detail

    :param shade_client:
    :param project_id:
    :param quotas:
    :returns:
    """
    try:
        return shade_client.set_compute_quotas(name_or_id=project_id, **quotas)
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [set_compute_quotas(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)
    return None


def delete_project_quotas(shade_client, project_id):
    """
    Delete quota for a project

    :param shade_client:
    :param project_id:
    :returns:
    """
    try:
        return shade_client.delete_compute_quotas(name_or_id=project_id)
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [set_compute_quotas(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)
    return None


def get_network_quotas(shade_client, project_id, details=False):
    """
    Delete quota for a project

    :param shade_client:
    :param project_id:
    :param details:
    :returns:
    """
    try:
        return shade_client.get_network_quotas(name_or_id=project_id, details=details)
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [get_network_quotas(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)
    return None


@valid_kwargs('floatingip', 'network', 'port', 'rbac_policy', 'router',
              'security_group', 'security_group_rule', 'subnet', 'subnetpool')
def set_network_quotas(shade_client, project_id, **kwargs):
    """
    Set a network quota in a project

    :param shade_client:
    :param project_id: project name or id
    :param kwargs: key/value pairs of quota name and quota value
    """
    try:
        return shade_client.set_network_quotas(name_or_id=project_id,**kwargs)
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [set_network_quotas(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)
    return None


def get_neutron_net(shade_client, network_id, filters=None):
    try:
        return shade_client.get_network(name_or_id=network_id, filters=filters)
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [get_neutron_net(shade_client)]."
                  "Exception message, '%s'", o_exc.orig_message)
        return None


def get_neutron_nets(shade_client):
    try:
        return shade_client.list_networks()
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [get_neutron_nets(shade_client)]."
                  "Exception message, '%s'", o_exc.orig_message)
        return None


def create_neutron_net(shade_client, network_name, shared=False, port_security_enabled=True,
                       admin_state_up=True, external=False, provider=None,
                       project_id=None, mtu_size=None):
    """
    Create a neutron network.

    :param network_name:
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
        networks = shade_client.create_network(
            name=network_name, shared=shared, admin_state_up=admin_state_up,
            port_security_enabled=port_security_enabled, mtu_size=mtu_size,
            external=external, provider=provider, project_id=project_id)
        return networks
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [create_neutron_net(shade_client)]."
                  "Exception message, '%s'", o_exc.orig_message)
        return None


def delete_neutron_net(shade_client, network_id):
    try:
        return shade_client.delete_network(network_id)
    except exc.OpenStackCloudException:
        LOG.error("Error [delete_neutron_net(shade_client, '%s')]", network_id)
        return False


def create_neutron_subnet(shade_client, network_name_or_id, cidr=None,
                          ip_version=4, enable_dhcp=False, subnet_name=None,
                          tenant_id=None, allocation_pools=None,
                          gateway_ip=None, disable_gateway_ip=False,
                          dns_nameservers=None, host_routes=None,
                          ipv6_ra_mode=None, ipv6_address_mode=None,
                          use_default_subnetpool=False):
    """
    Create a subnet on a specified network.

    :param shade_client:
    :param network_name_or_id: (string) name or id of the network being created.
    :param cidr:
    :param ip_version: (int) version of ip(4: IPv4, 6:IPv6)
    :param enable_dhcp: (bool) allow to assign an ip to compute automatically
    :param subnet_name: (sting) name of subnet
    :param tenant_id: (string) ID of project
    :param allocation_pools: (dict) ip pools where compute request an ip
    :param gateway_ip: (string) ip of gateway
    :param disable_gateway_ip: (bool)
    :param dns_nameservers:
    :param host_routes:
    :param ipv6_ra_mode:
    :param ipv6_address_mode:
    :param use_default_subnetpool:
    :return:
    """
    try:
        subnet = shade_client.create_subnet(
            network_name_or_id, cidr=cidr, ip_version=ip_version,
            enable_dhcp=enable_dhcp, subnet_name=subnet_name,
            tenant_id=tenant_id, allocation_pools=allocation_pools,
            gateway_ip=gateway_ip, disable_gateway_ip=disable_gateway_ip,
            dns_nameservers=dns_nameservers, host_routes=host_routes,
            ipv6_ra_mode=ipv6_ra_mode, ipv6_address_mode=ipv6_address_mode,
            use_default_subnetpool=use_default_subnetpool)
        return subnet['id']
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [create_neutron_subnet(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)
        return None


def create_neutron_router(shade_client, name=None, admin_state_up=True,
                          ext_gateway_net_id=None, enable_snat=None,
                          ext_fixed_ips=None, project_id=None):
    """Create a logical router.

    :param shade_client:
    :param name:
    :param admin_state_up:
    :param ext_gateway_net_id:
    :param enable_snat:
    :param ext_fixed_ips:
    :param project_id:

    :returns:(string) the router id.
    """
    try:
        router = shade_client.create_router(
            name, admin_state_up, ext_gateway_net_id, enable_snat,
            ext_fixed_ips, project_id)
        return router['id']
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [create_neutron_router(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)


def delete_neutron_router(shade_client, router_id):
    """
    Delete a neutron router

    :param shade_client:
    :param router_id: ID of the Router
    :return:
    """
    try:
        return shade_client.delete_router(router_id)
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [delete_neutron_router(shade_client, '%s')]. "
                  "Exception message: %s", router_id, o_exc.orig_message)
        return False


def remove_gateway_router(neutron_client, router_id):      # pragma: no cover
    try:
        neutron_client.remove_gateway_router(router_id)
        return True
    except Exception:
        LOG.error("Error [remove_gateway_router(neutron_client, '%s')]",
                  router_id)
        return False


def remove_router_interface(shade_client, router, subnet_id=None,
                            port_id=None):
    """
    Detach a subnet from an internal router interface.

    :param shade_client:
    :param router:
    :param subnet_id:
    :param port_id:
    :return:
    """
    try:
        shade_client.remove_router_interface(
            router, subnet_id=subnet_id, port_id=port_id)
        return True
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [remove_interface_router(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)
        return False


def create_floating_ip(shade_client, network_name_or_id=None, server=None,
                       fixed_address=None, nat_destination=None,
                       port=None, wait=False, timeout=60):
    """
    Allocate a new floating IP from a network or a pool.

    :param shade_client:
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
        fip = shade_client.create_floating_ip(
            network=network_name_or_id, server=server,
            fixed_address=fixed_address, nat_destination=nat_destination,
            port=port, wait=wait, timeout=timeout)
        return {'fip_addr': fip['floating_ip_address'], 'fip_id': fip['id']}
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [create_floating_ip(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)


def delete_floating_ip(shade_client, floating_ip_id, retry=1):
    try:
        return shade_client.delete_floating_ip(floating_ip_id=floating_ip_id,
                                               retry=retry)
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [delete_floating_ip(shade_client,'%s')]. "
                  "Exception message: %s", floating_ip_id, o_exc.orig_message)
        return False


def create_security_group_rule(shade_client, secgroup_name_or_id,
                               port_range_min=None, port_range_max=None,
                               protocol=None, remote_ip_prefix=None,
                               remote_group_id=None, direction='ingress',
                               ethertype='IPv4', project_id=None):
    """
    Create a new security group rule

    :param shade_client:
    :param secgroup_name_or_id:
    :param port_range_min:
    :param port_range_max:
    :param protocol:
    :param remote_ip_prefix:
    :param remote_group_id:
    :param direction:
    :param ethertype:
    :param project_id:
    :return:
    """

    try:
        shade_client.create_security_group_rule(
            secgroup_name_or_id, port_range_min=port_range_min,
            port_range_max=port_range_max, protocol=protocol,
            remote_ip_prefix=remote_ip_prefix, remote_group_id=remote_group_id,
            direction=direction, ethertype=ethertype, project_id=project_id)
        return True
    except exc.OpenStackCloudException as op_exc:
        LOG.error("Failed to create_security_group_rule(shade_client). "
                  "Exception message: %s", op_exc.orig_message)
        return False


def create_security_group_full(shade_client, sg_name,
                               sg_description, project_id=None):
    """
    Create a new security group
    :param shade_client:
    :param sg_name:
    :param sg_description:
    :param project_id:
    :return:
    """
    security_group = shade_client.get_security_group(sg_name)

    if security_group:
        LOG.info("Using existing security group '%s'...", sg_name)
        return security_group['id']

    LOG.info("Creating security group  '%s'...", sg_name)
    try:
        security_group = shade_client.create_security_group(
            sg_name, sg_description, project_id=project_id)
    except (exc.OpenStackCloudException,
            exc.OpenStackCloudUnavailableFeature) as op_exc:
        LOG.error("Error [create_security_group(shade_client, %s, %s)]. "
                  "Exception message: %s", sg_name, sg_description,
                  op_exc.orig_message)
        return

    LOG.debug("Security group '%s' with ID=%s created successfully.",
              security_group['name'], security_group['id'])

    LOG.debug("Adding ICMP rules in security group '%s'...", sg_name)
    if not create_security_group_rule(shade_client, security_group['id'],
                                      direction='ingress', protocol='icmp'):
        LOG.error("Failed to create the security group rule...")
        shade_client.delete_security_group(sg_name)
        return

    LOG.debug("Adding SSH rules in security group '%s'...", sg_name)
    if not create_security_group_rule(shade_client, security_group['id'],
                                      direction='ingress', protocol='tcp',
                                      port_range_min='22',
                                      port_range_max='22'):
        LOG.error("Failed to create the security group rule...")
        shade_client.delete_security_group(sg_name)
        return

    if not create_security_group_rule(shade_client, security_group['id'],
                                      direction='egress', protocol='tcp',
                                      port_range_min='22',
                                      port_range_max='22'):
        LOG.error("Failed to create the security group rule...")
        shade_client.delete_security_group(sg_name)
        return
    return security_group['id']


# *********************************************
#   GLANCE
# *********************************************
def create_image(shade_client, name, filename=None, container='images',
                 md5=None, sha256=None, disk_format=None,
                 container_format=None, disable_vendor_agent=True,
                 wait=False, timeout=3600, allow_duplicates=False, meta=None,
                 volume=None, **kwargs):
    """
    Upload an image.

    :param shade_client:
    :param name:
    :param filename:
    :param container:
    :param md5:
    :param sha256:
    :param disk_format:
    :param container_format:
    :param disable_vendor_agent:
    :param wait:
    :param timeout:
    :param allow_duplicates:
    :param meta:
    :param volume:
    :param kwargs:
    :returns: Image id
    """
    try:
        image_id = shade_client.get_image_id(name)
        if image_id is not None:
            LOG.info("Image %s already exists.", name)
            return image_id
        LOG.info("Creating image '%s'", name)
        image = shade_client.create_image(
            name, filename=filename, container=container, md5=md5, sha256=sha256,
            disk_format=disk_format, container_format=container_format,
            disable_vendor_agent=disable_vendor_agent, wait=wait, timeout=timeout,
            allow_duplicates=allow_duplicates, meta=meta, volume=volume, **kwargs)
        image_id = image["id"]
        return image_id
    except exc.OpenStackCloudException as op_exc:
        LOG.error("Failed to create_image(shade_client). "
                  "Exception message: %s", op_exc.orig_message)


def delete_image(shade_client, name_or_id, wait=False, timeout=3600,
                 delete_objects=True):
    try:
        return shade_client.delete_image(name_or_id, wait=wait,
                                         timeout=timeout,
                                         delete_objects=delete_objects)

    except exc.OpenStackCloudException as op_exc:
        LOG.error("Failed to delete_image(shade_client). "
                  "Exception message: %s", op_exc.orig_message)
        return False


def list_images(shade_client=None):
    if shade_client is None:
        shade_client = get_shade_client()

    try:
        return shade_client.list_images()
    except exc.OpenStackCloudException as o_exc:
        LOG.error("Error [list_images(shade_client)]."
                  "Exception message, '%s'", o_exc.orig_message)
        return False


# *********************************************
#   CINDER
# *********************************************
def get_volume_id(shade_client, volume_name):
    return shade_client.get_volume_id(volume_name)


def get_volume(shade_client, name_or_id, filters=None):
    """
    Get a volume by name or ID.

    :param shade_client:
    :param name_or_id: Name or ID of the volume.
    :param filters: A dictionary of meta data to use for further filtering.

    :returns: A volume ``munch.Munch`` or None if no matching volume is found.
    """
    return shade_client.get_volume(name_or_id, filters=filters)


def get_volumes(shade_client, cache=True):
    """
    List all available volumes.

    :param shade_client:
    :param cache:
    :returns: A list of volume ``munch.Munch``.
    """
    return shade_client.list_volumes(cache=cache)


def create_volume(shade_client, size, wait=True, timeout=None,
                  image=None, **kwargs):
    """
    Create a volume.

    :param shade_client:
    :param size: Size, in GB of the volume to create.
    :param wait: If true, waits for volume to be created.
    :param timeout: Seconds to wait for volume creation. None is forever.
    :param image: (optional) Image name, ID or object from which to create
                  the volume.

    :returns: The created volume object.

    """
    try:
        return shade_client.create_volume(size, wait=wait, timeout=timeout,
                                          image=image, **kwargs)
    except (exc.OpenStackCloudException, exc.OpenStackCloudTimeout) as op_exc:
        LOG.error("Failed to create_volume(shade_client). "
                  "Exception message: %s", op_exc.orig_message)


def delete_volume(shade_client, name_or_id=None, wait=True, timeout=None):
    """
    Delete a volume.

    :param shade_client
    :param name_or_id:(string) Name or unique ID of the volume.
    :param wait:(bool) If true, waits for volume to be deleted.
    :param timeout:(string) Seconds to wait for volume deletion. None is forever.

    :return:  True on success, False otherwise.
    """
    try:
        return shade_client.delete_volume(name_or_id=name_or_id,
                                          wait=wait, timeout=timeout)
    except (exc.OpenStackCloudException, exc.OpenStackCloudTimeout) as o_exc:
        LOG.error("Error [delete_volume(shade_client,'%s')]. "
                  "Exception message: %s", name_or_id, o_exc.orig_message)
        return False


def detach_volume(shade_client, server_name_or_id, volume_name_or_id,
                  wait=True, timeout=None):
    """
    Detach a volume from a server.

    :param shade_client
    :param server_name_or_id: The server name or id to detach from.
    :param volume_name_or_id: The volume name or id to detach.
    :param wait: If true, waits for volume to be detached.
    :param timeout: Seconds to wait for volume detachment. None is forever.

    :return: True on success.
    """
    try:
        volume = shade_client.get_volume(volume_name_or_id)
        server = get_instance(shade_client, name_or_id=server_name_or_id)
        shade_client.detach_volume(server, volume, wait=wait, timeout=timeout)
        return True
    except (exc.OpenStackCloudException, exc.OpenStackCloudTimeout) as o_exc:
        LOG.error("Error [detach_volume(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)
        return False


def set_volume_bootable(shade_client, name_or_id, bootable=True):
    """

    :param shade_client:
    :param name_or_id:
    :param bootable:
    :return
    """
    try:
        shade_client.set_volume_bootable(name_or_id=name_or_id, bootable=bootable)
        return True
    except (exc.OpenStackCloudException, exc.OpenStackCloudTimeout) as o_exc:
        LOG.error("Error [set_volume_bootable(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)
        return False


def get_volume_snapshot(shade_client, name_or_id, filters=None):
    """
    Get a volume by name or ID.

    :param shade_client:
    :param name_or_id: Name or ID of the volume snapshot.
    :param filters:
    :returns: A volume ``munch.Munch`` or None if no matching volume is found.
    """
    try:
        return shade_client.get_volume_snapshot()
    except (exc.OpenStackCloudException, exc.OpenStackCloudTimeout) as o_exc:
        LOG.error("Error [get_volume_snapshot(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)
        return None


def get_volume_snapshots(shade_client, detailed=True, search_opts=None):
    """
    List all volume snapshots.

    :param shade_client:
    :param detailed:
    :param search_opts:
    :returns: A list of volume snapshots ``munch.Munch``.

    """
    try:
        return shade_client.get_volume_snapshots(detailed=detailed, search_opts=search_opts)
    except (exc.OpenStackCloudException, exc.OpenStackCloudTimeout) as o_exc:
        LOG.error("Error [get_volume_snapshots(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)
        return None


def create_volume_snapshot(shade_client, volume_id, force=False,
                           wait=True, timeout=None, **kwargs):
    """
    Create a volume.

    :param shade_client
    :param volume_id: the ID of the volume to snapshot.
    :param force: If set to True the snapshot will be created even if the
                  volume is attached to an instance, if False it will not
    :param wait: If true, waits for volume snapshot to be created.
    :param timeout: Seconds to wait for volume snapshot creation. None is
                    forever.

    :returns: The created volume object.
    """
    try:
        return shade_client.create_volume_snapshot(volume_id=volume_id, force=force,
                                                   wait=wait, timeout=timeout, **kwargs)
    except (exc.OpenStackCloudException, exc.OpenStackCloudTimeout) as o_exc:
        LOG.error("Error [create_volume_snapshot(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)
        return None


def delete_volume_snapshot(shade_client, name_or_id=None, wait=False,
                           timeout=None):
    """
    Delete a volume snapshot.

    :param shade_client
    :param name_or_id: Name or unique ID of the volume snapshot.
    :param wait: If true, waits for volume snapshot to be deleted.
    :param timeout: Seconds to wait for volume snapshot deletion. None is
                    forever.
    """
    try:
        shade_client.delete_volume_snapshot(name_or_id=name_or_id, wait=wait,
                                            timeout=timeout)
        return True
    except (exc.OpenStackCloudException, exc.OpenStackCloudTimeout) as o_exc:
        LOG.error("Error [delete_volume_snapshot(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)
        return False


def get_volume_backup(shade_client, name_or_id, filters=None):
    """
    Get a volume by name or ID.

    :param shade_client:
    :param name_or_id: Name or ID of the volume backup.
    :param filters:
    :returns: A volume ``munch.Munch`` or None if no matching volume is found.
    """
    try:
        return shade_client.get_volume_backup(name_or_id=name_or_id, filters=filters)
    except (exc.OpenStackCloudException, exc.OpenStackCloudTimeout) as o_exc:
        LOG.error("Error [get_volume_backup(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)
        return None


def get_volume_backups(shade_client, detailed=True, search_opts=None):
    """
    List all volume snapshots.

    :param shade_client:
    :param detailed:
    :param search_opts:
    :returns: A list of volume snapshots ``munch.Munch``.

    """
    try:
        return shade_client.list_volume_backups(detailed=detailed, search_opts=search_opts)
    except (exc.OpenStackCloudException, exc.OpenStackCloudTimeout) as o_exc:
        LOG.error("Error [get_volume_backups(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)
        return None


def create_volume_backup(shade_client, volume_id, name=None, description=None,
                         force=False, wait=True, timeout=None):
    """
    Create a volume backup.

    :param shade_client:
    :param volume_id: the ID of the volume to backup.
    :param name: name of the backup, one will be generated if one is
                 not provided
    :param description: description of the backup, one will be generated
                        if one is not provided
    :param force: If set to True the backup will be created even if the
                  volume is attached to an instance, if False it will not
    :param wait: If true, waits for volume backup to be created.
    :param timeout: Seconds to wait for volume backup creation. None is
                    forever.

    :returns: The created volume backup object.
    """
    try:
        return shade_client.create_volume_backup(volume_id=volume_id, name=name, description=description,
                                                 force=force, wait=wait, timeout=timeout)
    except (exc.OpenStackCloudException, exc.OpenStackCloudTimeout) as o_exc:
        LOG.error("Error [create_volume_backup(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)
        return None


def delete_volume_backup(shade_client, name_or_id=None, wait=False,
                         timeout=None):
    """
    Delete a volume backup.

    :param shade_client:
    :param name_or_id: Name or unique ID of the volume backup.
    :param wait: If true, waits for volume backup to be deleted.
    :param timeout: Seconds to wait for volume backup deletion. None is
                    forever.
    """
    try:
        return shade_client.delete_volume_backup(name_or_id=name_or_id, wait=wait,
                                                 timeout=timeout)
    except (exc.OpenStackCloudException, exc.OpenStackCloudTimeout) as o_exc:
        LOG.error("Error [delete_volume_backup(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)
        return False


def get_security_group(shade_client, name_or_id, filters=None):
    """
    Get a security group by name or ID.

    :param shade_client
    :param name_or_id: Name or ID of the security group.
    :param filters:
    :returns: A security group ``munch.Munch`` or None if no matching
              security group is found.
    """
    try:
        return shade_client.get_security_group(name_or_id=name_or_id, filters=filters)
    except (exc.OpenStackCloudException, exc.OpenStackCloudTimeout) as o_exc:
        LOG.error("Error [get_security_group(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)
        return None


def get_security_groups(shade_client, filters=None):
    """
    List all available security groups.

    :param shade_client
    :param filters: (optional) dict of filter conditions to push down
    :returns: A list of security group ``munch.Munch``.

    """
    try:
        return shade_client.list_security_groups(filters=filters)
    except (exc.OpenStackCloudException, exc.OpenStackCloudTimeout) as o_exc:
        LOG.error("Error [get_security_group(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)
        return None


def get_server_security_groups(shade_client, server):
    """
    List all available security groups of server.

    :param shade_client
    :param server:
    :returns: A list of security group ``munch.Munch``.
    """
    try:
        return shade_client.list_server_security_groups(server=server)
    except (exc.OpenStackCloudException, exc.OpenStackCloudTimeout) as o_exc:
        LOG.error("Error [get_server_security_groups(shade_client)]. "
                  "Exception message: %s", o_exc.orig_message)
        return None
