
import codecs
import json
import pprint
import requests
import sys

import api_base as base


# user, configuration, order, compute, promotion, product
USER_ARGS = ['compute', 'update']
USER_DATA = {
    'data': {
        "id": 17,
            "backend_id": "prox-hn-1/pve02/108",
            "status": "ENABLED",
            "data": {
                "info": {
                    "cpu": 2,
                    "mem": 4,
                    "disk": 40,
                    "disks": [
                        {
                            "name": "scsi0",
                            "size": 40,
                            "type": None,
                            "enabled": True,
                            "read_iops": None,
                            "write_iops": None
                        }
                    ],
                    "onboot": False,
                    "reboot": True,
                    "os_arch": "x86_64",
                    "os_name": "windows-10-enterprise",
                    "os_type": "windows",
                    "ssh_key": None,
                    "networks": [
                        {
                            "type": "public",
                            "iface": "net0",
                            "bridge": None,
                            "enabled": True,
                            "gateway": None,
                            "netmask": None,
                            "vlan_tag": None,
                            "bandwidth": 100,
                            "ip_address": None,
                            "mac_address": None
                        }
                    ],
                    "password": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRhIjoiQ2FzQDIwMjAiLCJ0aW1lIjoxNTk4NjEzMzI3LjUyNDczNzR9.HjRMmZqhpe_6RwER7zDgOfdFVV5BQ7K60hIc-cW4GRc",
                    "username": "user",
                    "autostart": True,
                    "os_distro": "microsoft",
                    "nameservers": None,
                    "ssh_key_priv": None,
                    "net_bandwidth": 100,
                    "backup_size_max": 40,
                    "backup_supported": True,
                    "snapshot_size_max": 20,
                    "snapshot_supported": True
                },
                "settings": {
                    "notify_when_created": None
                },
                "prox_info": {
                    "cluster": 'prox-hn-1',
                    "node": 'pve02',
                    "vm_id": 108
                },
                "prox_status": {
                    "last_error": "Backend node not found",
                    "last_action": "create compute",
                    "last_action_time": 1598613327.625515
                }
            },
    }
}
USER_DATA2 = {
    'data': {
        "id": 4,
        'contents': {                      # <-- ODS production config
            'clusters': [
                {
                    'cluster': 'prox-hn-1',
                    'enabled': True,
                    'region_id': 'VN_HN',
                    'host': '172.16.5.31',
                    'port': 8006,
                    'username': 'portal@pve',
                    'password': 'Cas@2020',
                    'use_ssl': False,
                    'nodes': [
                        {
                            'node': 'pve01',
                            'os_mapping': {
                                'windows-server-2012': 101,
                                'windows-server-2016': 101,
                                'windows-server-2019': 101,
                                'windows-10': 101,
                                'ubuntu-server-16.04': 101,
                                'ubuntu-server-18.04': 101,
                                'ubuntu-server-20.04': 101,
                                'centos-7': 9001,
                                'centos-8': 9002,
                                'debian-9': 9004,
                                'debian-10': 9003,
                            }
                        },
                        {
                            'node': 'pve02',
                            'os_mapping': {
                                'windows-server-2012': 101,
                                'windows-server-2016': 101,
                                'windows-server-2019': 101,
                                'windows-10': 101,
                                'ubuntu-server-16.04': 9006,
                                'ubuntu-server-18.04': 9007,
                                'ubuntu-server-20.04': 9008,
                                'centos-7': 9001,
                                'centos-8': 9002,
                                'debian-9': 9004,
                                'debian-10': 9003,
                            }
                        },
                    ],
                    'target_nodes': None,
                    'ignored_nodes': None,
                    'qemu': {
                        'clone_type': 1,  # 1 - Full clone, 0 - Linked clone
                        'vm_id_prefix': ['1'],
                        'storage': 'ceph',
                        'snapshot_storage': 'ceph',
                        'backup_mode': 'snapshot',
                        'backup_storage': 'nfs',
                        'backup_lock_wait': 180,
                        'default_disk_type': 'scsi',
                        'default_disk_size': 20,
                        'default_disk_backup': 1,
                        'default_disk_replicate': 1,
                        'default_disk_shared': 1,
                        'default_read_iops': 10000,
                        'default_write_iops': 5000,
                        'default_disk_rerror': 'report',
                        'default_disk_werror': 'report',
                        'default_public_vlan_tag': 100,
                        'default_private_vlan_tag': 102,
                        'default_net_bandwidth': 100,
                    },
                    'netbox': {
                        'host': 'netbox.foxcloud.vn',
                        'port': 443,
                        'tenant': 'ODS',
                        'tenant_group': 'FPT',
                        'token': '5efcbbed9f33d6f7bf8a83ecff797bc265761eff',
                        'use_ssl': True,
                    },
                    'pfsense': {
                        'host': '42.112.37.203',
                        'port': 80,
                        'username': 'admin',
                        'password': 'Cas@2020',
                        'use_ssl': False,
                    }
                },

                {                       # <-- prox-hcm-1
                    'cluster': 'prox-hcm-1',
                    'enabled': True,
                    'region_id': 'VN_HCM',
                    'host': '172.16.5.2',
                    'port': 8006,
                    'username': 'root@pve',
                    'password': 'Cas@2020',
                    'use_ssl': False,
                    'nodes': [
                        {
                            'node': 'proxmox01',
                            'os_mapping': {
                                'windows-server-2012': 101,
                                'windows-server-2016': 101,
                                'windows-server-2019': 101,
                                'windows-10': 101,
                                'ubuntu-server-16.04': 101,
                                'ubuntu-server-18.04': 101,
                                'ubuntu-server-20.04': 101,
                                'centos-7': 101,
                                'centos-8': 101,
                                'debian-9': 101,
                                'debian-10': 101,
                            }
                        }
                    ],
                    'target_nodes': None,
                    'ignored_nodes': None,
                    'qemu': {
                        'clone_type': 1,
                        'vm_id_prefix': ['2'],
                        'storage': 'ceph',
                        'snapshot_storage': 'ceph',
                        'backup_mode': 'snapshot',
                        'backup_storage': 'nfs',
                        'backup_lock_wait': 180,
                        'default_disk_type': 'scsi',
                        'default_disk_size': 20,
                        'default_disk_backup': 1,
                        'default_disk_replicate': 1,
                        'default_disk_shared': 1,
                        'default_read_iops': 10000,
                        'default_write_iops': 5000,
                        'default_disk_rerror': 'report',
                        'default_disk_werror': 'report',
                        'default_public_vlan_tag': 100,
                        'default_private_vlan_tag': 102,
                        'default_net_bandwidth': 100,
                    },
                    'netbox': {
                        'host': 'netbox.foxcloud.vn',
                        'port': 443,
                        'tenant': 'ODS',
                        'tenant_group': 'FPT',
                        'token': '5efcbbed9f33d6f7bf8a83ecff797bc265761eff',
                        'use_ssl': True,
                    },
                    'pfsense': {
                        'host': '42.112.37.203',
                        'port': 80,
                        'username': 'admin',
                        'password': 'Cas@2020',
                        'use_ssl': False,
                    }
                },

            ],
            'target_clusters': None,
            'ignored_clusters': None,
        }
    },
}


ARGS = sys.argv[1:] or USER_ARGS
base.pp('ARGS:', ARGS)
MODEL = ARGS[0]
CMD = ARGS[1]

URL = base.URL_ADMIN_MODELS % MODEL if CMD == 'list' else base.URL_ADMIN_MODEL % MODEL
base.pp('URL:', URL)

r = requests.put(
    URL,
    headers={
        'Authorization': 'bearer %s' % (base.AUTH['access_token']),
    },
    json=USER_DATA,
    verify=base.VERIFY,
)
base.pp(json.dumps(r.json(encoding='utf-8'), indent=4))

with open('out_{}_{}.txt'.format(MODEL, CMD), 'w') as outfile:
    outfile.write(json.dumps(r.json(encoding='utf-8'), indent=4))
