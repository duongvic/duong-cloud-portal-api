#
# Copyright (c) 2020 FTI-CAS
#

from concurrent import futures
import functools
import re
import uuid

from application import app
from application.base import errors
from application import models as md
from application.product_types import compute_base
from application.product_types.openstack import os_api as client, constant
from application.utils import date_util, mail_util, str_util

LOG = app.logger
DEBUG = app.config['DEBUG']

SUPPORTED_ACTIONS = ['start', 'stop', 'pause', 'unpause',
                     'lock', 'unlock', 'suspend', 'resume',
                     'reboot']

ACTION_PERFORM_VM_ACTION = 'perform vm action'

VM_ACTION_STATUS = {
    'start': 'starting',
    'stop': 'stopping',
    'pause': 'pausing',
    'unpause': 'unpausing',
    'lock': 'locking',
    'unlock': 'unlocking',
    'suspend': 'suspending',
    'resume': 'resuming',
    'reboot': 'rebooting',
}

ACTION_GET_COMPUTE = 'get compute'
ACTION_GET_COMPUTES = 'get computes'
ACTION_CREATE_COMPUTE = 'create compute'
ACTION_UPDATE_COMPUTE = 'update compute'
ACTION_DELETE_COMPUTE = 'delete compute'

ACTION_GET_COMPUTE_STATUS = 'get compute status'
ACTION_GET_COMPUTE_CONFIG = 'get compute config'
ACTION_GET_COMPUTE_STATS = 'get compute stats'
ACTION_SYNCHRONIZE_COMPUTE = 'synchronize compute'

ACTION_GET_SNAPSHOT = 'get snapshot'
ACTION_GET_SNAPSHOTS = 'get snapshots'
ACTION_CREATE_SNAPSHOT = 'create snapshot'
ACTION_UPDATE_SNAPSHOT = 'update snapshot'
ACTION_DELETE_SNAPSHOT = 'delete snapshot'
ACTION_ROLLBACK_SNAPSHOT = 'rollback snapshot'

ACTION_GET_BACKUP_JOB = 'get backup job'
ACTION_GET_BACKUP_JOBS = 'get backup jobs'
ACTION_CREATE_BACKUP_JOB = 'create backup job'
ACTION_UPDATE_BACKUP_JOB = 'update backup job'
ACTION_DELETE_BACKUP_JOB = 'delete backup job'

ACTION_GET_BACKUP_FILE = 'get backup file'
ACTION_GET_BACKUP_FILES = 'get backup files'
ACTION_CREATE_BACKUP_FILE = 'create backup file'
ACTION_UPDATE_BACKUP_FILE = 'update backup file'
ACTION_DELETE_BACKUP_FILE = 'delete backup file'
ACTION_ROLLBACK_BACKUP_FILE = 'rollback backup file'

ACTION_CREATE_VOLUME = 'create volume'
ACTION_UPDATE_VOLUME = 'update volume'
ACTION_DELETE_VOLUME = 'delete volume'

ACTION_GET_SECGROUP = 'get secgroup'
ACTION_GET_SECGROUPS = 'get secgroups'
ACTION_CREATE_SECGROUP = 'create secgroup'
ACTION_UPDATE_SECGROUP = 'update secgroup'
ACTION_DELETE_SECGROUP = 'delete secgroup'

ACTION_GET_SECGROUP_RULE = 'get secgroup rule'
ACTION_GET_SECGROUP_RULES = 'get secgroup rules'
ACTION_CREATE_SECGROUP_RULE = 'create secgroup rule'
ACTION_UPDATE_SECGROUP_RULE = 'update secgroup rule'
ACTION_DELETE_SECGROUP_RULE = 'delete secgroup rule'


# Action timeout in seconds
ACTION_TIMEOUT = {
    ACTION_CREATE_COMPUTE: 120 if DEBUG else 1800,
    ACTION_UPDATE_COMPUTE: 120 if DEBUG else 300,
    ACTION_DELETE_COMPUTE: 120 if DEBUG else 600,

    ACTION_CREATE_VOLUME: 120 if DEBUG else 1800,
    ACTION_UPDATE_VOLUME: 120 if DEBUG else 300,
    ACTION_DELETE_VOLUME: 120 if DEBUG else 300,

    ACTION_CREATE_SNAPSHOT: 300 if DEBUG else 1800,
    ACTION_UPDATE_SNAPSHOT: 120 if DEBUG else 300,
    ACTION_DELETE_SNAPSHOT: 120 if DEBUG else 300,
    ACTION_ROLLBACK_SNAPSHOT: 300 if DEBUG else 3600,

    ACTION_CREATE_BACKUP_FILE: 300 if DEBUG else 1800,
    ACTION_UPDATE_BACKUP_FILE: 120 if DEBUG else 300,
    ACTION_DELETE_BACKUP_FILE: 120 if DEBUG else 300,
    ACTION_ROLLBACK_BACKUP_FILE: 300 if DEBUG else 3600,
}


class OSCompute(compute_base.OSComputeBase):
    """
    OpenStack Compute type.
    """

    def __init__(self):
        super().__init__()

    @property
    def supported(self):
        return True

    @property
    def supported_actions(self):
        return SUPPORTED_ACTIONS

    def on_get_computes(self, ctx, computes):
        """
        Called when computes loaded in get_computes().
        :param ctx:
        :param computes:
        :return:
        """
        all_computes = computes
        sync_computes_status = False
        if ctx.is_admin_request:
            # TODO in case admin has his own computes
            pass
        else:
            sync_computes_status = True

        if sync_computes_status:
            all_computes = []
            item_ctx = ctx.copy(task='synchronize compute status', data={})
            for compute in computes:
                item_ctx.data['compute'] = compute
                compute = self.do_load_compute(item_ctx) or compute
                all_computes.append(compute)

        return all_computes

    def do_load_compute(self, ctx):
        """
        Subclass should override this method.
        :param ctx:
        :return:
        """
        compute = super().do_load_compute(ctx)
        if not compute:
            return None

        # In case the compute is not disabled, the below code will
        # try to synchronize compute status with the backend. It also
        # unlock the compute if the last action fails or timed out.
        if compute.status != md.ComputeStatus.DISABLED:
            compute_need_update = False
            # Update status for compute (if backend resource is linked)
            os_info = compute.data.get('os_info') or {}
            if (compute.status == md.ComputeStatus.ENABLED
                    and os_info.get('cluster') and os_info.get('server_id')):
                compute_need_update = self._sync_compute_status(ctx, compute=compute, save=False)

            # If compute is locked, try to unlock it if we can
            if compute.status == md.ComputeStatus.LOCKED:
                target_status = None
                os_status = compute.data.get('os_status') or {}
                last_action = os_status.get('last_action') or ''
                last_action_time = os_status.get('last_action_time')
                last_error = os_status.get('last_error')

                # If last action failed then unlock the compute
                if last_error and last_action:
                    if last_action == ACTION_CREATE_COMPUTE:
                        target_status = md.ComputeStatus.FAILED
                    else:
                        target_status = md.ComputeStatus.ENABLED
                        compute.backend_status = constant.VM_STATUS_UNKNOWN
                else:  # Check for action timed out, if it did, then unlock the compute
                    timeout = ACTION_TIMEOUT.get(last_action)
                    if timeout and last_action_time:
                        action_time = date_util.utc_from_timestamp(last_action_time)
                        if date_util.utc_now() > date_util.datetime_add(action_time, seconds=timeout):
                            if last_action == ACTION_CREATE_COMPUTE:
                                target_status = md.ComputeStatus.FAILED
                            else:
                                target_status = md.ComputeStatus.ENABLED
                                compute.backend_status = constant.VM_STATUS_UNKNOWN

                if target_status is not None:
                    compute.status = target_status
                    compute_need_update = True

                # TODO khanhct If compute is locked, try to unlock it if we can
                # output = info.get('output')
                # if output:
                #     server_id = output['id']
                #     api = self._get_os_api(ctx=ctx, compute=compute)
                #     locked, locked_reason = api.get_locked_state(server_id=server_id)
                #     if locked:
                #         ret = api.unlock_server(server_id=server_id)
                #         if ret:
                #             # TODO Update compute status to database
                #             pass
                #         else:
                #             # TODO update locked reason
                #             pass

            if compute_need_update:
                md.save(compute)

        return compute

    def _sync_compute_status(self, ctx, compute, save=False):
        """
        Update VM status.
        :param compute:
        :return:
        """
        # TODO
        return False

    def _sync_compute_config(self, ctx, compute, save=False):
        """
        Update VM configuration.
        CPU/mem/disk/... may be updated in this function.
        :param ctx:
        :param compute:
        :param save:
        :return:
        """
        # TODO

    def _get_os_client_for_compute(self, ctx, info, engine='console', services='shade'):
        if not info.get('cluster'):
            e = ValueError('No mapping resource in backend for compute.')
            LOG.error(e)
            ctx.set_error(errors.BACKEND_CLUSTER_NOT_FOUND, cause=e, status=404)
            return

        return self.get_os_client(ctx, cluster=info['cluster'], engine=engine, services=services)

    def do_lock_compute(self, ctx, compute, purpose, backend_status=None, backend_lock=False):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :param purpose:
        :param backend_status:
        :param backend_lock:
        :return:
        """
        if backend_lock:
            os_info = compute.data['os_info']
            os_client = self._get_os_client_for_compute(ctx, info=os_info)
            if ctx.failed:
                return

            server_id = os_info['server_id']
            result = os_client.lock_server(server_id=server_id, reason=purpose)
            if result.get('error'):
                ctx.set_error(errors.COMPUTE_LOCK_FAILED, cause=result['error'], status=500)
                return

        last_action = purpose
        current_time = date_util.utc_now_as_sec()
        compute.data['os_status'].update({
            'last_action': last_action,
            'last_action_time': current_time,
            'last_error': None,
        })
        if backend_status is not None:
            compute.backend_status = backend_status
        compute.flag_modified('data')
        compute.status = md.ComputeStatus.LOCKED

        # Add some info to the history log
        action_timeout = ACTION_TIMEOUT.get(last_action)
        if action_timeout:
            ctx.log_args['action_timeout_at'] = current_time + action_timeout

    def do_unlock_compute(self, ctx, compute, purpose, target_status,
                          backend_status=None, backend_unlock=False, error=None):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :param purpose:
        :param target_status:
        :param backend_status:
        :param backend_unlock:
        :param error:
        :return:
        """
        try:
            if backend_unlock:
                os_info = compute.data['os_info']
                os_client = self._get_os_client_for_compute(ctx, info=os_info)
                if ctx.failed:
                    return

                server_id = os_info['server_id']
                err, _ = os_client.unlock_server(server_id=server_id)
                if err:
                    ctx.set_error(errors.COMPUTE_UNLOCK_FAILED, cause=err, status=500)
                    return

            os_status = compute.data['os_status']
            os_status.update({
                'last_action': purpose,
                'last_action_time': date_util.utc_now_as_sec(),
                'last_error': error,
            })
            if backend_status is not None:
                compute.backend_status = backend_status
            compute.flag_modified('data')
            if compute.status == md.ComputeStatus.LOCKED:
                compute.status = target_status
        finally:
            # Finish history log for the action
            save = ctx.failed
            # TODO: expires compute object
            self.finish_action_log(ctx, error=error, save=save)

    def init_compute_info(self, ctx, compute, order=None):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :param order:
        :return:
        """
        super().init_compute_info(ctx, compute=compute, order=order)
        if ctx.failed:
            return
        # TODO

    def do_recreate_compute(self, ctx, compute):
        """
        Override method from super class.
        :param ctx:
        :param compute:
        :return:
        """
        compute_info = compute.data['info']
        os_info = compute.data.get('os_info') or {}
        info = dict(os_info)
        info.update({
            'networks': compute_info.get('networks'),
            'volumes': compute_info.get('volumes'),
            'release_ip': False,  # Don't release the IP as we will use it soon
        })

        # Delete the backend VM associated with this compute first
        # as we will create another one.
        server_id = info.get('server_id')
        if server_id and os_info.get('cluster'):
            compute.backend_status = constant.VM_STATUS_UNKNOWN
            self.lock_compute(ctx, compute=compute, purpose=ACTION_DELETE_COMPUTE)
            if ctx.failed:
                return

            # Synchronously delete the backend compute
            os_client = self._get_os_client_for_compute(ctx, os_info)
            if ctx.failed:
                return
            os_client.delete_server(info=info)
        else:
            # Lock for creating compute
            compute.backend_status = constant.VM_STATUS_BUILD
            self.lock_compute(ctx, compute=compute, purpose=ACTION_CREATE_COMPUTE)
            if ctx.failed:
                return

    def do_create_compute(self, ctx, compute):
        """
        Override method from super class.
        :param ctx:
        :param compute:
        :return:
        """
        super().do_create_compute(ctx, compute=compute)
        if ctx.failed:
            return

        data = ctx.data
        compute_info = compute.data['info']

        passwd = data.get('password')
        passwd_enc = md.Compute.encrypt(passwd) if passwd else None
        ssh_key_priv = data.get('ssh_key_priv')
        ssh_key_enc = md.Compute.encrypt(ssh_key_priv) if ssh_key_priv else None
        username = data.get('username')

        compute_info.update({
            'username': username.strip() if username else None,
            'password': passwd_enc,
            'ssh_key': data.get('ssh_key'),
            'ssh_key_priv': ssh_key_enc,
        })

        cluster = self._find_target_cluster(ctx, compute=compute)
        if ctx.failed:
            return

        default_pub_net = cluster['os_info']['public_network']
        if not default_pub_net:
            e = ValueError('No default network found for provisioning new compute.')
            LOG.error(e)
            ctx.set_error(errors.BACKEND_DEFAULT_NET_NOT_FOUND, cause=e, status=404)
            return

        # TODO khanhct add more networks
        compute.data['info']['networks'].append({
            'name': default_pub_net['name'],
            'subnet': default_pub_net['subnet']['name'],
            'port_security_enabled': True,
            'admin_state_up': True,
            "net_flags": {
                "is_shared": True,
                "is_public": True,
                "is_existing": True,
            },
        })
        # self._add_network_ports(ctx, compute=compute)

        # Test only
        compute.data['info']['volumes'].append({
            "size": 10,
            "is_boot": True,
            "read_only": False,
            'vol_flags': {
                "is_existing": False,
            }
        })

        compute.data['info'].update({
            "placement_groups": {},
            "server_groups": {},
            "security_group": {
                "description": "description",
                "rules": [
                    {
                        "direction": "ingress",
                        "protocol": "tcp",
                        "ether_type": "IPv4",
                        "port_range": "80:80",
                        "source": "0.0.0.0",
                        "description": "https",
                        "remote_ip_prefix": "0.0.0.0/0"
                    },
                    {
                        "direction": "ingress",
                        "protocol": "tcp",
                        "ether_type": "IPv4",
                        "port_range": "22:22",
                        "source": "0.0.0.0",
                        "description": "ssh",
                        "remote_ip_prefix": "0.0.0.0/0"
                    }
                ]
            },
            "floating_ip": False,
            "server_group": "961b2051-e838-4a29-af9a-718325ad1eb7",
        })

        compute.data.update({
            'os_info': {
                'cluster': cluster['cluster'],
            },
            'os_status': {
                'last_action': ACTION_CREATE_COMPUTE,
                'last_action_time': date_util.utc_now_as_sec(),
                'last_error': None,
            },
        })
        compute.backend_status = constant.VM_STATUS_BUILD

        # Mark the data field is modified
        compute.flag_modified('data')

    def _add_network_ports(self, ctx, compute):
        compute_info = compute.data['info']
        network_ports = {}
        index = 0

        def _is_public(network):
            net_flags = network.get('net_flags')
            if net_flags:
                return False
            return net_flags.get(constant.IS_PUBLIC) or False

        for net in compute_info['networks']:
            net_port = {
                net['name']: {
                    'eth{}'.format(index): {
                        'local_ip': net.get('local_ip'),  # TODO fixed public IP
                        'netmask': net.get('netmask'),
                    }
                }
            }
            network_ports.update(net_port)
            index += 1

        compute_info['network_ports'] = network_ports

    def do_post_create_compute(self, ctx, compute, method='thread', on_result=None):
        """
        Override method from super class.
        :param ctx:
        :param compute:
        :param method:
        :param on_result:
        :return:
        """
        compute_info = compute.data['info']
        os_info = compute.data['os_info']

        cluster = self.get_os_cluster(ctx, cluster=os_info['cluster'])
        if ctx.failed:
            return
        cluster_name = cluster['cluster']

        user_os_info = ctx.target_user.data.get('os_info')
        if not user_os_info:
            e = ValueError('No OS user found.')
            LOG.error(e)
            ctx.set_error(errors.USER_OS_INFO_NOT_FOUND, cause=e, status=404)
            return

        image_mapping = cluster['os_info']['image_mapping']
        image = image_mapping[compute_info['os_name']]

        flavor = self._find_target_flavor(ctx, compute_info)
        if ctx.failed:
            return

        task_id = uuid.uuid4().hex
        stack_name = '{}.{}'.format(ctx.target_user.user_name, task_id[-8:])
        stack = {
            'name': stack_name,
            'task_id': task_id,
            'block': True,
            'timeout': ACTION_TIMEOUT.get(ACTION_CREATE_COMPUTE),
            'flags': {
                'no_setup': False,
                'no_teardown': False,
                'os_cloud_config': self.get_os_config(ctx, cluster=cluster_name),
            },
        }

        servers = [
            {
                'name': 'Compute-{}'.format(compute.id),
                'image': image,
                'flavor': flavor,
                'floating_ip': compute_info['floating_ip'],
                'server_group': compute_info.get('server_group'),
                'public_key': compute_info.get('ssh_key'),
                'username': compute_info.get('username'),
                'password': ctx.data.get('password'),  # password in compute_info is encrypted
                'volumes': compute_info['volumes'],
            }
        ]
        resources = {
            'placement_groups': compute_info.get('placement_groups') or {},
            'server_groups': compute_info.get('server_groups') or {},
            'networks': compute_info.get('networks') or [],
            'security_group': compute_info.get('security_group') or {},
            'servers': servers,
        }

        info = {
            'compute_id': compute.id,
            'stack': stack,
            'resources': resources,
        }

        os_client = self._get_os_client_for_compute(ctx, info=os_info, engine='heat')
        if ctx.failed:
            return

        return self._execute_client_func(ctx, compute=compute,
                                         func=functools.partial(os_client.create_compute, info=info),
                                         method=method,
                                         on_result=on_result or self.on_create_compute_result)

    def _execute_client_func(self, ctx, compute, func, method, on_result):
        """
        Execute client func
        """
        compute_id = compute.id

        def _on_result(ctx, result):
            compute = md.load(md.Compute, id=compute_id)
            # Check the compute
            if not compute:
                error = 'Compute not found in callback {}.'.format(ctx.task)
                LOG.error(error)
                self.finish_action_log(ctx, error=error, save=True)
            else:
                on_result(ctx=ctx, compute=compute, result=result)

        self.execute_client_func(ctx, func=func, method=method, on_result=_on_result)

    def _find_target_cluster(self, ctx, compute):
        """
        Find target cluster for provisioning compute.
        """
        # Find target cluster
        info = {
            'region_id': compute.region_id,
        }
        cluster = client.find_target_cluster(info=info)
        if not cluster:
            e = ValueError('No cluster found for provisioning new compute.')
            LOG.error(e)
            ctx.set_error(errors.BACKEND_CLUSTER_NOT_FOUND, cause=e, status=404)
            return

        ctx.response = {
            'cluster': cluster,
        }
        return cluster

    def _find_target_flavor(self, ctx, compute_info):
        """
        Find flavor for compute.
        :param ctx:
        :param compute_info:
        :return:
        """
        # TODO
        return 'm1.small'

    def on_create_compute_result(self, ctx, compute, result):
        """
        Create compute result.
        :param ctx:
        :param compute:
        :param result:
        :return:
        """
        task = ACTION_CREATE_COMPUTE
        error, data = result
        if not error:  # Success
            data = data['data']
            LOG.info('Compute create result:', data)
            server_info = self._parse_create_result(ctx, compute=compute, data=data)
            os_info = compute.data['os_info']
            os_info.update(server_info)

            cluster, server_id = os_info['cluster'], ''  # os_info['server_id']
            target_status = md.ComputeStatus.ENABLED
            backend_status = server_info['status']
            compute.backend_id = '{}/{}'.format(cluster, server_id)

            # Sync back VM config
            # self._sync_compute_config(ctx, compute=compute, save=False)

            # Update compute end date if need to
            if not compute.end_date:
                order = compute.order
                if not order.start_date:
                    order.start_date = date_util.utc_now()
                if not order.end_date:
                    order.end_date = date_util.datetime_add_duration(
                        order.start_date, order.duration)
                compute.end_date = order.end_date

            self.unlock_compute(ctx, compute=compute, purpose=task,
                                target_status=target_status, error=error,
                                backend_status=backend_status)

            # Send email to user if user wants
            settings = compute.data.get('settings') or {}
            notify_when_created = settings.get('notify_when_created')
            if notify_when_created in ('e-mail', 'email'):
                ssh_port = self.compute_config.get('compute_ssh_port') or 22
                mail_util.send_mail_compute_info(user=compute.user, compute=compute,
                                                 ssh_port=ssh_port)
        else:
            is_cancelled = error == 'task cancelled'
            target_status = md.ComputeStatus.FAILED
            backend_status = constant.VM_STATUS_UNKNOWN

            self.unlock_compute(ctx, compute=compute, purpose=task,
                                target_status=target_status, error=error,
                                backend_status=backend_status)
        if error:
            return {'error': error}

    def _parse_create_result(self, ctx, compute, data):
        """
        Parse stack output
        :param ctx:
        :param compute:
        :param data:
        :return:
        """
        result = {}
        if data.get('stack_status') == 'COMPLETE':
            instance = data['instances'][0]  # TODO fix
            addresses = instance.get('addresses')
            result['ports'] = addresses
            result['server_id'] = instance['id']
            result['status'] = instance['status']

        # info = compute.data['info']
        # stack_name = data['name']
        # server_ports = []
        # resources = data['resources']
        # for _, ports in sorted(info["network_ports"].items()):
        #     for port_name, _ in sorted(ports.items()):
        #         server_ports.append({
        #             'name': port_name,
        #             'ip': resources[str_util.h_join(stack_name, port_name, 'port-ip_address')],
        #             'mac': resources[str_util.h_join(stack_name, port_name, 'port-mac_address')],
        #         })
        # result['ports'] = server_ports
        # result['server_id'] = resources[stack_name]
        # result['console_url'] = resources[str_util.h_join(stack_name, 'console')]
        return result

    def _create_backend_status(self, status):
        """
        Create backend status from status data.
        :param status:
        :return: a string like: 'running', 'running (paused)'
        """
        bk_status = status.get('status')
        qmp_status = status.get('qmpstatus')
        if qmp_status != bk_status:
            bk_status += ' ({})'.format(qmp_status)
        return bk_status

    def do_update_compute(self, ctx, compute, sync=False, on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :param sync:
        :param on_result:
        :return:
        """
        data = ctx.data
        admin_roles = md.UserRole.admin_roles_of(compute_base.UPDATE_ROLES)
        is_admin = ctx.check_request_user_role(admin_roles)

        # Update name and desc
        if data.get('name'):
            compute.name = data['name']
        if data.get('description'):
            compute.description = data['description']

        # Status? for admin
        if is_admin:
            status = data.get('status')
            if status and md.ComputeStatus.is_valid(status):
                compute.status = status
                # If admin delete/disable compute, then stop it
                if status in (md.ComputeStatus.DELETED, md.ComputeStatus.DISABLED):
                    # Stop/Suspend compute
                    action = data.get('action_when_done') or 'suspend'
                    if action not in ('stop', 'shutdown', 'suspend'):
                        action = 'suspend'
                    vm_name = 'Compute-{}-{}'.format(compute.id, compute.status)
                    self._change_backend_compute(ctx, compute=compute, action=action,
                                                 name=vm_name)
                # Return here?
                return

        self.lock_compute(ctx, compute=compute, purpose=ACTION_UPDATE_COMPUTE)
        if ctx.failed:
            return

        compute_info = compute.data['info']
        os_info = compute.data['os_info']

        stack = os_info['stack']
        info = {
            'stack': {
                'task_id': stack['task_id'],
                'name': stack['name'],
                'block': not sync,
                'timeout': ACTION_TIMEOUT.get(ACTION_UPDATE_COMPUTE),
                'flags': {
                    'no_setup': False,
                    'no_teardown': False,
                    'os_cloud_config': self._get_os_config(ctx=ctx, compute=compute)
                }
            },
            'resources': {
                **compute_info
            }
        }

        return self._execute_client_func(ctx, compute=compute,
                                         func=client.update_stack,
                                         info=info, sync=sync,
                                         on_result=on_result or self.on_update_compute_result)

    def on_update_compute_result(self, ctx, compute, result):
        """
        Update compute callback.
        :param ctx:
        :param compute:
        :param result:
        :return:
        """
        task = ACTION_UPDATE_COMPUTE
        if not compute:
            LOG.error('Compute not found at {}.'.format(task))
            return
        compute_id = compute.id

        os_error = result.get('error')
        if os_error:
            is_cancelled = os_error == 'task cancelled'
            LOG.error('Failed to update compute {} in the backend. Error {}.'
                      .format(compute_id, os_error))

        target_status = md.ComputeStatus.ENABLED
        self.unlock_compute(ctx, compute=compute, purpose=task,
                            target_status=target_status, error=os_error, backend_status=None)

    def do_release_compute_resource(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def do_delete_compute(self, ctx, compute, lock=True, sync=False, on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :param lock:
        :param sync:
        :param on_result:
        :return:
        """
        if lock:
            self.lock_compute(ctx, compute=compute, purpose=ACTION_DELETE_COMPUTE)
            if ctx.failed:
                return

        os_info = compute.data['os_info']
        os_stack = os_info.get('stack')

        info = {}
        if os_stack:
            info = {
                'stack': {
                    'task_id': os_stack['task_id'],
                    'name': os_stack['name'],
                    'block': not sync,
                    'timeout': ACTION_TIMEOUT.get(ACTION_DELETE_COMPUTE),
                    'flags': {
                        'no_setup': True,
                        'no_teardown': False,
                        'os_cloud_config': self._get_os_config(ctx=ctx, compute=compute)
                    }
                },
                'resources': None
            }

        return self._execute_client_func(ctx, compute=compute,
                                         func=client.delete_stack,
                                         info=info, sync=sync,
                                         on_result=on_result or self.on_delete_compute_result)

    def on_delete_compute_result(self, ctx, compute, result):
        """
        Delete compute callback.
        :param ctx:
        :param compute:
        :param result:
        :return:
        """
        task = ACTION_DELETE_COMPUTE
        if not compute:
            LOG.error('Compute not found at {}.'.format(task))
            return
        compute_id = compute.id

        os_error = result.get('error')
        if not os_error:  # Success
            error = md.remove(compute)
            if error:
                LOG.error('Failed to delete compute {} from database. Error: {}.'
                          .format(compute_id, error))
                return
        else:
            is_cancelled = os_error == 'task cancelled'
            LOG.error('Failed to remove compute {} in the backend.'
                      .format(compute_id))
            target_status = md.ComputeStatus.FAILED
            backend_status = constant.VM_STATUS_UNKNOWN
            self.unlock_compute(ctx, compute=compute, purpose=task,
                                target_status=target_status, error=os_error, backend_status=backend_status)

    #######################################################
    # COMPUTE STATS
    #######################################################

    def do_get_compute_stats(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    #######################################################
    # COMPUTE STATUS
    #######################################################

    def do_get_compute_status(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """
        os_info = compute.data['os_info']

        os_client = self._get_os_client_for_compute(ctx, info=os_info)
        if ctx.failed:
            return

    #######################################################
    # COMPUTE ACTION
    #######################################################

    def do_perform_action(self, ctx, compute, method='thread', on_result=None):
        """
        Override method from super class.
        :param ctx:
        :param compute:
        :param method:
        :param on_result:
        :return:
        """
        data = ctx.data
        action = data['action']

        self.lock_compute(ctx, compute=compute, purpose=ACTION_PERFORM_VM_ACTION,
                          backend_status=VM_ACTION_STATUS[action])
        if ctx.failed:
            return

        os_info = compute.data['os_info']
        info = {
            'server_id': os_info['server_id'],
            'action': action,
        }

        os_client = self._get_os_client_for_compute(ctx, info=os_info)
        if ctx.failed:
            return
        return self._execute_client_func(ctx, compute=compute,
                                         func=functools.partial(os_client.perform_server_action, **info),
                                         method=method,
                                         on_result=on_result or self.on_perform_action_result)

    def on_perform_action_result(self, ctx, compute, result):
        """
        Update status callback.
        :param ctx:
        :param compute:
        :param result:
        :return:
        """
        task = ACTION_PERFORM_VM_ACTION
        if not compute:
            LOG.error('Compute not found at {}.'.format(task))
            return

        error, data = result
        backend_status = compute.backend_status
        if error:
            is_cancelled = error == 'task cancelled'

        target_status = md.ComputeStatus.ENABLED
        self.unlock_compute(ctx, compute=compute, purpose=task,
                            target_status=target_status, error=error,
                            backend_status=backend_status)

    #######################################################
    # SEC GROUP
    #######################################################

    def do_get_secgroup(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """
        data = ctx.data
        os_info = compute.data['os_info']

        os_client = self._get_os_client_for_compute(ctx, info=os_info)
        if ctx.failed:
            return

        error, sec_group = os_client.get_security_group(id=data['secgroup_id'])
        if error:
            ctx.set_error(errors.COMPUTE_SG_GET_FAILED, cause=error, status=500)
            return
        rules = []
        if sec_group:
            rules = self._parse_secgroup_rules(sec_group.get('security_group_rules') or [])
        response = {
            'id': sec_group['id'],
            'name': sec_group.get('name'),
            'description': sec_group.get('description'),
            'rules': rules
        }
        ctx.response = response
        return response

    def do_get_secgroups(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """
        os_info = compute.data['os_info']

        os_client = self._get_os_client_for_compute(ctx, info=os_info)
        if ctx.failed:
            return
        listing = self.parse_ctx_listing(ctx)
        error, sec_groups = os_client.get_server_security_groups(server_id=os_info['server_id'],
                                                                 listing=listing)
        if error:
            ctx.set_error(errors.COMPUTE_SG_GET_FAILED, cause=error, status=500)
            return
        sec_groups_ = []
        for sg in sec_groups['data']:
            rules = self._parse_secgroup_rules(sg.get('rules') or [])
            sec_groups_.append({
                'id': sg['id'],
                'name': sg.get('name'),
                'description': sg.get('description'),
                'rules': rules
            })
        response = {
            'data': sec_groups_,
            "has_more": sec_groups['has_more'],
            "next_page": sec_groups['next_page'],
            "prev_page": sec_groups['prev_page'],
        }
        ctx.response = response
        return response

    def _parse_secgroup_rules(self, sg_rules):
        """
        """
        rules = []
        for rule in sg_rules:
            rules.append(self._parse_secgroup_rule(rule))
        return rules

    def _parse_secgroup_rule(self, rule):
        if rule:
            port_range_min = rule.get('from_port') or rule.get('port_range_min')
            port_range_max = rule.get('to_port') or rule.get('port_range_max')
            port_range = 'Any' if not (port_range_min and port_range_max) \
                else '{}:{}'.format(port_range_min, port_range_max)
            ip_range = rule.get('ip_range', {}) or {}
            remote_ip_prefix = rule.get('remote_ip_prefix')
            return {
                'id': rule['id'],
                'direction': rule.get('direction') or 'Any',
                'ether_type': rule.get('ethertype', 'Any'),
                'port_range': port_range,
                'source_ip': ip_range.get('cidr') or remote_ip_prefix,
                'protocol': rule.get('ip_protocol') or rule.get('protocol'),
            }
        return None

    def do_create_secgroup(self, ctx, compute, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """
        data = ctx.data
        self.lock_compute(ctx, compute=compute, purpose=ACTION_CREATE_SECGROUP_RULE)
        if ctx.failed:
            return

        os_info = compute.data['os_info']
        # TODO need to verify secgroup
        os_client = self._get_os_client_for_compute(ctx, info=os_info)
        if ctx.failed:
            return

        sg = {
            'server_id': os_info.get('server_id'),
            'secgroup_ids': [data['secgroup_id']]
        }
        return self._execute_client_func(ctx, compute=compute,
                                         func=functools.partial(os_client.attach_server_security_groups, **sg),
                                         method=method,
                                         on_result=on_result or self.on_create_secgroup_result)

    def on_create_secgroup_result(self, ctx, compute, result):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """
        task = ACTION_CREATE_SECGROUP
        error, sec_group = result
        if error:
            ctx.set_error(errors.COMPUTE_SG_UPDATE_FAILED, cause=error, status=500)
        ctx.response = sec_group

        is_cancelled = error == 'task cancelled'
        target_status = md.ComputeStatus.ENABLED

        self.unlock_compute(ctx, compute=compute, purpose=task,
                            target_status=target_status, error=error)

    def do_update_secgroup(self, ctx, compute, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_update_secgroup_result(self,  ctx, compute, result):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def do_delete_secgroup(self, ctx, compute, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """
        data = ctx.data
        self.lock_compute(ctx, compute=compute, purpose=ACTION_CREATE_SECGROUP_RULE)
        if ctx.failed:
            return

        os_info = compute.data['os_info']
        # TODO need to verify secgroup
        os_client = self._get_os_client_for_compute(ctx, info=os_info)
        if ctx.failed:
            return

        secgroup = {
            'secgroup_id': data['secgroup_id'],
            'server_id': os_info.get('server_id'),
        }
        return self._execute_client_func(ctx, compute=compute,
                                         func=functools.partial(os_client.remove_server_security_group, **secgroup),
                                         method=method,
                                         on_result=on_result or self.on_delete_secgroup_result)

    def on_delete_secgroup_result(self, ctx, compute, result):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """
        task = ACTION_UPDATE_SECGROUP
        error, sec_group = result
        if error:
            ctx.set_error(errors.COMPUTE_SG_UPDATE_FAILED, cause=error, status=500)
        ctx.response = sec_group

        is_cancelled = error == 'task cancelled'
        target_status = md.ComputeStatus.ENABLED

        self.unlock_compute(ctx, compute=compute, purpose=task,
                            target_status=target_status, error=error)

    def do_create_secgroup_rule(self, ctx, compute, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """
        data = ctx.data

        self.lock_compute(ctx, compute=compute, purpose=ACTION_CREATE_SECGROUP_RULE)
        if ctx.failed:
            return

        os_info = compute.data['os_info']
        port_range = data['port_range']
        if port_range:
            port_range_arr = port_range.split(":")
            max_port = int(port_range_arr[1])
            min_port = int(port_range_arr[0])
            if (min_port > max_port) or (min_port < 1) and (max_port > 65535):
                LOG.warning("Ports out of ranger %s", port_range)
                raise Exception("Ports out of ranger %s", port_range)
        else:
            raise Exception("Ports out of ranger %s", port_range)

        info = {
            'id': data['id'],
            'protocol': data['protocol'],
            'direction': data['direction'],
            'ethertype': data['ether_type'],
            'port_range_max': max_port,
            'port_range_min': min_port,
            'remote_ip_prefix': data['source_ip']
        }

        os_client = self._get_os_client_for_compute(ctx, info=os_info)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, compute=compute,
                                         func=functools.partial(os_client.create_security_group_rule, info=info),
                                         method=method,
                                         on_result=on_result or self.on_create_secgroup_rule_result)

    def on_create_secgroup_rule_result(self, ctx, compute, result):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """
        task = ACTION_CREATE_SECGROUP_RULE
        error, data = result
        if error:
            LOG.error('Error updating sg rule: {}.'.format(error))
            ctx.set_error(errors.COMPUTE_SG_RULE_CREATE_FAILED, cause=error, status=500)
        else:
            ctx.response = self._parse_secgroup_rule(data)

        is_cancelled = error == 'task cancelled'
        target_status = md.ComputeStatus.ENABLED

        self.unlock_compute(ctx, compute=compute, purpose=task,
                            target_status=target_status, error=error)

    def do_update_secgroup_rule(self, ctx, compute, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_update_secgroup_rule_result(self, ctx, compute, result):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def do_delete_secgroup_rule(self, ctx, compute, method='sync', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """
        data = ctx.data

        self.lock_compute(ctx, compute=compute, purpose=ACTION_DELETE_SECGROUP_RULE)
        if ctx.failed:
            return

        os_info = compute.data['os_info']
        os_client = self._get_os_client_for_compute(ctx, info=os_info)
        if ctx.failed:
            return

        info = {
            'rule_id': data['rule_id']
        }
        return self._execute_client_func(ctx, compute=compute,
                                         func=functools.partial(os_client.delete_security_group_rule, info=info),
                                         method=method,
                                         on_result=on_result or self.on_delete_secgroup_rule_result)

    def on_delete_secgroup_rule_result(self, ctx, compute, result):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """
        task = ACTION_DELETE_SECGROUP_RULE
        error, data = result
        if error:
            LOG.error('Error updating sg rule: {}.'.format(error))
            ctx.set_error(errors.COMPUTE_SG_RULE_DELETE_FAILED, cause=error, status=500)

        if not data:
            ctx.set_error(errors.COMPUTE_SG_RULE_DELETE_FAILED, cause=error, status=500)

        is_cancelled = error == 'task cancelled'
        target_status = md.ComputeStatus.ENABLED

        self.unlock_compute(ctx, compute=compute, purpose=task,
                            target_status=target_status, error=error)

    #######################################################
    # SNAPSHOT
    #######################################################

    @property
    def snapshot_supported(self):
        return True

    def do_get_snapshot(self, ctx, compute):
        """
        Override method from super class.
        :param ctx:
        :param compute:
        :return:
        """
        data = ctx.data
        os_info = compute.data['os_info']
        os_client = self._get_os_client_for_compute(ctx, info=os_info)
        if ctx.failed:
            return
        listing = self.parse_ctx_listing(ctx)
        error, snapshot = os_client.get_snapshot(snapshot_id=data['snapshot_id'], listing=listing)
        if error:
            ctx.set_error(errors.COMPUTE_SNAPSHOT_GET_FAILED, cause=error, status=500)
            return

        ctx.response = snapshot
        return snapshot

    def do_get_snapshots(self, ctx, compute):
        """
        Override method from super class.
        :param ctx:
        :param compute:
        :return:
        """
        data = ctx.data
        os_info = compute.data['os_info']

        filters = None
        info = {
            'volume_id': data.get('volume_id'),
            'server_id': os_info.get('server_id'),
            'detailed': True,
            'filters': filters,
        }

        os_client = self._get_os_client_for_compute(ctx, info=os_info)
        if ctx.failed:
            return

        listing = self.parse_ctx_listing(ctx)
        error, snapshots = os_client.get_snapshots(info=info, listing=listing)
        if error:
            ctx.set_error(errors.COMPUTE_SNAPSHOT_GET_FAILED, cause=error, status=500)
            return

        ctx.response = snapshots
        return snapshots

    def do_create_snapshot(self, ctx, compute, method='thread', on_result=None):
        """
        Override method from super class.
        :param ctx:
        :param compute:
        :param method:
        :param on_result:
        :return:
        """
        data = ctx.data
        name = data['name']
        description = data.get('description')

        if not self._validate_snapshot_name(name):
            e = ValueError('Snapshot name "{}" invalid. Allows [A-Z][a-z][0-9][_] only.'
                           .format(name))
            ctx.set_error(errors.COMPUTE_SNAPSHOT_NAME_INVALID, cause=e, status=406)
            return

        self.lock_compute(ctx, compute=compute, purpose=ACTION_CREATE_SNAPSHOT)
        if ctx.failed:
            return

        os_info = compute.data['os_info']
        info = {
            'server_id': os_info['server_id'],
            'force': True,
            'timeout': ACTION_TIMEOUT.get(ACTION_CREATE_SNAPSHOT),
            'name': name,
            'description': description,
        }

        os_client = self._get_os_client_for_compute(ctx, info=os_info)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, compute=compute,
                                         func=functools.partial(os_client.create_snapshot, info=info),
                                         method=method,
                                         on_result=on_result or self.on_create_snapshot_result)

    def _validate_snapshot_name(self, name):
        """
        Validate snapshot name.
        :param name:
        :return:
        """
        pattern = '^[A-Za-z][A-Za-z0-9_]+$'
        return True if re.match(pattern, name) else False

    def on_create_snapshot_result(self, ctx, compute, result):
        """
        Create snapshot callback.
        :param ctx:
        :param compute:
        :param result:
        :return:
        """
        task = ACTION_CREATE_SNAPSHOT
        error, data = result
        if error:
            LOG.error('Error creating snapshot: {}.'.format(error))

        is_cancelled = error == 'task cancelled'
        target_status = md.ComputeStatus.ENABLED

        self.unlock_compute(ctx, compute=compute, purpose=task,
                            target_status=target_status, error=error)

    def do_update_snapshot(self, ctx, compute, method='thread', on_result=None):
        """
        Override method from super class.
        :param ctx:
        :param compute:
        :param method:
        :param on_result:
        :return:
        """
        data = ctx.data
        name = data['name']
        description = data.get('description')
        snapshot_id = data['snapshot_id']

        if not self._validate_snapshot_name(name):
            e = ValueError('Snapshot name "{}" invalid. Allows [A-Z][a-z][0-9][_] only.'
                           .format(name))
            ctx.set_error(errors.COMPUTE_SNAPSHOT_NAME_INVALID, cause=e, status=406)
            return

        os_info = compute.data['os_info']
        os_client = self._get_os_client_for_compute(ctx, info=os_info)
        if ctx.failed:
            return

        if not self._snapshot_exists(client=os_client, snapshot_id=snapshot_id):
            ctx.set_error(errors.COMPUTE_SNAPSHOT_NOT_FOUND, status=404)
            return

        self.lock_compute(ctx, compute=compute, purpose=ACTION_UPDATE_SNAPSHOT)
        if ctx.failed:
            return

        info = {
            'snapshot_id': snapshot_id,
            'name': name,
            'description': description,
        }
        return self._execute_client_func(ctx, compute=compute,
                                         func=functools.partial(os_client.update_snapshot, info=info),
                                         method=method,
                                         on_result=on_result or self.on_update_snapshot_result)

    def on_update_snapshot_result(self, ctx, compute, result):
        """
        Update snapshot callback.
        :param ctx:
        :param compute:
        :param result:
        :return:
        """
        task = ACTION_UPDATE_SNAPSHOT
        error, data = result
        if error:
            LOG.error('Error updating snapshot: {}.'.format(error))

        is_cancelled = error == 'task cancelled'
        target_status = md.ComputeStatus.ENABLED
        self.unlock_compute(ctx, compute=compute, purpose=task,
                            target_status=target_status, error=error)

    def _snapshot_exists(self, client, snapshot_id):
        """
        Check snapshot exists.
        :param client:
        :param snapshot_id:
        :return:
        """
        error, _ = client.get_snapshot(snapshot_id=snapshot_id)
        return False if error else True

    def do_delete_snapshot(self, ctx, compute, method='thread', on_result=None):
        """
        Override method from super class.
        :param ctx:
        :param compute:
        :param method:
        :param on_result:
        :return:
        """
        data = ctx.data
        snapshot_id = data['snapshot_id']

        os_info = compute.data['os_info']
        os_client = self._get_os_client_for_compute(ctx, info=os_info)
        if ctx.failed:
            return

        if not self._snapshot_exists(client=os_client, snapshot_id=snapshot_id):
            ctx.set_error(errors.COMPUTE_SNAPSHOT_NOT_FOUND, status=404)
            return

        self.lock_compute(ctx, compute=compute, purpose=ACTION_DELETE_SNAPSHOT)
        if ctx.failed:
            return

        info = {
            'force': True,
            'snapshot_id': snapshot_id,
        }
        return self._execute_client_func(ctx, compute=compute,
                                         func=functools.partial(os_client.delete_snapshot, info=info),
                                         method=method,
                                         on_result=on_result or self.on_delete_snapshot_result)

    def on_delete_snapshot_result(self, ctx, compute, result):
        """
        Delete snapshot callback
        :param ctx:
        :param compute:
        :param result:
        :return:
        """
        task = ACTION_DELETE_SNAPSHOT
        error, data = result
        if error:
            LOG.error('Error deleting snapshot: {}.'.format(error))

        is_cancelled = error == 'task cancelled'
        target_status = md.ComputeStatus.ENABLED
        self.unlock_compute(ctx, compute=compute, purpose=task,
                            target_status=target_status, error=error)

    def do_rollback_snapshot(self, ctx, compute, method='thread', on_result=None):
        """
        Override method from super class.
        :param ctx:
        :param compute:
        :param method:
        :param on_result:
        :return:
        """
        data = ctx.data
        volume_id = data['volume_id']
        snapshot_id = data['snapshot_id']

        self.lock_compute(ctx, compute=compute, purpose=ACTION_ROLLBACK_SNAPSHOT)
        if ctx.failed:
            return

        os_info = compute.data['os_info']
        os_client = self._get_os_client_for_compute(ctx, info=os_info)
        if ctx.failed:
            return

        error, status = os_client.get_server_status(server_id=os_info['server_id'])
        if error:
            ctx.set_error(errors.COMPUTE_GET_STATUS_FAILED, cause=error, status=406)
            return

        if status == constant.VM_STATUS_ACTIVE:
            e = 'Compute {} required to be off to rollback snapshot.'.format(compute.id)
            ctx.set_error(errors.COMPUTE_IS_RUNNING, cause=e, status=406)
            return

        info = {
            'type': 'volume',
            'server_id': os_info['server_id'],
            'volume_id': volume_id,
            'snapshot_id': snapshot_id,
        }
        return self._execute_client_func(ctx, compute=compute,
                                         func=functools.partial(os_client.rollback_snapshot, info),
                                         method=method,
                                         on_result=on_result or self.on_rollback_snapshot_result)

    def on_rollback_snapshot_result(self, ctx, compute, result):
        """
        Rollback snapshot callback.
        :param ctx:
        :param compute:
        :param result:
        :return:
        """
        task = ACTION_ROLLBACK_SNAPSHOT
        error, data = result
        if error:
            LOG.error('Error rolling back snapshot: {}.'.format(error))

        is_cancelled = error == 'task cancelled'
        target_status = md.ComputeStatus.ENABLED
        self.unlock_compute(ctx, compute=compute, purpose=task,
                            target_status=target_status, error=error)

    #######################################################
    # BACKUP JOB
    #######################################################

    # TODO

    #######################################################
    # BACKUP FILE
    #######################################################

    def do_get_backup_file(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """
        data = ctx.data

        os_info = compute.data['os_info']
        os_client = self._get_os_client_for_compute(ctx, info=os_info)
        if ctx.failed:
            return

        listing = self.parse_ctx_listing(ctx)
        error, data = os_client.get_backup(backup_id=data['backup_id'], listing=listing)
        if error:
            ctx.set_error(errors.COMPUTE_BACKUP_GET_FAILED, cause=error, status=500)
            return

        ctx.response = data
        return data

    def do_get_backup_files(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """
        data = ctx.data
        os_info = compute.data['os_info']

        info = {
            'volume_id': data.get('volume_id'),
            'server_id': os_info['server_id'],
            'detailed': True,
            'filters': None,
        }

        os_client = self._get_os_client_for_compute(ctx, info=os_info)
        if ctx.failed:
            return

        listing = self.parse_ctx_listing(ctx)
        error, backups = os_client.get_backups(info=info, listing=listing)
        if error:
            ctx.set_error(errors.COMPUTE_BACKUP_FILE_GET_FAILED, cause=error, status=500)
            return

        ctx.response = backups
        return backups

    def do_create_backup_file(self, ctx, compute, method='thread', on_result=None):
        """
        Override method from super class.
        :param ctx:
        :param compute:
        :param method:
        :param on_result:
        :return:
        """
        self.lock_compute(ctx, compute=compute, purpose=ACTION_CREATE_BACKUP_FILE)
        if ctx.failed:
            return

        data = ctx.data
        os_info = compute.data['os_info']

        info = {
            'server_id': os_info['server_id'],
            'name': data['name'],
            'description': data.get('description'),
            'force': True,
        }

        os_client = self._get_os_client_for_compute(ctx, info=os_info)
        if ctx.failed:
            return

        return self._execute_client_func(ctx, compute=compute,
                                         func=functools.partial(os_client.create_backup, info=info),
                                         method=method,
                                         on_result=on_result or self.on_create_backup_file_result)

    def on_create_backup_file_result(self, ctx, compute, result):
        """
        Create backup callback.
        :param ctx:
        :param compute:
        :param result:
        :return:
        """
        task = ACTION_CREATE_BACKUP_FILE
        error, data = result
        if error:
            LOG.error('Failed to create backup file. Error {}.'.format(error))

        is_cancelled = error == 'task cancelled'
        target_status = md.ComputeStatus.ENABLED

        self.unlock_compute(ctx, compute=compute, purpose=task,
                            target_status=target_status, error=error)

    def do_update_backup_file(self, ctx, compute, method='thread', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :param method:
        :param on_result:
        :return:
        """

    def on_update_backup_file_result(self, ctx, compute, result):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :param result:
        :return:
        """

    def do_delete_backup_file(self, ctx, compute, method='thread', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :param method:
        :param on_result:
        :return:
        """
        data = ctx.data

        self.lock_compute(ctx, compute=compute, purpose=ACTION_DELETE_SNAPSHOT)
        if ctx.failed:
            return

        os_info = compute.data['os_info']
        os_client = self._get_os_client_for_compute(ctx, info=os_info)
        if ctx.failed:
            return

        info = {
            'backup_id': data['backup_id'],
            'force': False,
        }
        return self._execute_client_func(ctx, compute=compute,
                                         func=functools.partial(os_client.delete_backup, **info),
                                         method=method,
                                         on_result=on_result or self.on_delete_backup_file_result)

    def on_delete_backup_file_result(self, ctx, compute, result):
        """
        Delete backup callback.
        :param ctx:
        :param compute:
        :param result:
        :return:
        """
        task = ACTION_DELETE_BACKUP_FILE
        error, data = result
        if error:
            LOG.error('Failed to delete backup file. Error {}.'.format(error))

        is_cancelled = error == 'task cancelled'
        target_status = md.ComputeStatus.ENABLED

        self.unlock_compute(ctx, compute=compute, purpose=task,
                            target_status=target_status, error=error)

    def do_rollback_backup_file(self, ctx, compute, method='thread', on_result=None):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :param method:
        :param on_result:
        :return:
        """
        data = ctx.data
        os_info = compute.data['os_info']

        os_client = self._get_os_client_for_compute(ctx, info=os_info)
        if ctx.failed:
            return

        error, status = os_client.get_server_status(server_id=os_info['server_id'])
        if error:
            ctx.set_error(errors.COMPUTE_GET_STATUS_FAILED, cause=error, status=500)
            return

        if status == constant.VM_STATUS_ACTIVE:
            e = 'Compute {} required to be off to restore backup.'.format(compute.id)
            ctx.set_error(errors.COMPUTE_IS_RUNNING, cause=e, status=406)
            return

        self.lock_compute(ctx, compute=compute, purpose=ACTION_ROLLBACK_BACKUP_FILE)
        if ctx.failed:
            return

        backup_id = data['backup_id']
        volume_id = data['volume_id']
        error, _ = os_client.reset_volume_state(volume_id=volume_id, state='available')
        if error:
            ctx.set_error(errors.BACKEND_ERROR, cause=error, status=500)
            return

        info = {
            'backup_id': backup_id,
            'volume_id': volume_id,
            'name': data.get('name'),
        }

        return self._execute_client_func(ctx, compute=compute,
                                         func=functools.partial(os_client.restore_backup, **info),
                                         method=method,
                                         on_result=on_result or self.on_rollback_backup_file_result)

    def on_rollback_backup_file_result(self, ctx, compute, result):
        """
        Rollback backup callback.
        :param ctx:
        :param compute:
        :param result:
        :return:
        """
        task = ACTION_ROLLBACK_BACKUP_FILE
        error, data = result
        if error:
            LOG.error('Failed to restore backup file. Error {}.'.format(error))

        is_cancelled = error == 'task cancelled'
        target_status = md.ComputeStatus.ENABLED

        self.unlock_compute(ctx, compute=compute, purpose=task,
                            target_status=target_status, error=error)