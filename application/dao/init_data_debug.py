#
# Copyright (c) 2020 FTI-CAS
#

from application import app, db
from application.dao import init_data
from application import models as md
from application.utils import data_util, str_util

LOG = app.logger

DEBUG = app.config['ENV'] in ('dev', 'development', 'debug')

# Pasword_hash generation:
# from werkzeug.security import generate_password_hash
# generate_password_hash('123')

USERS = init_data.USERS + [
    {
        'user_name': 'u1',
        'email': 'u1@xxxyyyzzz.null',
        'role': 'USER',
        'password_hash': 'pbkdf2:sha256:150000$US6gLMIB$ee69ade16053adbaf442d7f86a9a4e7e2d8fba1adbde2012a1ff6a81f8390e54',
        'status': 'ENABLED',
        'data': {
            'ldap_info': str_util.jwt_encode_token({
                'dc': 'dc=ldap,dc=foxcloud,dc=vn',
                'ou': 'Users',
                'cn': 'u1',
                'password': '123',
            }),
            'os_info': {
                'domain_name': 'tripleodomain',
            }
        }
    },
    {
        'user_name': 'u2',
        'email': 'u2@xxxyyyzzz.null',
        'role': 'USER',
        'password_hash': 'pbkdf2:sha256:150000$US6gLMIB$ee69ade16053adbaf442d7f86a9a4e7e2d8fba1adbde2012a1ff6a81f8390e54',
        'status': 'ENABLED',
        'data': {
            'ldap_info': str_util.jwt_encode_token({
                'dc': 'dc=ldap,dc=foxcloud,dc=vn',
                'ou': 'Users',
                'cn': 'u2',
                'password': '123',
            }),
            'os_info': {
                'domain_name': 'tripleodomain',
            }
        }
    },
    {
        'user_name': 'ad1',
        'email': 'ad1@xxxyyyzzz.null',
        'role': 'ADMIN',
        'password_hash': 'pbkdf2:sha256:150000$US6gLMIB$ee69ade16053adbaf442d7f86a9a4e7e2d8fba1adbde2012a1ff6a81f8390e54',
        'status': 'ENABLED',
        'data': {
            'ldap_info': str_util.jwt_encode_token({
                'dc': 'dc=ldap,dc=foxcloud,dc=vn',
                'ou': 'Users',
                'cn': 'ad1',
                'password': '123',
            }),
            'os_info': {
                'domain_name': 'tripleodomain',
            }
        }
    },
    {
        'user_name': 'ad2',
        'email': 'ad2@xxxyyyzzz.null',
        'role': 'ADMIN',
        'password_hash': 'pbkdf2:sha256:150000$US6gLMIB$ee69ade16053adbaf442d7f86a9a4e7e2d8fba1adbde2012a1ff6a81f8390e54',
        'status': 'ENABLED',
        'data': {
            'ldap_info': str_util.jwt_encode_token({
                'dc': 'dc=ldap,dc=foxcloud,dc=vn',
                'ou': 'Users',
                'cn': 'ad2',
                'password': '123',
            }),
            'os_info': {
                'domain_name': 'tripleodomain',
            }
        }
    },
    {
        'user_name': 'sale',
        'email': 'sale@xxxyyyzzz.null',
        'role': 'SALE',
        'password_hash': 'pbkdf2:sha256:150000$US6gLMIB$ee69ade16053adbaf442d7f86a9a4e7e2d8fba1adbde2012a1ff6a81f8390e54',
        'status': 'ENABLED',
        'data': {
            'ldap_info': str_util.jwt_encode_token({
                'dc': 'dc=ldap,dc=foxcloud,dc=vn',
                'ou': 'Users',
                'cn': 'sale',
                'password': '123',
            }),
            'os_info': {
                'domain_name': 'tripleodomain',
            }
        }
    },
    {
        'user_name': 'ad_sale',
        'email': 'admin_sale@xxxyyyzzz.null',
        'role': 'ADMIN_SALE',
        'password_hash': 'pbkdf2:sha256:150000$US6gLMIB$ee69ade16053adbaf442d7f86a9a4e7e2d8fba1adbde2012a1ff6a81f8390e54',
        'status': 'ENABLED',
        'data': {
            'ldap_info': str_util.jwt_encode_token({
                'dc': 'dc=ldap,dc=foxcloud,dc=vn',
                'ou': 'Users',
                'cn': 'ad_sale',
                'password': '123',
            }),
            'os_info': {
                'domain_name': 'tripleodomain',
            }
        }
    },
    {
        'user_name': 'it',
        'email': 'it@xxxyyyzzz.null',
        'role': 'ADMIN_IT',
        'password_hash': 'pbkdf2:sha256:150000$US6gLMIB$ee69ade16053adbaf442d7f86a9a4e7e2d8fba1adbde2012a1ff6a81f8390e54',
        'status': 'ENABLED',
        'data': {
            'ldap_info': str_util.jwt_encode_token({
                'dc': 'dc=ldap,dc=foxcloud,dc=vn',
                'ou': 'Users',
                'cn': 'it',
                'password': '123',
            }),
            'os_info': {
                'domain_name': 'tripleodomain',
            }
        }
    },
]

CONFIG = [
    # APP
    {
        'type': md.ConfigurationType.APP,
        'name': 'app_config',
        'version': 10000,
        'status': 'ENABLED',
        'contents': {
            'history_log_expiration_days': 180,
            'report_expiration_days': 180,
            'support_expiration_days': 180,
        },
    },
    # APP - orders
    {
        'type': md.ConfigurationType.APP,
        'name': 'order_config',
        'version': 10000,
        'status': 'ENABLED',
        'contents': {
            'auto_complete_zero_price_orders': False,
            'notify_sale_when_orders_created': True,
            'sales_info': {
                'all': [],
                'VN_HN': [
                    {
                        'email': 'tiendc@gmail.com',
                    },
                ],
                'VN_HCM': [
                    {
                        'email': 'tiendc@gmail.com',
                    },
                ],
                'VN_DN': [],
            }
        },
    },
    # APP - products
    {
        'type': md.ConfigurationType.APP,
        'name': 'product_config',
        'version': 10000,
        'status': 'ENABLED',
        'contents': {

        },
    },
    # COMPUTE
    {
        'type': md.ConfigurationType.COMPUTE,
        'name': 'compute_config',
        'version': 10000,
        'status': 'ENABLED',
        'contents': {
            'expired_compute_action': 'suspend',
            'delete_expired_compute_after_days': 7,
            'compute_ssh_port': 22,
        },
    },
    # BACKEND - LDAP
    {
        'type': md.ConfigurationType.BACKEND,
        'name': 'ldap_config',
        'version': 10000,
        'status': 'ENABLED',
        'contents': {
            'enabled': True,
            'dc': 'dc=ldap,dc=foxcloud,dc=vn',
            'cn': 'admin',
            'password': 'Cas@2020',
            'url': 'ldap://172.16.1.56',
        }
    },
    # BACKEND - OS
    {
        'type': md.ConfigurationType.BACKEND,
        'name': 'os_config',
        'version': 10000,
        'status': 'ENABLED',
        'contents': {
            'clusters': [
                {
                    'cluster': 'VN_HN_1',
                    'enabled': True,
                    'region_id': md.RegionId.VN_HN,
                    'os_info': {
                        'verify': False,
                        'region_name': 'regionOne',
                        'auth': {
                            'username': 'ldapadmin',
                            'password': 'Cas@2020',
                            'project_name': 'test-k8s',
                            'auth_url': 'https://hn.foxcloud.vn:13000/v3',
                            'project_domain_name': 'tripleodomain',
                            'user_domain_name': 'tripleodomain',
                        },
                        'project': {
                            'quotas': {
                                'cores': 128,
                                'force': True,
                                'instances': 100,
                                'key_pairs': 100,
                                'ram': 10000,
                                'server_groups': 10,
                                'server_group_members': 10,
                                'networks': 100,
                                'security_group_rules': 100,
                                'security_groups': 100,
                            }
                        },
                        'public_network': {
                            'name': 'providernet_22',
                            'id': 'providernet_22',
                            'subnet': {
                                'name': 'providersubnet_22',
                                'id': 'providersubnet_22'
                            }
                        },
                        'router': {
                            'name': 'ex',
                            'id': '',
                        },
                        'image_mapping': {
                            'centos-7': 'Ubuntu16.04',
                            'centos-8': 'Ubuntu16.04',
                            'ubuntu-server-16.04': 'Ubuntu16.04',
                            'ubuntu-server-18.04': 'Ubuntu16.04',
                            'ubuntu-server-20.04': 'Ubuntu16.04',
                            'debian-9': 'Ubuntu16.04',
                            'debian-10': 'Ubuntu16.04',
                            'windows-server-2012': 'Ubuntu16.04',
                            'windows-server-2016': 'Ubuntu16.04',
                            'windows-server-2019': 'Ubuntu16.04',
                            'windows-10-enterprise': 'Ubuntu16.04',
                        },
                    },
                },
                {
                    'cluster': 'VN_HCM_1',
                    'enabled': True,
                    'region_id': md.RegionId.VN_HCM,
                    'os_info': {
                        'verify': False,
                        'region_name': 'regionOne',
                        'auth': {
                            'username': 'ldapadmin',
                            'password': 'Cas@2020',
                            'project_name': 'test-k8s',
                            'auth_url': 'https://hn.foxcloud.vn:13000/v3',
                            'project_domain_name': 'tripleodomain',
                            'user_domain_name': 'tripleodomain',
                        },
                        'project': {
                            'quotas': {
                                'cores': 128,
                                'force': True,
                                'instances': 100,
                                'key_pairs': 100,
                                'ram': 10000,
                                'server_groups': 10,
                                'server_group_members': 10,
                                'networks': 100,
                                'security_group_rules': 100,
                                'security_groups': 100,
                            }
                        },
                        'public_network': {
                            'name': 'providernet_22',
                            'id': 'providernet_22',
                            'subnet': {
                                'name': 'providersubnet_22',
                                'id': 'providersubnet_22'
                            }
                        },
                        'router': {
                            'name': 'ex',
                            'id': '',
                        },
                        'image_mapping': {
                            'centos-7': 'Ubuntu16.04',
                            'centos-8': 'Ubuntu16.04',
                            'ubuntu-server-16.04': 'Ubuntu16.04',
                            'ubuntu-server-18.04': 'Ubuntu16.04',
                            'ubuntu-server-20.04': 'Ubuntu16.04',
                            'debian-9': 'Ubuntu16.04',
                            'debian-10': 'Ubuntu16.04',
                            'windows-server-2012': 'Ubuntu16.04',
                            'windows-server-2016': 'Ubuntu16.04',
                            'windows-server-2019': 'Ubuntu16.04',
                            'windows-10-enterprise': 'Ubuntu16.04',
                        },
                    },
                }
            ],
            'target_clusters': None,
            'ignored_clusters': None,
        },
    }
]

REGIONS = init_data.REGIONS

PRODUCTS = init_data.PRODUCTS

PROMOTIONS = init_data.PROMOTIONS

ORDERS_HN = [
    {
        'code': 'DH000010',
        'type': md.OrderType.TRIAL,
        'product_type': md.ProductType.COMPUTE,
        'status': md.OrderStatus.COMPLETED,
        'user_id': 'u1',
        'duration': '1 month',
        'amount': 100,
        'region_id': md.RegionId.VN_HN,
        'currency': 'VND',
        'payment_type': None,
        'price': 100000,
        'price_paid': 0,
        'data': {
            "info": {
                "cpu": 2,
                "mem": 4,
                "disk": 40,
                "os_name": "ubuntu-server-16.04",
                "os_type": "linux",
                "os_distro": "ubuntu",
                "snapshot_size_max": 40,
                "snapshot_supported": True,
                "backup_size_max": 40,
                "backup_supported": True,
            }
        },
        'products': [
            # TODO
        ],
    }
]

ORDERS_HCM = [
    data_util.merge_dicts(d, {'region_id': md.RegionId.VN_HCM}, create_new=True) for d in ORDERS_HN
]

ORDERS_DN = [
    # TODO
]

ORDERS = ORDERS_HN + ORDERS_HCM + ORDERS_DN


def create_all():
    init_data.create(users=USERS, config=CONFIG, regions=REGIONS,
                     products=PRODUCTS, promotions=PROMOTIONS,
                     orders=ORDERS)
