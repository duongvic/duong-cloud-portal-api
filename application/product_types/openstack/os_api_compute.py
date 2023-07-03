#
# Copyright (c) 2020 FTI-CAS
#

import time

from foxcloud import exceptions as fox_exc

from application import app
from application.base import errors
from application.product_types.openstack import constant
from application.utils import data_util

LOG = app.logger


class OSComputeMixin(object):

    def get_compute_quotas(self, project_id, listing={}):
        """
        Get quota for a compute

        :param project_id:
        :returns:
        """
        try:
            data = self.client.shade.get_compute_quotas(name_or_id=project_id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_compute_quotas(%s)]: %s.", project_id, e.orig_message)
            return self.fail(e)

    def set_compute_quotas(self, project_id, quotas: dict, listing={}):
        """
        Set a quota in a compute.
        Refer: https://docs.openstack.org/api-ref/compute/?expanded=update-quotas-detail

        :param project_id:
        :param quotas:
        :returns:
        """
        try:
            data = self.client.shade.set_compute_quotas(name_or_id=project_id, **quotas)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [set_compute_quotas(%s)]: %s.", project_id, e.orig_message)
            return self.fail(e)

    def delete_compute_quotas(self, project_id):
        """
        Delete quotas for a compute

        :param project_id:
        :returns:
        """
        try:
            data = self.client.shade.delete_compute_quotas(name_or_id=project_id)
            return self.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [set_compute_quotas(%s)]: %s.", project_id, e.orig_message)
            return self.fail(e)

    # *************************************
    # KEYPAIR
    # *************************************

    # def get_keypair(self, keypair_id, user_id=None, listing={}):
    #     """
    #     Get an existed keypair.
    #     :param keypair_id:
    #     :param user_id:
    #     :return:
    #     """
    #     try:
    #         data = self.client.shade.get_keypair(keypair_id=keypair_id,
    #                                                    user_id=user_id)
    #         return data.parse(**listing)
    #     except fox_exc.FoxCloudException as e:
    #         LOG.error("Error [get_keypair(%s)]: %s.", keypair_id, e.orig_message)
    #         return self.fail(e)
    #
    # def get_keypairs(self, user_id=None, listing={}):
    #     """
    #     Get all keypairs
    #     :@param user_id
    #     :return:
    #     """
    #     try:
    #         data = self.client.shade.get_keypairs(user_id=user_id)
    #         return data.parse(**listing)
    #     except fox_exc.FoxCloudException as e:
    #         LOG.error("Error [get_keypairs()]: %s.", e)
    #         return self.fail(e)
    #
    # def create_keypair(self, info):
    #     """
    #     Create a new keypair
    #     :param info:
    #     :return:
    #     """
    #     try:
    #
    #         data = self.client.shade.create_keypair(name=info['name'], public_key=info['public_key'],
    #                                                       key_type=info['key_type'], user_id=info.get('user_id'))
    #         return data.parse()
    #     except fox_exc.FoxCloudException as e:
    #         LOG.error("Error [create_keypair(%s)]: %s.", info['name'], e.orig_message)
    #         return self.fail(e)
    #
    # def delete_keypair(self, info):
    #     """
    #     Delete a keypair.
    #     :param info:
    #     :returns: True if delete succeeded, False otherwise.
    #     """
    #     try:
    #         data = self.client.shade.delete_keypair(keypair_id=info['keypair_id'],
    #                                                       user_id=info.get('user_id'))
    #         return data.parse()
    #     except fox_exc.FoxCloudException as e:
    #         LOG.error("Error [delete_keypair(%s)]: %s.", info['keypair_id'], e)
    #         return self.fail(e)

    # *******************************
    # NOVA
    # *******************************

    def get_server_group(self, sg_id=None, filters=None, listing={}):
        """
        Get a server group by name or ID.

        :param sg_id: ID of the server group.
        :param filters:
        :returns: A server groups dict or None if no matching server group
                  is found.
        """
        try:
            sg = self.client.shade.server_groups.get(id=sg_id)
            err, sg = self.parse(sg, **listing)
            if err:
                return self.fail(err)
            if filters:
                data_util.filter_list(data=sg, filters=filters)
            return None, sg
        except Exception as e:
            LOG.error("Error [get_server_group(%s)]: %s.", sg_id, e)
            return self.fail(e)

    def create_server_group(self, name, policy, rules=None):
        """
        Create (allocate) a server group.

        :param name: The name of the server group.
        :param policy: Policy name to associate with the server group.
        :param rules: The rules of policy which is a dict, can be applied to
           the policy, now only ``max_server_per_host`` for ``anti-affinity``
           policy would be supported (optional).
        :return A server groups dict or None if not create server group
        """
        try:
            sg = self.client.shade.server_groups.create(name=name, policy=policy,
                                                        rules=rules)
            return self.parse(sg)
        except Exception as e:
            LOG.error("Error [create_server_group(%s)]: %s.", name, e)
            return self.fail(e)

    def delete_server_group(self, sg_id=None):
        """
        Delete a specific server group.

        :param sg_id: The ID of the :class:`ServerGroup` to delete.
        :returns: True if success else False
        """
        try:
            sg = self.client.shade.server_groups.delete(id=sg_id)
            return self.parse(sg)
        except Exception as e:
            LOG.error("Error [delete_server_group(%s)]: %s.", sg_id, e)
            return self.fail(e)

    def get_server(self, server_id):
        """
        Get a specific user
        @param server_id:
        @return:
        """
        try:
            data = self.client.shade.get_server(server_id=server_id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_server(%s)]: %s.", server_id, e.orig_message)
            return self.fail(e)

    def get_servers(self, detailed=True, search_opts=None, marker=None,
                    limit=None, sort_keys=None, sort_dirs=None, listing={}):
        """
        List all servers
        @param detailed:
        @param search_opts:
        @param marker:
        @param limit:
        @param sort_keys:
        @param sort_dirs:
        @param listing:
        @return:
        """
        try:
            data = self.client.shade.get_servers(detailed=detailed, search_opts=search_opts,
                                                 marker=marker, limit=limit, sort_keys=sort_keys,
                                                 sort_dirs=sort_dirs)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_servers()]: %s.", e.orig_message)
            return self.fail(e)

    def create_compute(self, info):
        """
        Create a new compute
        :param info:
        :return:
        """
        try:

            data = self.client.shade.create_server(info=info)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_compute()]: %s.", e)
            return self.fail(e)

    def attach_volume_to_server(self, server_id, volume_id,
                                device=None, wait=True, timeout=None):

        try:
            server = self.client.shade.get_server(server_id=server_id)
            volume = self.client.shade.get_volume(volume_id)
            v = self.client.shade.attach_volume(server, volume, device=device,
                                                wait=wait, timeout=timeout)
            return self.parse(v)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [attach_volume_to_server(%s,%s)]: %s.", server_id, volume_id, e.orig_message)
            return self.fail(e)

    def delete_server(self, server_id, wait=False, timeout=180,
                      delete_ips=False, delete_ip_retry=1):
        """

        @param server_id:
        @param wait:
        @param timeout:
        @param delete_ips:
        @param delete_ip_retry:
        @return:
        """

    def perform_server_action(self, action, server_id, **kwargs):
        try:
            data = self.client.shade.perform_server_action(server_id=server_id,
                                                           action=action, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            return self.fail(e)

    def get_locked_state(self, server_id):
        """
        Get status
        :param server_id
        :return
        """
        err, server = self.get_server(server_id=server_id, detailed=True)
        if err:
            return self.fail(err)
        if server:
            return None, (server.locked, server.locked_reason)
        else:
            return None, None

    def get_power_state(self, server_id):
        """
        Get power status of server
        :param server_id
        :return
        """
        err, server = self.get_server(server_id=server_id, detailed=True)
        if err:
            return self.fail(err)
        state = None
        if server:
            power_state = server.power_state
            for ps in constant.VM_POWER_STATE:
                if ps[0] == power_state:
                    state = ps[1]
        return None, state

    def get_server_status(self, server_id):
        """
        Get status of server
        :param server_id
        :return [ACTIVE, BUILD, REBUILD, RESIZE, VERIFY_RESIZE, MIGRATING, SHUTOFF, ERROR, DELETED]
        """
        err, server = self.get_server(server_id=server_id)
        if err:
            return self.fail(err)
        status = None
        if server:
            status = server.get('status')
        return self.ok(status)

    def get_server_fault(self, server_id):
        """
        Get fault of server
        Only displayed when the server status is ERROR or DELETED and a fault occurred.
        :param server_id
        :return
        """
        err, server = self.get_server(server_id=server_id)
        if err:
            return self.fail(err)
        fault = None
        if server:
            fault = server.get('fault')
        return None, fault

    def get_server_state(self, server_id):
        """
        Get state of server
        :param server_id
        :return []
        """
        err, server = self.get_server(server_id=server_id)
        if err:
            return self.fail(err)
        vm_state = None
        if server:
            vm_state = server.get('vm_state')
        return None, vm_state

    # *******************************
    # SEC GROUP
    # *******************************

    def get_security_group(self, id, **filters):
        """
        Get a security group by name or ID.

        :param id: ID of the security group.
        :param filters:
        :returns: A security group ``munch.Munch`` or None if no matching
                  security group is found.
        """
        try:
            filters = filters or {}
            data = self.client.shade.get_sec_group(sg_id=id, **filters)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_security_group(%s)]: %s.", id, e)
            return self.fail(e)

    def get_security_groups(self, listing={}, **filters):
        """
        List all available security groups.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of security group ``munch.Munch``.
        """
        try:
            data = self.client.shade.get_sec_groups(**filters)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_security_groups()]: %s.", e)
            return self.fail(e)

    def get_server_security_groups(self, server_id, listing={}):
        """
        List all available security groups of server.

        :param server_id:
        :returns: A list of security group ``munch.Munch``.
        """
        try:
            data = self.client.shade.get_server_sec_groups(server_id=server_id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_server_security_groups(%s)]: %s.", server_id, e)
            return self.fail(e)

    def create_security_group(self, name, description):
        """
        Update a security group
        :param name
        :param description
        :return:
        """
        try:
            data = self.client.shade.create_sec_group(name=name, description=description)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            return self.fail(e)

    def update_security_group(self, id, name, description):
        """
        Update a security group
        :param info
        :return:
        """
        try:
            data = self.client.shade.update_sec_group(sg_id=id, name=name,
                                                      description=description)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            return self.fail(e)

    def delete_security_group(self, id):
        """
        Update a security group
        :param info
        :return:
        """
        try:
            data = self.client.shade.delete_sec_group(sg_id=id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            return self.fail(e)

    def get_security_group_rule(self, id, **filters):
        """
        Get a security group by name or ID.

        :param id: ID of the security group.
        :param filters:
        :returns: A security group ``munch.Munch`` or None if no matching
                  security group is found.
        """
        try:
            filters = filters or {}
            data = self.client.shade.get_sg_rule(sg_rule_id=id, **filters)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_security_group(%s)]: %s.", id, e)
            return self.fail(e)

    def get_security_group_rules(self, listing={}, **filters):
        """
        List all available security groups.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of security group ``munch.Munch``.
        """
        try:
            data = self.client.shade.get_sg_rules(**filters)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_security_groups()]: %s.", e)
            return self.fail(e)

    def create_security_group_rule(self, info):
        try:
            data = self.client.shade.create_sec_group_rule(sg_id=info['secgroup_id'],
                                                           port_range_min=info['port_range_min'],
                                                           port_range_max=info['port_range_max'],
                                                           protocol=info['protocol'],
                                                           remote_ip_prefix=info['remote_ip_prefix'],
                                                           remote_group_id=info.get('remote_group_id'),
                                                           direction=info['direction'],
                                                           ethertype=info['ethertype'],
                                                           project_id=info.get('protocol'))
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_security_group_rule(%s)]: %s.", info['id'], e.orig_message)
            return self.fail(e)

    def delete_security_group_rule(self, id):
        """
        Create a new security group
        :param id
        :return:
        """
        try:
            data = self.client.shade.delete_sg_rule(rule_id=id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            return self.fail(e)

    def attach_server_security_groups(self, server_id, secgroup_ids=[]):
        try:
            data = self.client.shade.attach_server_sec_groups(server_id=server_id, sg_ids=secgroup_ids)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            return self.fail(e)

    def remove_server_security_group(self, server_id, secgroup_id):
        try:
            data = self.client.shade.remove_server_sec_group(server_id=server_id, sg_id=secgroup_id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            return self.fail(e)

    def get_keypair(self, keypair_id, user_id=None, listing={}):
        """
        Get a specific keypair
        :param keypair_id:
        :param user_id:
        :param listing:
        :return:
        """
        try:
            data = self.client.shade.get_keypair(keypair_id=keypair_id, user_id=user_id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            return self.fail(e)

    def get_keypairs(self, user_id=None, listing={}):
        """
        List all keypairs
        :param user_id:
        :param listing:
        :return:
        """
        try:
            data = self.client.shade.get_keypairs(user_id=user_id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            return self.fail(e)

    def create_keypair(self, name, public_key, key_type="ssh", user_id=None):
        """
        Create a new keypair
        :param name:
        :param public_key:
        :param key_type:
        :param user_id:
        :return:
        """
        try:
            data = self.client.shade.create_keypair(name=name, public_key=public_key,
                                                    key_type=key_type, user_id=user_id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            return self.fail(e)

    def delete_keypair(self, keypair_id, user_id=None):
        """
        Delete a existing keypair
        :param keypair_id:
        :param user_id:
        :return:
        """
        try:
            data = self.client.shade.delete_keypair(keypair_id=keypair_id, user_id=user_id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            return self.fail(e)
