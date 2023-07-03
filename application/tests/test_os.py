#
# Copyright (c) 2020 FTI-CAS
#

import json

from foxcloud import client

from keystoneauth1 import exceptions

from application import app, db, api
from application.base import objects
from application import models as md
from application import product_types
from application.product_types.openstack import os_api
from application.product_types.openstack.utils import keystone_util as ks_util
from application.utils import data_util, date_util, str_util, net_util


def p(*a, **kw):
    """

    :rtype: object
    """
    print(*a, **kw)


admin_os_info = {
    'region_name': 'regionOne',
    'auth': {
        'username': 'admin',
        'password': 'YjChRZhTugYg1qSXnoYpajbRg',
        'project_name': 'admin',
        'user_domain_name': 'Default',
        'project_domain_name': 'Default',
        'auth_url': 'https://hn.foxcloud.vn:13000/v3',
    }
}

admin2_os_info = {
    'region_name': 'regionOne',
    'auth': {
        'username': 'khanhct',
        'password': 'khanhct',
        'project_name': 'khanhct',
        'user_domain_name': 'Default',
        'project_domain_name': 'Default',
        'auth_url': 'https://hn.foxcloud.vn:13000/v3',
    }
}

admin3_os_info = {
    'region_name': 'regionOne',
    'auth': {
        'username': 'ldapadmin',
        'password': 'Cas@2020',
        'project_name': 'test-k8s',
        'user_domain_name': 'tripleodomain',
        'project_domain_name': 'tripleodomain',
        'auth_url': 'https://hn.foxcloud.vn:13000/v3',
    }
}

os_info = {
    'region_name': 'regionOne',
    'auth': {
        'username': 'u1',
        'password': '123',
        'user_domain_name': 'tripleodomain',
        'project_name': 'u1',
        'project_domain_name': 'tripleodomain',
        'auth_url': 'https://hn.foxcloud.vn:13000/v3',
    }
}

cluster = 'cas-hn-1'
info = os_info
admin_info = admin3_os_info


def do_test():
    try:
        os_ad_client = os_api.get_admin_os_client(cluster, os_config=admin_info)
        os_client = os_api.get_os_client(cluster, os_config=os_info)
        p('ADMIN ID:', os_ad_client.ks_client.users.api.user_id)
        p('USER ID:', os_client.ks_client.users.api.user_id)
    except Exception as e:
        p(e)

    #p('USER:', os_ad_client.get_user('u1'))
    # {'data': Munch({'id': '8b4d7e2c27f37911fd6dcd78e8d8b55c2e6bd632eed0c35c45b4ed3d84224c81', 'email': None, 'name': 'u1', 'username': None, 'default_project_id': None, 'domain_id': '1479becc2ac64684990ca3aec9eda9e8', 'enabled': None, 'description': None})}
    # {'data': Munch({'id': '10f20b5f8ac180d3d5e982293ea5830834e4ddb3e45688a0021493d580984579', 'email': None, 'name': 'u2', 'username': None, 'default_project_id': None, 'domain_id': '1479becc2ac64684990ca3aec9eda9e8', 'enabled': None, 'description': None})}

    # p(os_ad_client.ks_get_projects(user='8b4d7e2c27f37911fd6dcd78e8d8b55c2e6bd632eed0c35c45b4ed3d84224c81'))
    # p(os_ad_client.ks_get_project('207bf3f396fd407dba021f11b1c7348d'))

    err, roles = os_ad_client.ks_get_roles()
    print(err, roles)
    role_member = None
    for r in roles:
        print(r)
        if r['name'] == 'member':
            role_member = r
    p(role_member)
    # {'id': 'fc96a29c34a0451b9ec2bf574410772e', 'name': 'member', 'domain_id': None, 'description': None, 'options': {'immutable': True}, 'links': {'self': 'https://hn.foxcloud.vn:13000/v3/roles/fc96a29c34a0451b9ec2bf574410772e'}}

    # p(os_ad_client.ks_create_project('u1', domain_id='1479becc2ac64684990ca3aec9eda9e8'))
    # p(os_ad_client.ks_create_project('u1', domain_id='default'))
    #
    # ret = os_ad_client.ks_assign_role(role_id='fc96a29c34a0451b9ec2bf574410772e',
    #                                   user_id='8b4d7e2c27f37911fd6dcd78e8d8b55c2e6bd632eed0c35c45b4ed3d84224c81',
    #                                   project_id='aec1bc214206495084866fd54e6e19f3')
    # p(ret)

    #p(os_ad_client.ks_delete_project('6e7c33d380ba49d18cd74d0d36f0ec25'))

    #
    # USER API
    #

    # p('USER PROJECTS', os_client.get_projects())  -> not allowed
    # p('USER PROJECTS', os_client.get_project(project_id='aec1bc214206495084866fd54e6e19f3')) -> not allowed

    # p('USER NETWORKS', os_client.get_networks()) # -> OK
    # USER NETWORKS {'data': [{'id': '1344dd8b-f594-4242-ba20-c9461ab196b4', 'name': 'k8s-mgmt-net', 'tenant_id': 'f3d345efc6404e278838952f5d88c609', 'admin_state_up': True, 'mtu': 1442, 'status': 'ACTIVE', 'subnets': ['094a1e0f-94af-48b8-84aa-a27956049aa6'], 'shared': True, 'availability_zone_hints': [], 'availability_zones': [], 'ipv4_address_scope': None, 'ipv6_address_scope': None, 'router:external': False, 'description': '', 'qos_policy_id': None, 'port_security_enabled': True, 'dns_domain': '', 'l2_adjacency': True, 'tags': [], 'created_at': '2020-08-22T14:11:34Z', 'updated_at': '2020-08-22T16:49:53Z', 'revision_number': 3, 'project_id': 'f3d345efc6404e278838952f5d88c609'}, {'id': '37a37fa4-5d6d-4462-86e8-26558186bffb', 'name': 'providernet_268', 'tenant_id': 'f3d345efc6404e278838952f5d88c609', 'admin_state_up': True, 'mtu': 1500, 'status': 'ACTIVE', 'subnets': ['096a001d-ebd0-418a-adf0-cf55679fe51b'], 'shared': True, 'availability_zone_hints': [], 'availability_zones': [], 'ipv4_address_scope': None, 'ipv6_address_scope': None, 'router:external': True, 'description': '', 'qos_policy_id': None, 'port_security_enabled': True, 'dns_domain': '', 'l2_adjacency': True, 'is_default': False, 'tags': [], 'created_at': '2020-08-15T15:07:04Z', 'updated_at': '2020-08-17T02:42:06Z', 'revision_number': 4, 'project_id': 'f3d345efc6404e278838952f5d88c609'}, {'id': '761e7cf6-fb7e-4555-8862-9c777c0b3145', 'name': 'providernet_22', 'tenant_id': 'f3d345efc6404e278838952f5d88c609', 'admin_state_up': True, 'mtu': 1500, 'status': 'ACTIVE', 'subnets': ['99096ad1-5a08-4c3e-84ee-f9b1374a5c22'], 'shared': True, 'availability_zone_hints': [], 'availability_zones': [], 'ipv4_address_scope': None, 'ipv6_address_scope': None, 'router:external': True, 'description': '', 'qos_policy_id': None, 'port_security_enabled': True, 'dns_domain': '', 'l2_adjacency': True, 'is_default': False, 'tags': [], 'created_at': '2020-08-15T15:08:05Z', 'updated_at': '2020-08-15T15:08:09Z', 'revision_number': 2, 'project_id': 'f3d345efc6404e278838952f5d88c609'}, {'id': 'f2c379ad-45b2-4cb6-a3ce-4d011b583f17', 'name': 'servicenet_17', 'tenant_id': 'f3d345efc6404e278838952f5d88c609', 'admin_state_up': True, 'mtu': 1500, 'status': 'ACTIVE', 'subnets': ['ce9b6e14-216c-4119-9990-159146300a22'], 'shared': True, 'availability_zone_hints': [], 'availability_zones': [], 'ipv4_address_scope': None, 'ipv6_address_scope': None, 'router:external': False, 'description': '', 'qos_policy_id': None, 'port_security_enabled': True, 'dns_domain': '', 'l2_adjacency': True, 'tags': [], 'created_at': '2020-08-16T16:48:00Z', 'updated_at': '2020-08-16T18:08:17Z', 'revision_number': 5, 'project_id': 'f3d345efc6404e278838952f5d88c609'}]}
