#
# Copyright (c) 2020 FTI-CAS
#

from application import app, db
from application import models as md
from application.utils import data_util, date_util, str_util

LOG = app.logger

# Pasword_hash generation:
# from werkzeug.security import generate_password_hash
# generate_password_hash('123')

USERS = [
    {
        'user_name': 'admin.foxcloud.vn',
        'email': 'admin@foxcloud.vn',
        'role': 'ADMIN',
        'password_hash': 'pbkdf2:sha256:150000$SU0BRgMm$55b35300a78affffd2413d71ec92149facfeb31b87849606ee24bfea41fa306d',
        # 'FTI-CAS-19%102&z0*#@37'
        'status': 'ENABLED',
        'data': {
            'ldap_info': str_util.jwt_encode_token({
                'dc': 'dc=ldap,dc=foxcloud,dc=vn',
                'ou': 'Users',
                'cn': 'admin.foxcloud.vn',
                'password': 'FTI-CAS-19%102&z0*#@37',
            }),
            'os_info': {
                'domain_name': 'Default',
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
            'compute_ssh_port': 2222,
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
                        'config': {
                            'verify': False,
                            'region_name': 'regionOne',
                            'auth': {
                                'username': 'admin',
                                'password': 'YjChRZhTugYg1qSXnoYpajbRg',
                                'project_name': 'admin',
                                'auth_url': 'https://hn.foxcloud.vn:13000/v3',
                                'project_domain_name': 'Default',
                                'user_domain_name': 'Default',
                            },
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
                            'name': 'providernet_268',
                            'id': 'providernet_268',
                            'subnet': {
                                'name': 'providersubnet_268',
                                'id': 'providersubnet_268'
                            }
                        },
                        'router': {
                            'name': 'ex',
                            'id': '',
                        }
                    },
                },
                {
                    'cluster': 'VN_HCM_1',
                    'enabled': True,
                    'region_id': md.RegionId.VN_HCM,
                    'os_info': {
                        'os_cloud_config': {
                            'verify': False,
                            'region_name': 'regionOne',
                            'auth': {
                                'username': 'admin',
                                'password': 'YjChRZhTugYg1qSXnoYpajbRg',
                                'project_name': 'admin',
                                'auth_url': 'https://hn.foxcloud.vn:13000/v3',
                                'project_domain_name': 'Default',
                                'user_domain_name': 'Default',
                            },
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
                            'name': 'providernet_268',
                            'id': 'providernet_268',
                            'subnet': {
                                'name': 'providersubnet_268',
                                'id': 'providersubnet_268'
                            }
                        },
                        'router': {
                            'name': 'ex',
                            'id': '',
                        }
                    },
                }
            ],
            'target_clusters': None,
            'ignored_clusters': None,
        },
    }
]

REGIONS = [
    {
        'id': md.RegionId.VN_HN,
        'name': 'Hà Nội',
        'status': 'ENABLED',
    },
    {
        'id': md.RegionId.VN_HCM,
        'name': 'Ho Chi Minh',
        'status': 'ENABLED',
    },
    # {
    #     'id': md.RegionId.VN_DN,
    #     'name': 'Đa Nang',
    #     'status': 'ENABLED',
    # }
]

PRODUCTS_HN = [
    {
        'type': md.ProductType.COMPUTE,
        'name': 'custom',
        'status': 'ENABLED',
        'region_id': md.RegionId.VN_HN,
        'info': {
            'name': 'Custom',
            'custom': True,
            'cpu': {
                'values': {'min': 0, 'max': 64, 'step': 1},
            },
            'mem': {
                'values': {'min': 0, 'max': 128, 'step': 1},
            },
            'disk': {
                'values': {'min': 0, 'max': 2048, 'step': 10},
            },
            'disk_iops': {
                'values': [[10000, 5000], [20000, 10000]],
            },
            'net_ip': {
                'values': {'min': 0, 'max': 5, 'step': 1}
            },
            'net_bandwidth': {
                'values': [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
            },
            'snapshot': {
                'values': {'min': 0, 'max': 2048, 'step': 10},
            },
            'backup': {
                'values': {'min': 0, 'max': 2048, 'step': 10},
            }
        },
        'pricing': {
            'price': {
                'cpu': {
                    'unit': 100000,
                },
                'mem': {
                    'unit': 80000,
                },
                'disk': {
                    'unit': 2000,
                },
                'disk_iops': {
                    '10000,5000': 10000, '20000,10000': 20000,
                },
                'net_ip': {
                    'unit': 100000,
                },
                'net_bandwidth': {
                    '100': 0, '200': 50000, '300': 80000, '400': 110000, '500': 130000,
                    '600': 150000, '700': 170000, '800': 190000, '900': 210000, '1000': 230000,
                },
                'snapshot': {
                    'unit': 1500,
                },
                'backup': {
                    'unit': 1500,
                },
            },
            'currency': 'VND',
            'amount': {'min': 1},
            'duration': {'min': 1, 'max': 48},
        },
    },
    # BASIC
    {
        'type': md.ProductType.COMPUTE,
        'name': 'basic-1',
        'status': 'ENABLED',
        'region_id': md.RegionId.VN_HN,
        'info': {
            'name': 'Basic-1',
            'cpu': 1,
            'cpu_desc': '1 vCPU (Intel Xeon)',
            'mem': 2,
            'mem_desc': '2 GB',
            'disk': 20,
            'disk_desc': '20 GB',
            'disk_type': 'SSD',
        },
        'pricing': {
            'price': 339000,
            'price_by_month': {
                '1m': 339000,
            },
            'currency': 'VND',
            'amount': {'min': 1},
            'duration': {'min': 1, 'max': 48},
        },
    },
    {
        'type': md.ProductType.COMPUTE,
        'name': 'basic-2',
        'status': 'ENABLED',
        'region_id': md.RegionId.VN_HN,
        'info': {
            'name': 'Basic-2',
            'cpu': 2,
            'cpu_desc': '2 vCPU (Intel Xeon)',
            'mem': 4,
            'mem_desc': '4 GB',
            'disk': 40,
            'disk_desc': '40 GB',
            'disk_type': 'SSD',
        },
        'pricing': {
            'price': 569000,
            'price_by_month': {
                '1m': 569000,
            },
            'currency': 'VND',
            'amount': {'min': 1},
            'duration': {'min': 1, 'max': 48},
        },
    },
    {
        'type': md.ProductType.COMPUTE,
        'name': 'basic-3',
        'status': 'ENABLED',
        'region_id': md.RegionId.VN_HN,
        'info': {
            'name': 'Basic-3',
            'cpu': 4,
            'cpu_desc': '4 vCPU (Intel Xeon)',
            'mem': 4,
            'mem_desc': '4 GB',
            'disk': 60,
            'disk_desc': '60 GB',
            'disk_type': 'SSD',
        },
        'pricing': {
            'price': 789000,
            'price_by_month': {
                '1m': 789000,
            },
            'currency': 'VND',
            'amount': {'min': 1},
            'duration': {'min': 1, 'max': 48},
        },
    },
    {
        'type': md.ProductType.COMPUTE,
        'name': 'basic-4',
        'status': 'ENABLED',
        'region_id': md.RegionId.VN_HN,
        'info': {
            'name': 'Basic-4',
            'cpu': 4,
            'cpu_desc': '4 vCPU (Intel Xeon)',
            'mem': 6,
            'mem_desc': '6 GB',
            'disk': 100,
            'disk_desc': '100 GB',
            'disk_type': 'SSD',
        },
        'pricing': {
            'price': 969000,
            'price_by_month': {
                '1m': 969000,
            },
            'currency': 'VND',
            'amount': {'min': 1},
            'duration': {'min': 1, 'max': 48},
        },
    },
    # PRO
    {
        'type': md.ProductType.COMPUTE,
        'name': 'pro-1',
        'status': 'ENABLED',
        'region_id': md.RegionId.VN_HN,
        'info': {
            'name': 'Pro-1',
            'cpu': 6,
            'cpu_desc': '6 vCPU (Intel Xeon)',
            'mem': 8,
            'mem_desc': '8 GB',
            'disk': 150,
            'disk_desc': '150 GB',
            'disk_type': 'SSD',
            'snapshot_supported': True,
            'snapshot_size_max': 40,
            'backup_supported': True,
            'backup_size_max': 80
        },
        'pricing': {
            'price': 1079000,
            'price_by_month': {
                '1m': 1079000,
            },
            'currency': 'VND',
            'amount': {'min': 1},
            'duration': {'min': 1, 'max': 48},
        },
    },
    {
        'type': md.ProductType.COMPUTE,
        'name': 'pro-2',
        'status': 'ENABLED',
        'region_id': md.RegionId.VN_HN,
        'info': {
            'name': 'Pro-2',
            'cpu': 8,
            'cpu_desc': '8 vCPU (Intel Xeon)',
            'mem': 12,
            'mem_desc': '12 GB',
            'disk': 200,
            'disk_desc': '200 GB',
            'disk_type': 'SSD',
            'snapshot_supported': True,
            'snapshot_size_max': 50,
            'backup_supported': True,
            'backup_size_max': 100
        },
        'pricing': {
            'price': 1749000,
            'price_by_month': {
                '1m': 1749000,
            },
            'currency': 'VND',
            'amount': {'min': 1},
            'duration': {'min': 1, 'max': 48},
        },
    },
    {
        'type': md.ProductType.COMPUTE,
        'name': 'pro-3',
        'status': 'ENABLED',
        'region_id': md.RegionId.VN_HN,
        'info': {
            'name': 'Pro-3',
            'cpu': 12,
            'cpu_desc': '12 vCPU (Intel Xeon)',
            'mem': 16,
            'mem_desc': '16 GB',
            'disk': 300,
            'disk_desc': '300 GB',
            'disk_type': 'SSD',
            'snapshot_supported': True,
            'snapshot_size_max': 60,
            'backup_supported': True,
            'backup_size_max': 120
        },
        'pricing': {
            'price': 2429000,
            'price_by_month': {
                '1m': 2429000,
            },
            'currency': 'VND',
            'amount': {'min': 1},
            'duration': {'min': 1, 'max': 48},
        },
    },
    # OS - WINDOWS
    {
        'type': md.ProductType.OS,
        'name': 'windows-server-2012',
        'status': 'ENABLED',
        'region_id': md.RegionId.VN_HN,
        'info': {
            'type': 'windows',
            'name': 'Windows Server 2012',
            'arch': 'x86_64',
        },
        'pricing': {
            'price': 0,
            'currency': 'VND',
        },
    },
    {
        'type': md.ProductType.OS,
        'name': 'windows-server-2016',
        'status': 'ENABLED',
        'region_id': md.RegionId.VN_HN,
        'info': {
            'type': 'windows',
            'name': 'Windows Server 2016',
            'arch': 'x86_64',
        },
        'pricing': {
            'price': 0,
            'currency': 'VND',
        },
    },
    {
        'type': md.ProductType.OS,
        'name': 'windows-server-2019',
        'status': 'ENABLED',
        'region_id': md.RegionId.VN_HN,
        'info': {
            'type': 'windows',
            'name': 'Windows Server 2019',
            'arch': 'x86_64',
        },
        'pricing': {
            'price': 0,
            'currency': 'VND',
        },
    },
    {
        'type': md.ProductType.OS,
        'name': 'windows-10-enterprise',
        'status': 'ENABLED',
        'region_id': md.RegionId.VN_HN,
        'info': {
            'type': 'windows',
            'name': 'Windows 10 Enterprise',
            'arch': 'x86_64',
        },
        'pricing': {
            'price': 0,
            'currency': 'VND',
        },
    },
    # OS - LINUX
    {
        'type': md.ProductType.OS,
        'name': 'ubuntu-server-16.04',
        'status': 'ENABLED',
        'region_id': md.RegionId.VN_HN,
        'info': {
            'type': 'linux',
            'distro': 'ubuntu',
            'name': 'Ubuntu Server 16.04',
            'arch': 'x86_64'
        },
        'pricing': {
            'price': 0,
            'currency': 'VND',
        },
    },
    {
        'type': md.ProductType.OS,
        'name': 'ubuntu-server-18.04',
        'status': 'ENABLED',
        'region_id': md.RegionId.VN_HN,
        'info': {
            'type': 'linux',
            'distro': 'ubuntu',
            'name': 'Ubuntu Server 18.04',
            'arch': 'x86_64'
        },
        'pricing': {
            'price': 0,
            'currency': 'VND',
        },
    },
    {
        'type': md.ProductType.OS,
        'name': 'ubuntu-server-20.04',
        'status': 'ENABLED',
        'region_id': md.RegionId.VN_HN,
        'info': {
            'type': 'linux',
            'distro': 'ubuntu',
            'name': 'Ubuntu Server 20.04',
            'arch': 'x86_64'
        },
        'pricing': {
            'price': 0,
            'currency': 'VND',
        },
    },
    {
        'type': md.ProductType.OS,
        'name': 'centos-7',
        'status': 'ENABLED',
        'region_id': md.RegionId.VN_HN,
        'info': {
            'type': 'linux',
            'distro': 'centos',
            'name': 'Cent OS 7',
            'arch': 'x86_64'
        },
        'pricing': {
            'price': 0,
            'currency': 'VND',
        },
    },
    {
        'type': md.ProductType.OS,
        'name': 'centos-8',
        'status': 'ENABLED',
        'region_id': md.RegionId.VN_HN,
        'info': {
            'type': 'linux',
            'distro': 'centos',
            'name': 'Cent OS 8',
            'arch': 'x86_64'
        },
        'pricing': {
            'price': 0,
            'currency': 'VND',
        },
    },
    {
        'type': md.ProductType.OS,
        'name': 'debian-9',
        'status': 'ENABLED',
        'region_id': md.RegionId.VN_HN,
        'info': {
            'type': 'linux',
            'distro': 'debian',
            'name': 'Debian 9',
            'arch': 'x86_64'
        },
        'pricing': {
            'price': 0,
            'currency': 'VND',
        },
    },
    {
        'type': md.ProductType.OS,
        'name': 'debian-10',
        'status': 'ENABLED',
        'region_id': md.RegionId.VN_HN,
        'info': {
            'type': 'linux',
            'distro': 'debian',
            'name': 'Debian 10',
            'arch': 'x86_64'
        },
        'pricing': {
            'price': 0,
            'currency': 'VND',
        },
    }
]

PRODUCTS_HCM = [
    data_util.merge_dicts(d, {'region_id': md.RegionId.VN_HCM}, create_new=True) for d in PRODUCTS_HN
]

PRODUCTS_DN = [

]

PRODUCTS = PRODUCTS_HN + PRODUCTS_HCM + PRODUCTS_DN

PROMOTIONS_HN = [
    {
        'type': 'TRIAL',
        'name': 'Compute Trial',
        'status': 'ENABLED',
        'region_id': md.RegionId.VN_HN,
        'target_product_types': ['COMPUTE', 'OS'],
        'product_settings': {
            'compute': {
                'warning_only': True,
                'max_cpu': 2,
                'max_mem': 4,
                'max_disk': 40,
                'snapshot_supported': True,
                'max_snapshot_size': 20,
                'backup_supported': True,
                'max_backup_size': 40
            }
        },
        'user_settings': {'max_uses_per_user': 2},
        'settings': {
            'amount': 1,
            'duration': '10 days',
        },
        'discount_code': None,
    },
    {
        'type': 'DISCOUNT',
        'name': 'Compute Discount 20%',
        'status': 'DISABLED',
        'region_id': md.RegionId.VN_HN,
        'target_product_types': ['COMPUTE'],
        'product_settings': {
            'compute': {
                'warning_only': True,
                'max_cpu': 2,
                'max_mem': 4,
                'max_disk': 40,
                'snapshot_supported': True,
                'max_snapshot_size': 20,
                'backup_supported': True,
                'max_backup_size': 40
            }
        },
        'user_settings': {'max_uses_per_user': 1},
        'settings': {
            'amount': {'min': 1},
            'duration': {'min': 3},
            'currency': ['VND'],
            'discount_rate': 0.2,
        },
        'discount_code': 'PROMO20',
    }
]

PROMOTIONS_HCM = [
    data_util.merge_dicts(d, {'region_id': md.RegionId.VN_HCM}, create_new=True) for d in PROMOTIONS_HN
]

PROMOTIONS_DN = [
    # TODO
]

PROMOTIONS = PROMOTIONS_HN + PROMOTIONS_HCM + PROMOTIONS_DN


def create_user(data):
    """
    Create an user object.
    """
    user = md.User()
    data_util.assign_model_object(user, data)
    if user.create_date is None:
        user.create_date = date_util.utc_now()
    return user


def create_config(data):
    """
    Create a config object.
    """
    config = md.Configuration()
    data_util.assign_model_object(config, data)
    if config.create_date is None:
        config.create_date = date_util.utc_now()
    return config


def create_region(data):
    """
    Create a region object.
    """
    region = md.Region()
    data_util.assign_model_object(region, data)
    if region.create_date is None:
        region.create_date = date_util.utc_now()
    return region


def create_product(data):
    """
    Create a product object.
    """
    product = md.Product()
    data_util.assign_model_object(product, data)
    if product.create_date is None:
        product.create_date = date_util.utc_now()
    return product


def create_promotion(data):
    """
    Create a promotion object.
    """
    promotion = md.Promotion()
    data_util.assign_model_object(promotion, data)
    if promotion.create_date is None:
        promotion.create_date = date_util.utc_now()
    return promotion


def create_order(data):
    """
    Create an order object.
    """
    data = dict(data)
    order = md.Order()

    user_id = data['user_id']
    if isinstance(user_id, str):
        data['user_id'] = md.User.query.filter_by(user_name=user_id).first().id

    data_util.assign_model_object(order, data)
    if order.create_date is None:
        order.create_date = date_util.utc_now()

    # Create order products
    # TODO

    return order


def create_order_product(data):
    """
    Create an order product object.
    """
    order_product = md.OrderProduct()
    data_util.assign_model_object(order_product, data)
    if order_product.create_date is None:
        order_product.create_date = date_util.utc_now()
    return order_product


def create(**kw):
    """
    Create all objects.
    """
    all_objects = []

    # Base objects
    for data in (kw.get('users') or []):
        if data:
            user = create_user(data)
            all_objects.append(user)

    for data in (kw.get('config') or []):
        if data:
            config = create_config(data)
            all_objects.append(config)

    for data in (kw.get('regions') or []):
        if data:
            region = create_region(data)
            all_objects.append(region)

    for data in (kw.get('products') or []):
        if data:
            product = create_product(data)
            all_objects.append(product)

    for data in (kw.get('promotions') or []):
        if data:
            promo = create_promotion(data)
            all_objects.append(promo)

    if len(all_objects) > 0:
        error = md.save_new(all_objects)
        if error:
            raise Exception(error.get_message(localized=False))

    # Orders must be created after users, products, ...
    all_objects = []
    for data in (kw.get('orders') or []):
        if data:
            order = create_order(data)
            all_objects.append(order)

    if len(all_objects) > 0:
        error = md.save_new(all_objects)
        if error:
            raise Exception(error.get_message(localized=False))


def create_all():
    create(users=USERS, config=CONFIG, regions=REGIONS,
           products=PRODUCTS, promotions=PROMOTIONS)
