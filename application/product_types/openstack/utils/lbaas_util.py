#
# Copyright (c) 2020 FTI-CAS
#

from octaviaclient.api import exceptions
from octaviaclient.api.v2 import octavia
from application.utils.data_util import valid_kwargs


class OctaviaClient:
    def __init__(self, session, endpoint):
        self.session = session
        self.api = octavia.OctaviaAPI(session=session, endpoint=endpoint)

    def get_lbs(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        try:
            ret = self.api.load_balancer_list(**kwargs)
            return {
                'data': ret
            }
        except Exception as ex:
            pass

    def get_lb(self, lb_id):
        """

        :param lb_id:
        :return:
        """
        try:
            ret = self.api.load_balancer_show(lb_id=lb_id)
            return {
                'data': ret
            }
        except Exception as e:
            return {
                'error': e
            }

    @valid_kwargs('admin_state_up', 'availability_zone', 'flavor_id', 'listeners',
                  'tags', 'vip_network_id', 'vip_port_id',
                  'vip_qos_policy_id', 'vip_subnet_id')
    def create_lb(self, name, description, vip_ip,provider='octavia', **kwargs):
        """
        Create a new load balancer

        :param name:
        :param description:
        :param vip_ip:
        :param provider:
        :param kwargs:
        :return:
        """
        try:
            ret = self.api.load_balancer_create(name=name, description=description,
                                                vip_address=vip_ip, provider=provider,
                                                **kwargs)
            return {
                'data': ret
            }
        except Exception as e:
            return {
                'error': e
            }

    def delete_lb(self, lb_id):
        """
        Delete a load balancer being created
        :param lb_id:
        :return:
        """
        try:
            ret = self.api.load_balancer_delete(lb_id=lb_id)
            return {
                'data': True if ret == 200 else False
            }
        except Exception as e:
            return {
                'error': e
            }
