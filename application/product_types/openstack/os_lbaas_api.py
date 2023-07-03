#
# Copyright (c) 2020 FTI-CAS
#
from foxcloud import exceptions as fox_exc
from foxcloud import client as fox_client

from application import app
from application.product_types.openstack import os_base

LOG = app.logger


def get_lbaas_client(cluster, os_config, engine='console', services='lbaas'):
    """
    Create OS client.
    :param cluster:
    :param os_config:
    :param engine:
    :param services:
    :return:
    """
    return LbaasAPI(cluster=cluster, os_config=os_config, engine=engine, services=services)


class LbaasAPI(os_base.OSBaseMixin):
    def get_lbs(self, listing={}, filters={}):
        """
        List all lbs
        :param listing:
        :param filters:
        :return:
        """
        try:
            data = self.client.lbaas.get_lbs(**filters)
            return data.parse(extra_field_getter=self._get_extra_field, **listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_lbs()]: %s.", e)
            return self.fail(e)

    def get_lb(self, lb_id, listing={}):
        """
        Get a specific lb
        :param listing:
        :param lb_id:
        :return:
        """
        try:
            data = self.client.lbaas.get_lb(lb_id=lb_id)
            return data.parse(extra_field_getter=self._get_extra_field, **listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_lb(%s)]: %s.", lb_id, e)
            return self.fail(e)

    def _get_extra_field(self, obj, field):
        if field == 'listeners':
            listeners = []
            for listener in obj['listeners'] or []:
                result = self.client.lbaas.get_listener(listener_id=listener.get('id'))
                err, data = result.parse()
                if err:
                    return self.fail(err)
                listeners.append(data)
            return None, listeners

        if field == 'pools':
            pools = []
            for pool in obj['pools'] or []:
                result = self.client.lbaas.get_pool(pool_id=pool['id'])
                err, data = result.parse()
                if err:
                    return self.fail(err)
                pools.append(data)
            return None, pools

        return self.fail('Unknown extra field "%s".' % field)

    def create_lb(self, name, description, subnet_id=None, wait=False, **kwargs):
        """
        Create a new lb
        :param name:
        :param description:
        :param subnet_id:
        :param wait:
        :param kwargs:
        :return:
        """
        try:
            data = self.client.lbaas.create_lb(name=name, description=description,
                                               subnet_id=subnet_id, wait=wait, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_lb()]: %s.", e)
            return self.fail(e)

    def update_lb(self, id, **kwargs):
        """
        Update an existing lb
        :param id:
        :param kwargs:
        :return:
        """
        try:
            data = self.client.lbaas.update_lb(lb_id=id, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [update_lb(%s)]: %s.", id, e)
            return self.fail(e)

    def delete_lb(self, id):
        """
        Delete an existing lb
        :param id:
        :return:
        """
        try:
            data = self.client.lbaas.delete_lb(lb_id=id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_lb(%s)]: %s.", id, e)
            return self.fail(e)

    def get_listeners(self, listing={}, filters={}):
        """
        List all listeners
        :param listing:
        :param filters:
        :return:
        """
        try:
            data = self.client.lbaas.get_listeners(**filters)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_listeners()]: %s.", e)
            return self.fail(e)

    def get_listener(self, id, listing={}):
        """
        Get a specific listener
        :param listing:
        :param id:
        :return:
        """
        try:
            data = self.client.lbaas.get_listener(listener_id=id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_lb(%s)]: %s.", id, e)
            return self.fail(e)

    def create_listener(self, name, description, protocol, port, lb_id, wait=False, **kwargs):
        """
        Create a new listener
        :param name:
        :param description:
        :param protocol:
        :param port:
        :param lb_id:
        :param wait:
        :param kwargs:
        :return:
        """
        try:
            data = self.client.lbaas.create_listener(name=name, description=description,
                                                     protocol=protocol, port=port,
                                                     lb_id=lb_id, wait=wait, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_listener(%s)]: %s.", name, e)
            return self.fail(e)

    def update_listener(self, id, **kwargs):
        """
        Update an existing listener
        :param id:
        :param kwargs:
        :return:
        """
        try:
            data = self.client.lbaas.update_listener(listener_id=id, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [update_listener(%s)]: %s.", id, e)
            return self.fail(e)

    def delete_listener(self, id):
        """
        Delete an existing listener
        :param id:
        :return:
        """
        try:
            data = self.client.lbaas.delete_listener(listener_id=id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_listener(%s)]: %s.", id, e)
            return self.fail(e)

    def get_pools(self, listing={}, filters={}):
        """
        List all pools
        :param listing:
        :param filters:
        :return:
        """
        try:
            data = self.client.lbaas.get_pools(**filters)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_pools()]: %s.", e)
            return self.fail(e)

    def get_pool(self, pool_id, listing={}):
        """
        Get a specific pool
        :param listing:
        :param pool_id:
        :return:
        """
        try:
            data = self.client.lbaas.get_pool(pool_id=pool_id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_pool(%s)]: %s.", pool_id, e)
            return self.fail(e)

    def create_pool(self, name, description, listener_id, lb_id,
                    lb_algorithm='ROUND_ROBIN', protocol='HTTP', wait=False, **kwargs):
        """
        Create a new pool
        :param name:
        :param description:
        :param listener_id:
        :param lb_id:
        :param lb_algorithm:
        :param protocol:
        :param wait:
        :param kwargs:
        :return:
        """
        try:
            data = self.client.lbaas.create_pool(name=name, description=description,
                                                 listener_id=listener_id, lb_id=lb_id,
                                                 alg=lb_algorithm, protocol=protocol,
                                                 wait=wait, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_pool()]: %s.", e)
            return self.fail(e)

    def update_pool(self, id, **kwargs):
        """
        Update an existing pool
        :param id:
        :param kwargs:
        :return:
        """
        try:
            data = self.client.lbaas.update_pool(pool_id=id, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [update_pool(%s)]: %s.", id, e)
            return self.fail(e)

    def delete_pool(self, id):
        """
        Delete an existing pool
        :param id:
        :return:
        """
        try:
            data = self.client.lbaas.delete_pool(pool_id=id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_pool(%s)]: %s.", id, e)
            return self.fail(e)

    def get_pool_members(self, pool_id, listing={}, filters={}):
        """
        List all pool_members
        :param pool_id:
        :param listing:
        :param filters:
        :return:
        """
        try:
            data = self.client.lbaas.get_members(pool_id=pool_id, **filters)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_pool_members()]: %s.", e)
            return self.fail(e)

    def get_pool_member(self, pool_id, member_id, listing={}):
        """
        Get a specific pool_member
        :param pool_id:
        :param member_id:
        :param listing:
        :return:
        """
        try:
            data = self.client.lbaas.get_member(pool_id=pool_id, member_id=member_id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_pool_member(%s)]: %s.", member_id, e)
            return self.fail(e)

    def create_pool_member(self, name, pool_id, address, port, weight=1, wait=False, **kwargs):
        """

        :param name:
        :param pool_id:
        :param address:
        :param port:
        :param weight:
        :param wait:
        :param kwargs:
        :return:
        """
        try:
            data = self.client.lbaas.add_member(name=name, pool_id=pool_id,
                                                address=address, port=port,
                                                weight=weight, wait=wait,
                                                **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_pool_member()]: %s.", e)
            return self.fail(e)

    def update_pool_member(self, id, pool_id, **kwargs):
        """
        Update an existing pool member
        :param id:
        :param pool_id:
        :param kwargs:
        :return:
        """
        try:
            data = self.client.lbaas.update_member(pool_id=pool_id, member_id=id, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [update_pool_member(%s)]: %s.", id, e)
            return self.fail(e)

    def delete_pool_member(self, id, pool_id):
        """
        Delete an existing pool_member
        :param id:
        :param pool_id:
        :return:
        """
        try:
            data = self.client.lbaas.remove_member(member_id=id, pool_id=pool_id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_pool_member(%s)]: %s.", id, e)
            return self.fail(e)

    def get_monitors(self, listing={}, filters={}):
        """
        List all monitors
        :param listing:
        :param filters:
        :return:
        """
        try:
            data = self.client.lbaas.get_monitors(**filters)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_monitors()]: %s.", e)
            return self.fail(e)

    def get_monitor(self, monitor_id, listing={}):
        """
        Get a specific monitor
        :param listing:
        :param monitor_id:
        :return:
        """
        try:
            data = self.client.lbaas.get_monitor(monitor_id=monitor_id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_monitor(%s)]: %s.", monitor_id, e)
            return self.fail(e)

    def create_monitor(self, name, pool_id, delay, timeout, type='HTTP',
                       http_method='GET', max_retries=10, max_retries_down=10,
                       url_path='/', wait=False, **kwargs):
        try:
            data = self.client.lbaas.create_health_monitor(name=name, pool_id=pool_id,
                                                           delay=delay, timeout=timeout, type=type,
                                                           http_method=http_method, max_retries=max_retries,
                                                           max_retries_down=max_retries_down, url_path=url_path,
                                                           wait=wait, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_monitor()]: %s.", e)
            return self.fail(e)

    def update_monitor(self, id, **kwargs):
        """
        Update an existing monitor
        :param id:
        :param kwargs:
        :return:
        """
        try:
            data = self.client.lbaas.update_health_monitor(health_monitor_id=id, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [update_monitor(%s)]: %s.", id, e)
            return self.fail(e)

    def delete_monitor(self, id):
        """
        Delete an existing monitor
        :param id:
        :return:
        """
        try:
            data = self.client.lbaas.delete_health_monitor(health_monitor_id=id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_monitor(%s)]: %s.", id, e)
            return self.fail(e)

    def get_l7policies(self, listing={}, filters={}):
        """
        List all l7policys
        :param listing:
        :param filters:
        :return:
        """
        try:
            data = self.client.lbaas.get_l7policies(**filters)
            return data.parse(extra_field_getter=self._get_l7rule_field, **listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_l7policies()]: %s.", e)
            return self.fail(e)

    def _get_l7rule_field(self, obj, field):
        if field == 'rules':
            l7rules = []
            for l7rule in obj['rules'] or []:
                result = self.client.lbaas.get_l7rule(l7policy_id=obj['id'], l7rule_id=l7rule.get('id'))
                err, data = result.parse()
                if err:
                    return self.fail(err)
                l7rules.append(data)
            return None, l7rules

    def get_l7policy(self, l7policy_id, listing={}):
        """
        Get a specific l7policy
        :param listing:
        :param l7policy_id:
        :return:
        """
        try:
            data = self.client.lbaas.get_l7policy(l7policy_id=l7policy_id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_l7policy(%s)]: %s.", l7policy_id, e)
            return self.fail(e)

    def create_l7policy(self, name, description, action, listener_id, wait=False, **kwargs):
        """
        Create a new l7policy
        :param name:
        :param description:
        :param listener_id:
        :param lb_id:
        :param lb_algorithm:
        :param protocol:
        :param wait:
        :param kwargs:
        :return:
        """
        try:
            data = self.client.lbaas.create_l7policy(name=name, description=description,
                                                     listener_id=listener_id, action=action,
                                                     wait=wait, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_l7policy()]: %s.", e)
            return self.fail(e)

    def update_l7policy(self, id, **kwargs):
        """
        Update an existing l7policy
        :param id:
        :param kwargs:
        :return:
        """
        try:
            data = self.client.lbaas.update_l7policy(l7policy_id=id, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [update_l7policy(%s)]: %s.", id, e)
            return self.fail(e)

    def delete_l7policy(self, id):
        """
        Delete an existing l7policy
        :param id:
        :return:
        """
        try:
            data = self.client.lbaas.delete_l7policy(l7policy_id=id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_l7policy(%s)]: %s.", id, e)
            return self.fail(e)

    def get_l7rules(self, l7policy_id, listing={}, filters={}):
        """
        List all l7rules
        :param l7policy_id:
        :param listing:
        :param filters:
        :return:
        """
        try:
            data = self.client.lbaas.get_l7rules(l7policy_id=l7policy_id, **filters)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_l7rules()]: %s.", e)
            return self.fail(e)

    def get_l7rule(self, l7rule_id, l7policy_id, listing={}):
        """
        Get a specific l7rule
        :param listing:
        :param l7rule_id:
        :param l7policy_id:
        :return:
        """
        try:
            data = self.client.lbaas.get_l7rule(l7rule_id=l7rule_id, l7policy_id=l7policy_id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_l7rule(%s)]: %s.", l7rule_id, e)
            return self.fail(e)

    def create_l7rule(self, l7policy_id, compare_type, type, value, invert=False, wait=False, **kwargs):
        """
        Create a new l7rule
        :param l7policy_id:
        :param compare_type:
        :param type:
        :param value:
        :param invert:
        :param wait:
        :param kwargs:
        :return:
        """
        try:
            data = self.client.lbaas.create_l7rule(l7policy_id=l7policy_id, compare_type=compare_type,
                                                   type=type, value=value, invert=invert, wait=wait,
                                                   **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_l7rule()]: %s.", e)
            return self.fail(e)

    def update_l7rule(self, l7policy_id, l7rule_id, **kwargs):
        """
        Update L7 rule
        :param l7policy_id:
        :param l7rule_id:
        :param kwargs:
        :return:
        """
        try:
            data = self.client.lbaas.update_l7rule(l7policy_id=l7policy_id, l7rule_id=l7rule_id, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [update_l7rule(%s)]: %s.", id, e)
            return self.fail(e)

    def delete_l7rule(self, l7policy_id, l7rule_id):
        """
        Delete L7 Rule
        :param l7policy_id:
        :param l7rule_id:
        :return:
        """
        try:
            data = self.client.lbaas.delete_l7rule(l7policy_id=l7policy_id, l7rule_id=l7rule_id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_l7rule(%s)]: %s.", id, e)
            return self.fail(e)
