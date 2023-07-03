#
# Copyright (c) 2020 FTI-CAS
#

import json

from foxcloud import client

from application import app, db, api
from application import models as md
from application import product_types
from application.product_types.openstack import os_api
from application.product_types.openstack.utils import keystone_util as ks_util
from application.utils import data_util, date_util, str_util, net_util

admin_info = {
    'dn': 'cn=admin,dc=ldap,dc=foxcloud,dc=vn',
    'ldap_endpoint': 'ldap://172.16.1.56',
    'password': 'Cas@2020'
}

u1_info = {
    'dn': 'cn=u1,dc=ldap,dc=foxcloud,dc=vn',
    'ldap_endpoint': 'ldap://172.16.1.56',
    'password': '123'
}

info = admin_info


def do_test():
    ldap_client = client.Client('1', engine='console', services='ldap',  **info).ldap


    # # Create user
    # try:
    #     print(ldap_client.create_user(base='dc=ldap,dc=foxcloud,dc=vn',
    #                                   username='u111', password='123'))
    # except Exception as e:
    #     print(e)


    # # Change pass
    # try:
    #     print(ldap_client.change_password(dn='cn={},ou=Users,dc=ldap,dc=foxcloud,dc=vn'.format('u1'),
    #                                       old_password='123', new_password='1234'))
    # except Exception as e:
    #     print(e)

    ldap_client.unbind()
