#
# Copyright (c) 2020 FTI-CAS
#

import re

from application import app
from application.base import errors
from application.base.context import create_admin_context
from application.managers import base as base_mgr, task_mgr, user_mgr
from application import models as md
from application.product_types import base, os_base
from application.utils import data_util, date_util, mail_util, str_util

LOG = app.logger
DEBUG = app.config['DEBUG']
DEBUG_NO_CHECK_COMPUTE = True if DEBUG else False

ADMIN_ROLES = (md.UserRole.ADMIN, md.UserRole.ADMIN_SALE, md.UserRole.ADMIN_IT)
GET_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
LIST_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
CREATE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)
UPDATE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)
DELETE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)

ENABLED_STATUS = (md.ComputeStatus.ENABLED, md.ComputeStatus.LOCKED)
ENABLED_UNLOCKED_STATUS = (md.ComputeStatus.ENABLED,)

DEFAULT_SNAPSHOT_FILE_MAX_ALLOWED = 50
DEFAULT_SNAPSHOT_SIZE_MAX_ALLOWED = 1000000  # 1000 TB
DEFAULT_BACKUP_JOB_MAX_ALLOWED = 50
DEFAULT_BACKUP_FILE_MAX_ALLOWED = 1000  # 1000 files
DEFAULT_BACKUP_SIZE_MAX_ALLOWED = 1000000  # 1000 TB


class OSComputeBase(os_base.OSBase):
    """
    Compute product type.
    """
    type = md.ProductType.COMPUTE

    def __init__(self):
        super().__init__()

        # Load config
        compute_config = md.query(md.Configuration,
                                  type=md.ConfigurationType.COMPUTE,
                                  name='compute_config',
                                  status=md.ConfigurationStatus.ENABLED,
                                  order_by=md.Configuration.version.desc()).first()
        if not compute_config:
            raise ValueError('Config COMPUTE/compute_config not found in database.')
        self.compute_config = compute_config.contents

        # Register some background tasks
        scheduler = task_mgr.get_scheduler()
        scheduler.add_job(self.run_bg_task_daily, id='compute.run_bg_task_daily',
                          **app.config['JOB_SYNC_COMPUTES_DAILY'])

    @property
    def supported_actions(self):
        """
        Supported actions on compute.
        :return:
        """
        return []

    def load_compute(self, ctx, check=True, **kwargs):
        """
        Load compute object from DB.
        :param ctx:
        :param check:
        :param kwargs: args will be passed to check_compute() method.
        :return:
        """
        compute = self.do_load_compute(ctx)
        if not compute:
            ctx.set_error(errors.COMPUTE_NOT_FOUND, status=404)
            return

        if check:
            self.check_compute(ctx, compute=compute, **kwargs)
            if ctx.failed:
                return

        return compute

    def do_load_compute(self, ctx):
        """
        Subclass should override this method.
        :param ctx:
        :return:
        """
        data = ctx.data
        compute = md.load_compute(data.get('compute') or data['compute_id'])
        if compute.user_id != ctx.request_user.id:
            ctx.target_user = md.load_user(compute.user_id)
        return compute

    def check_compute(self, ctx, compute,
                      check_roles=None,
                      check_status=ENABLED_UNLOCKED_STATUS,
                      check_expired=False):
        """
        Check a compute for permission and availability.
        :param ctx:
        :param compute:
        :param check_roles: a list of roles to check
        :param check_status: a list of statuses to check
        :param check_expired:
        :return:
        """
        if DEBUG_NO_CHECK_COMPUTE:
            return True

        if not user_mgr.check_user(ctx, roles=check_roles):
            return False

        if compute.user_id != ctx.request_user.id and not ctx.check_request_user_role(ADMIN_ROLES):
            ctx.set_error(errors.USER_ACTION_NOT_ALLOWED, status=403)
            return False

        if check_status and compute.status not in check_status:
            ctx.set_error(errors.COMPUTE_NOT_AVAILABLE, status=406)
            return False

        if check_expired and compute.expired:
            ctx.set_error(errors.COMPUTE_NOT_AVAILABLE, status=406)
            return False

        return True

    def lock_compute(self, ctx, compute, purpose, **kw):
        """
        Lock compute for a purpose.
        :param ctx:
        :param compute:
        :param purpose:
        :param kw:
        :return:
        """
        self.do_lock_compute(ctx, compute=compute, purpose=purpose, **kw)
        if ctx.failed:
            return

        compute.status = md.ComputeStatus.LOCKED
        error = md.save(compute)
        if error:
            e = IOError('Failed to lock compute {} for "{}". Error: {}.'
                        .format(compute.id, purpose, error))
            LOG.error(e)
            ctx.set_error(errors.COMPUTE_LOCK_FAILED, cause=e, status=500)
            return

    def do_lock_compute(self, ctx, compute, purpose, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :param purpose:
        :param kw:
        :return:
        """

    def unlock_compute(self, ctx, compute, purpose, target_status, **kw):
        """
        Unlock compute.
        :param ctx:
        :param compute:
        :param purpose:
        :param target_status:
        :param kw:
        :return:
        """
        self.do_unlock_compute(ctx, compute=compute, purpose=purpose,
                               target_status=target_status, **kw)
        if ctx.failed:
            return

        error = md.save(compute)
        if error:
            e = IOError('Failed to unlock compute {} at "{}". Error: {}.'
                        .format(compute.id, purpose, error))
            LOG.error(e)
            ctx.set_error(errors.COMPUTE_UNLOCK_FAILED, cause=e, status=500)
            return

    def do_unlock_compute(self, ctx, compute, purpose, target_status, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :param purpose:
        :param target_status:
        :param kw:
        :return:
        """

    #######################################################
    # COMPUTE CRUD
    #######################################################

    def get_compute(self, ctx):
        """
        Get compute.
        :param ctx:
        :return:
        """
        compute = self.load_compute(ctx,
                                    check_roles=GET_ROLES,
                                    check_status=None,
                                    check_expired=False)
        if ctx.failed:
            return

        base_mgr.dump_object(ctx, object=compute)
        return compute

    def get_computes(self, ctx):
        """
        Get multiple computes.
        :param ctx:
        :return:
        """
        admin_roles = md.UserRole.admin_roles_of(LIST_ROLES)

        # Admin can get computes of a specific user or all users
        if ctx.check_request_user_role(admin_roles):
            user_id = ctx.data.get('user_id')
            override_condition = {'user_id': user_id} if user_id else None
        else:
            # User can only get his computes
            override_condition = {'user_id': ctx.request_user.id}

        return base_mgr.dump_objects(ctx,
                                     model_class=md.Compute,
                                     override_condition=override_condition,
                                     on_loaded_func=self.on_get_computes)

    def on_get_computes(self, ctx, computes):
        """
        Called when computes loaded in get_computes().
        :param ctx:
        :param computes:
        :return:
        """

    def create_compute(self, ctx):
        """
        Create compute.
        :param ctx:
        :return:
        """
        # Validate input
        self.validate_create_compute(ctx)
        if ctx.failed:
            return

        data = ctx.data
        order = md.load_order(data.get('order') or data['order_id'])
        if not order:
            ctx.set_error(errors.ORDER_NOT_FOUND, status=404)
            return

        user = ctx.target_user = order.user
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        # To prevent race condition, create a lock in DB
        @base_mgr.with_lock(ctx, id='user:{}:create_compute'.format(user.id), timeout=5)
        def _create_compute():
            self.can_create_compute(ctx, order=order)
            if ctx.failed:
                return
            response = ctx.response
            ctx.clear_response()

            # If an old compute is re-created
            recreate_compute = response.get('recreate_compute')
            if recreate_compute:
                data['recreate_compute'] = True
                self.do_recreate_compute(ctx, compute=recreate_compute)
                if ctx.failed:
                    return

                recreate_compute.name = data.get('name') or recreate_compute.name
                recreate_compute.description = data.get('description') or recreate_compute.description
                recreate_compute.status = md.ComputeStatus.LOCKED
                recreate_compute.backend_status = None
                recreate_compute.backend_id = None
                recreate_compute.public_ip = None

                # Init compute info
                self.init_compute_info(ctx, compute=recreate_compute)
                if ctx.failed:
                    return

                self.do_create_compute(ctx, compute=recreate_compute)
                if ctx.failed:
                    return

                # Save Compute in database
                error = md.save(recreate_compute)
                if error:
                    ctx.set_error(error, status=500)
                    return

                self.do_post_create_compute(ctx, compute=recreate_compute)
                if ctx.failed:
                    recreate_compute.status = md.ComputeStatus.FAILED
                    error = md.save(recreate_compute)
                    if error:
                        LOG.error('Failed to save compute {} in DB. Error {}.'
                                  .format(recreate_compute.id, error))
                    return

                ctx.data = {
                    'compute': recreate_compute,
                }
                return self.get_compute(ctx)

            else:  # Create new compute
                # Max computes can create
                available_count = response['available_count']
                used_count = response['used_count']
                ctx.response = None

                create_count = max(data.get('create_count') or 1, 1)
                if create_count > available_count:
                    ctx.set_error(errors.COMPUTE_RESOURCE_EXHAUSTED, status=406)
                    return

                region_id = order.region_id
                order_info = order.data['info']
                compute_info = order_info.get('trial_info') or order_info

                compute_name = data.get('name')
                start_index = used_count + 1
                if not compute_name:
                    compute_name = 'Compute #' + str(start_index) if create_count == 1 else 'Compute'

                all_computes = []
                for i in range(create_count):
                    next_name = compute_name if create_count == 1 else compute_name + ' #' + str(start_index)
                    start_index += 1

                    compute = md.Compute()
                    compute.user_id = user.id
                    compute.order_id = order.id
                    compute.type = md.ComputeType.VM
                    compute.name = next_name
                    compute.description = data.get('description') or None
                    compute.create_date = date_util.utc_now()
                    compute.end_date = order.end_date or None
                    compute.status = md.ComputeStatus.LOCKED
                    compute.region_id = region_id
                    compute.data = {
                        'info': compute_info,
                    }

                    # Init compute config
                    self.init_compute_info(ctx, compute=compute, order=order)
                    if ctx.failed:
                        return

                    self.do_create_compute(ctx, compute=compute)
                    if ctx.failed:
                        return

                    # Save Compute in database
                    error = md.save_new(compute)
                    if error:
                        ctx.set_error(error, status=500)
                        return

                    self.do_post_create_compute(ctx, compute=compute)
                    if ctx.failed:
                        compute.status = md.ComputeStatus.FAILED
                        error = md.save(compute)
                        if error:
                            LOG.error('Failed to save compute {} in DB. Error {}.'
                                      .format(compute.id, error))
                        return

                    all_computes.append(compute)

                # Return details of the newly created computes
                response = []
                for compute_obj in all_computes:
                    ctx.data = {
                        'compute': compute_obj,
                    }
                    self.get_compute(ctx)
                    response.append(ctx.response)

                ctx.response = response = response[0] if len(response) == 1 else response
                return response

        # Create compute
        return _create_compute()

    def init_compute_info(self, ctx, compute, order=None):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :param order:
        :return:
        """
        data = ctx.data

        networks = []
        if data.get('network'):
            networks.append({
                'network': data.get('network'),
                'subnet': data.get('subnet'),
            })

        volumes = []
        # TODO

        compute.data['info'].update({
            'volumes': volumes,
            'networks': networks,
            'ssh_key': data.get('ssh_key'),
        })

        # Compute settings
        settings = compute.data['settings'] = compute.data.get('settings') or {}
        settings['notify_when_created'] = data.get('notify_when_created') or None

        # Mark the data field is modified
        compute.flag_modified('data')

    def validate_create_compute(self, ctx):
        """
        Validate create compute input
        :param ctx:
        :return:
        """
        data = ctx.data
        # Validate compute name
        if 'name' in data and not self.validate_compute_name(ctx, name=data['name']):
            return
        # Validate username
        if 'username' in data and not self.validate_compute_username(ctx, username=data['username']):
            return
        # Validate password
        if 'password' in data and not self.validate_compute_password(ctx, password=data['password']):
            return
        # Validate network
        if 'network' in data and not self.validate_compute_network(ctx, network=data['network']):
            return
        # Validate subnet
        if 'subnet' in data and not self.validate_compute_subnet(ctx, subnet=data['subnet']):
            return
        # Validate ssh_key
        if 'ssh_key' in data and not self.validate_compute_ssh_key(ctx, ssh_key=data['ssh_key']):
            return

        if not data.get('password') and not data.get('ssh_key'):
            e = ValueError('Either password and ssh_key must be set '
                           'when creating compute.')
            LOG.error(e)
            ctx.set_error(errors.COMPUTE_INFO_MISSING, cause=e, status=406)
            return

    def validate_compute_name(self, ctx, name):
        """
        Validate compute input
        :param ctx:
        :param name:
        :return:
        """
        name = name.strip() if name else None
        if not name or len(name) > 32:
            e = ValueError('Compute name exceeds 32 characters length.')
            LOG.error(e)
            ctx.set_error(errors.COMPUTE_NAME_INVALID, cause=e, status=406)
            return
        ctx.data['name'] = name
        return True

    def validate_compute_username(self, ctx, username):
        """
        Validate compute input
        :param ctx:
        :param username:
        :return:
        """
        username = username.strip() if username else None
        user_pattern = '^[a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}\\$)$'
        if not username or not re.match(user_pattern, username):
            e = ValueError('Username "{}" invalid.'.format(username))
            LOG.error(e)
            ctx.set_error(errors.COMPUTE_USERNAME_INVALID, cause=e, status=406)
            return
        ctx.data['username'] = username
        return True

    def validate_compute_password(self, ctx, password):
        """
        Validate compute input
        :param ctx:
        :param password:
        :return:
        """
        password = password.strip() if password else None
        requirement = app.config['COMPUTE_PASSWORD_REQUIREMENT']
        if not password or not str_util.valid_user_password(password, requirement=requirement):
            e = ValueError('Password requirements: ' +
                           str_util.password_requirement_desc(requirement))
            LOG.error(e)
            ctx.set_error(errors.COMPUTE_PASSWORD_REQUIREMENT_NOT_MET, cause=e, status=406)
            return
        ctx.data['password'] = password
        return True

    def validate_compute_network(self, ctx, network):
        """
        Validate compute input
        :param ctx:
        :param network:
        :return:
        """
        # TODO
        return True

    def validate_compute_subnet(self, ctx, subnet):
        """
        Validate compute input
        :param ctx:
        :param subnet:
        :return:
        """
        # TODO
        return True

    def validate_compute_ssh_key(self, ctx, ssh_key):
        """
        Validate compute input
        :param ctx:
        :param ssh_key:
        :return:
        """
        # TODO
        return True

    def can_create_compute(self, ctx, order):
        """
        Create compute.
        :param ctx:
        :param order:
        :return:
        """
        # Order not reach time
        start_date = order.start_date
        if start_date and date_util.utc_now() < start_date:
            ctx.set_error(errors.ORDER_TIME_INVALID, status=403)
            return False

        # Order expired
        end_date = order.end_date
        if end_date and date_util.utc_now() > end_date:
            ctx.set_error(errors.ORDER_EXPIRED, status=403)
            return False

        # Order not finished
        if order.status != md.OrderStatus.COMPLETED:
            ctx.set_error(errors.ORDER_NOT_FINISHED, status=403)
            return False

        # If user want to recreate his compute
        data = ctx.data
        recreate_compute_id = data.get('recreate_compute_id')
        if recreate_compute_id:  # Re-create old compute
            recreate_compute = md.load_compute(recreate_compute_id)

            if not recreate_compute:
                e = ValueError('Compute id {} not found.'.format(recreate_compute_id))
                LOG.error(e)
                ctx.set_error(errors.COMPUTE_NOT_FOUND, cause=e, status=404)
                return

            if recreate_compute.order_id != order.id:
                e = ValueError('User does not have permission to re-create compute {}.'
                               .format(recreate_compute_id))
                LOG.error(e)
                ctx.set_error(errors.USER_ACTION_NOT_ALLOWED, cause=e, status=403)
                return

            if recreate_compute.status == md.ComputeStatus.DISABLED:
                e = ValueError('Unable to re-create compute in Disabled state.')
                LOG.error(e)
                ctx.set_error(errors.COMPUTE_RECREATE_FAILED, cause=e, status=406)
                return

            ctx.response = response = {
                'recreate_compute': recreate_compute,
            }
            return response

        else:  # NEW compute
            info = order.data['info']

            check_keys = ['cpu', 'mem', 'disk', 'os_name']
            for key in check_keys:
                if key not in info:
                    ctx.set_error(errors.COMPUTE_RESOURCE_EXHAUSTED, status=406)
                    return False

            used_count = md.query(md.Compute, order_id=order.id).count()
            max_uses_allowed = order.amount
            if used_count >= max_uses_allowed:
                ctx.set_error(errors.COMPUTE_RESOURCE_EXHAUSTED, status=406)
                return False

            ctx.response = response = {
                'used_count': used_count,
                'available_count': max_uses_allowed - used_count,
            }
            return response

    def do_create_compute(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def do_recreate_compute(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def do_post_create_compute(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_create_compute_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def update_compute(self, ctx):
        """
        Update compute.
        :param ctx:
        :return:
        """
        # Validate input
        self.validate_update_compute(ctx)
        if ctx.failed:
            return

        admin_roles = md.UserRole.admin_roles_of(UPDATE_ROLES)
        is_admin = ctx.check_request_user_role(admin_roles)

        compute = self.load_compute(ctx,
                                    check_roles=UPDATE_ROLES,
                                    check_status=None if is_admin else ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        # Update Compute data
        self.do_update_compute(ctx, compute=compute)
        if ctx.failed:
            return

        error = md.save(compute)
        if error:
            ctx.set_error(error, status=500)
            return

        self.do_post_update_compute(ctx, compute=compute)
        if ctx.failed:
            return

        ctx.data = {
            'compute': compute,
        }
        return self.get_compute(ctx)

    def validate_update_compute(self, ctx):
        """
        Validate update compute input
        :param ctx:
        :return:
        """
        data = ctx.data
        # Validate compute name
        if 'name' in data and not self.validate_compute_name(ctx, name=data['name']):
            return
        # Validate username
        if 'username' in data and not self.validate_compute_username(ctx, username=data['username']):
            return
        # Validate password
        if 'password' in data and not self.validate_compute_password(ctx, password=data['password']):
            return
        # Validate network
        if 'network' in data and not self.validate_compute_network(ctx, network=data['network']):
            return
        # Validate subnet
        if 'subnet' in data and not self.validate_compute_subnet(ctx, subnet=data['subnet']):
            return
        # Validate ssh_key
        if 'ssh_key' in data and not self.validate_compute_ssh_key(ctx, ssh_key=data['ssh_key']):
            return

    def do_update_compute(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def do_post_update_compute(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_update_compute_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def delete_compute(self, ctx):
        """
        Delete compute.
        :param ctx:
        :return:
        """
        admin_roles = md.UserRole.admin_roles_of(UPDATE_ROLES)
        is_admin = ctx.check_request_user_role(admin_roles)

        statuses = list(ENABLED_STATUS) + [md.ComputeStatus.FAILED]
        compute = self.load_compute(ctx,
                                    check_roles=DELETE_ROLES,
                                    check_status=None if is_admin else statuses,
                                    check_expired=True)
        if ctx.failed:
            return

        # Release compute resources first
        self.do_release_compute_resource(ctx, compute=compute)
        if ctx.failed:
            return

        self.do_delete_compute(ctx, compute=compute)
        if ctx.failed:
            return

    def do_release_compute_resource(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def do_delete_compute(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def do_post_delete_compute(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_delete_compute_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    #######################################################
    # COMPUTE STATUS
    #######################################################

    def get_compute_status(self, ctx):
        """
        Get compute status.
        :param ctx:
        :return:
        """
        compute = self.load_compute(ctx,
                                    check_roles=GET_ROLES,
                                    check_status=ENABLED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        return self.do_get_compute_status(ctx, compute=compute)

    def do_get_compute_status(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    #######################################################
    # COMPUTE CONFIG
    #######################################################

    def get_compute_config(self, ctx):
        """
        Get compute config.
        :param ctx:
        :return:
        """
        compute = self.load_compute(ctx,
                                    check_roles=GET_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        return self.do_get_compute_config(ctx, compute=compute)

    def do_get_compute_config(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    #######################################################
    # COMPUTE STATS
    #######################################################

    @property
    def compute_stats_supported(self):
        """
        Check for compute stats support.
        :return:
        """
        return True

    def get_compute_stats(self, ctx):
        """
        Get compute stats.
        :param ctx:
        :return:
        """
        if not self.compute_stats_supported:
            ctx.set_error(errors.COMPUTE_STATS_NOT_SUPPORTED, status=400)
            return

        compute = self.load_compute(ctx,
                                    check_roles=GET_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        return self.do_get_compute_stats(ctx, compute=compute)

    def do_get_compute_stats(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    #######################################################
    # COMPUTE ACTIONS
    #######################################################

    def perform_action(self, ctx):
        """
        Perform action on compute.
        :param ctx:
        :return:
        """
        data = ctx.data
        action = data['action']
        if action not in self.supported_actions:
            ctx.set_error(errors.COMPUTE_ACTION_NOT_SUPPORTED, status=406)
            return

        compute = self.load_compute(ctx,
                                    check_roles=UPDATE_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        return self.do_perform_action(ctx, compute=compute)

    def do_perform_action(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_perform_action_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    #######################################################
    # SNAPSHOTS
    #######################################################

    @property
    def snapshot_supported(self):
        """
        Check for snapshot support.
        :return:
        """
        return True

    def snapshot_supported_on(self, compute):
        """
        Check for snapshot support for compute.
        :param compute:
        :return:
        """
        return compute.data['info'].get('snapshot_supported')

    @property
    def default_snapshot_file_max_allowed(self):
        return DEFAULT_SNAPSHOT_FILE_MAX_ALLOWED

    def snapshot_file_max_allowed(self, compute):
        """
        Get the max snapshots allowed for compute.
        :return:
        :param compute:
        """
        max_val = compute.data['info'].get('snapshot_file_max')
        return max_val if max_val is not None else self.default_snapshot_file_max_allowed

    @property
    def default_snapshot_size_max_allowed(self):
        return DEFAULT_SNAPSHOT_SIZE_MAX_ALLOWED

    def snapshot_size_max_allowed(self, compute):
        """
        Get the max size of snapshots allowed for compute.
        :return:
        :param compute:
        """
        max_val = compute.data['info'].get('snapshot_size_max')
        return max_val if max_val is not None else self.default_snapshot_size_max_allowed

    #######################################################
    # SNAPSHOTS
    #######################################################

    def get_snapshot(self, ctx):
        """
        Get compute snapshot.
        :param ctx:
        :return:
        """
        if not self.snapshot_supported:
            ctx.set_error(errors.COMPUTE_SNAPSHOT_NOT_SUPPORTED, status=400)
            return

        compute = self.load_compute(ctx,
                                    check_roles=GET_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        if not self.snapshot_supported_on(compute):
            ctx.set_error(errors.COMPUTE_SNAPSHOT_NOT_SUPPORTED, status=400)
            return

        return self.do_get_snapshot(ctx, compute=compute)

    def do_get_snapshot(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def get_snapshots(self, ctx):
        """
        Get compute snapshots.
        :param ctx:
        :return:
        """
        if not self.snapshot_supported:
            ctx.set_error(errors.COMPUTE_SNAPSHOT_NOT_SUPPORTED, status=400)
            return

        compute = self.load_compute(ctx,
                                    check_roles=GET_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        if not self.snapshot_supported_on(compute):
            ctx.set_error(errors.COMPUTE_SNAPSHOT_NOT_SUPPORTED, status=400)
            return

        return self.do_get_snapshots(ctx, compute=compute)

    def do_get_snapshots(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def create_snapshot(self, ctx):
        """
        Create compute snapshot.
        :param ctx:
        :return:
        """
        if not self.snapshot_supported:
            ctx.set_error(errors.COMPUTE_SNAPSHOT_NOT_SUPPORTED, status=400)
            return

        compute = self.load_compute(ctx,
                                    check_roles=CREATE_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        if not self.snapshot_supported_on(compute):
            ctx.set_error(errors.COMPUTE_SNAPSHOT_NOT_SUPPORTED, status=400)
            return

        _ctx = ctx.copy(task='get snapshots of compute', data={})
        self.do_get_snapshots(_ctx, compute=compute)
        if _ctx.failed:
            ctx.set_error(errors.COMPUTE_SNAPSHOT_GET_FAILED, status=406)
            return
        snapshots = _ctx.response['data']

        max_snap = self.snapshot_file_max_allowed(compute=compute)
        if max_snap and len(snapshots) >= max_snap:
            e = ValueError('Number of snapshots exceeds the limitation value {} units.'.format(max_snap))
            LOG.error(e)
            ctx.set_error(errors.COMPUTE_SNAPSHOT_EXCEEDED, cause=e, status=406)
            return

        total_size = 0
        for snap in snapshots:
            total_size += snap['size'] if 'size' in snap else 0
        max_size = self.snapshot_size_max_allowed(compute=compute)
        if max_size and total_size >= max_size * base.UNIT_GB:
            e = ValueError('Total size of snapshots exceeds the limitation value {} GB.'.format(max_size))
            LOG.error(e)
            ctx.set_error(errors.COMPUTE_SNAPSHOT_EXCEEDED, cause=e, status=406)
            return

        return self.do_create_snapshot(ctx, compute=compute)

    def do_create_snapshot(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_create_snapshot_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def update_snapshot(self, ctx):
        """
        Update compute snapshot.
        :param ctx:
        :return:
        """
        if not self.snapshot_supported:
            ctx.set_error(errors.COMPUTE_SNAPSHOT_NOT_SUPPORTED, status=400)
            return

        compute = self.load_compute(ctx,
                                    check_roles=UPDATE_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        if not self.snapshot_supported_on(compute):
            ctx.set_error(errors.COMPUTE_SNAPSHOT_NOT_SUPPORTED, status=400)
            return

        return self.do_update_snapshot(ctx, compute=compute)

    def do_update_snapshot(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_update_snapshot_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def rollback_snapshot(self, ctx):
        """
        Rollback to snapshot.
        :param ctx:
        :return:
        """
        if not self.snapshot_supported:
            ctx.set_error(errors.COMPUTE_SNAPSHOT_NOT_SUPPORTED, status=400)
            return

        compute = self.load_compute(ctx,
                                    check_roles=UPDATE_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        if not self.snapshot_supported_on(compute):
            ctx.set_error(errors.COMPUTE_SNAPSHOT_NOT_SUPPORTED, status=400)
            return

        return self.do_rollback_snapshot(ctx, compute=compute)

    def do_rollback_snapshot(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_rollback_snapshot_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def delete_snapshot(self, ctx):
        """
        Delete compute snapshot.
        :param ctx:
        :return:
        """
        if not self.snapshot_supported:
            ctx.set_error(errors.COMPUTE_SNAPSHOT_NOT_SUPPORTED, status=400)
            return

        compute = self.load_compute(ctx,
                                    check_roles=DELETE_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        if not self.snapshot_supported_on(compute):
            ctx.set_error(errors.COMPUTE_SNAPSHOT_NOT_SUPPORTED, status=400)
            return

        return self.do_delete_snapshot(ctx, compute=compute)

    def do_delete_snapshot(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_delete_snapshot_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    #######################################################
    # BACKUP
    #######################################################

    @property
    def backup_supported(self):
        """
        Check for backup support.
        :return:
        """
        return True

    def backup_supported_on(self, compute):
        """
        Check for backup support for compute.
        :return:
        :param compute:
        """
        return compute.data['info'].get('backup_supported')

    @property
    def default_backup_job_max_allowed(self):
        return DEFAULT_BACKUP_JOB_MAX_ALLOWED

    def backup_job_max_allowed(self, compute):
        """
        Get the max backup jobs allowed for compute.
        :return:
        :param compute:
        """
        max_val = compute.data['info'].get('backup_job_max')
        return max_val if max_val is not None else self.default_backup_job_max_allowed

    @property
    def default_backup_file_max_allowed(self):
        return DEFAULT_BACKUP_FILE_MAX_ALLOWED

    def backup_file_max_allowed(self, compute):
        """
        Get the max backup files allowed for compute.
        :return:
        :param compute:
        """
        max_val = compute.data['info'].get('backup_file_max')
        return max_val if max_val is not None else self.default_backup_file_max_allowed

    @property
    def default_backup_size_max_allowed(self):
        return DEFAULT_BACKUP_SIZE_MAX_ALLOWED

    def backup_size_max_allowed(self, compute):
        """
        Get the max backup size allowed for compute.
        :return:
        :param compute:
        """
        max_val = compute.data['info'].get('backup_size_max')
        return max_val if max_val is not None else self.default_backup_size_max_allowed

    #######################################################
    # BACKUP JOB
    #######################################################

    def get_backup_job(self, ctx):
        """
        Do get compute backup.
        :param ctx:
        :return:
        """
        if not self.backup_supported:
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        compute = self.load_compute(ctx,
                                    check_roles=GET_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        if not self.backup_supported_on(compute):
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        return self.do_get_backup_job(ctx, compute=compute)

    def do_get_backup_job(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def get_backup_jobs(self, ctx):
        """
        Get compute backups.
        :param ctx:
        :return:
        """
        if not self.backup_supported:
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        compute = self.load_compute(ctx,
                                    check_roles=GET_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        if not self.backup_supported_on(compute):
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        return self.do_get_backup_jobs(ctx, compute=compute)

    def do_get_backup_jobs(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def create_backup_job(self, ctx):
        """
        Do create new compute backup.
        :param ctx:
        :return:
        """
        if not self.backup_supported:
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        compute = self.load_compute(ctx,
                                    check_roles=CREATE_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        if not self.backup_supported_on(compute):
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        max_job = self.backup_job_max_allowed(compute=compute)
        if max_job:
            _ctx = ctx.copy(task='get backup jobs of compute', data={})
            self.do_get_backup_jobs(_ctx, compute=compute)
            if _ctx.succeed and len(_ctx.response['data']) >= max_job:
                ctx.set_error(errors.COMPUTE_BACKUP_EXCEEDED, status=406)
                return

        _ctx = ctx.copy(task='get backup files of compute', data={})
        self.do_get_backup_files(_ctx, compute=compute)
        if _ctx.failed:
            ctx.set_error(errors.COMPUTE_BACKUP_FILE_GET_FAILED, status=406)
            return
        bak_files = _ctx.response['data']

        max_file = self.backup_file_max_allowed(compute=compute)
        if max_file and len(bak_files) >= max_file:
            e = ValueError('Number of backup files exceeds the limitation value {} files.'.format(max_file))
            LOG.error(e)
            ctx.set_error(errors.COMPUTE_BACKUP_FILE_EXCEEDED, cause=e, status=406)
            return

        total_size = 0
        for bak in bak_files:
            total_size += bak['size']
        max_size = self.backup_size_max_allowed(compute=compute)
        if max_size and total_size >= max_size * base.UNIT_GB:
            e = ValueError('Total size of backup files exceeds the limitation value {} GB.'.format(max_size))
            LOG.error(e)
            ctx.set_error(errors.COMPUTE_BACKUP_FILE_EXCEEDED, cause=e, status=406)
            return

        return self.do_create_backup_job(ctx, compute=compute)

    def do_create_backup_job(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_create_backup_job_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def update_backup_job(self, ctx):
        """
        Do update a compute backup.
        :param ctx:
        :return:
        """
        if not self.backup_supported:
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        compute = self.load_compute(ctx,
                                    check_roles=UPDATE_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        if not self.backup_supported_on(compute):
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        return self.do_update_backup(ctx, compute=compute)

    def do_update_backup(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_update_backup_job_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def delete_backup_job(self, ctx):
        """
        Do delete a compute backup.
        :param ctx:
        :return:
        """
        if not self.backup_supported:
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        compute = self.load_compute(ctx,
                                    check_roles=DELETE_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        if not self.backup_supported_on(compute):
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        return self.do_delete_backup_job(ctx, compute=compute)

    def do_delete_backup_job(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_delete_backup_job_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    #######################################################
    # BACKUP FILES
    #######################################################

    def get_backup_file(self, ctx):
        """
        Do get compute backup file.
        :param ctx:
        :return:
        """
        if not self.backup_supported:
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        compute = self.load_compute(ctx,
                                    check_roles=GET_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        if not self.backup_supported_on(compute):
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        return self.do_get_backup_file(ctx, compute=compute)

    def do_get_backup_file(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def get_backup_files(self, ctx):
        """
        Get compute backup files.
        :param ctx:
        :return:
        """
        if not self.backup_supported:
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        compute = self.load_compute(ctx,
                                    check_roles=GET_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        if not self.backup_supported_on(compute):
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        return self.do_get_backup_files(ctx, compute=compute)

    def do_get_backup_files(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def create_backup_file(self, ctx):
        """
        Create a compute backup file.
        :param ctx:
        :return:
        """
        if not self.backup_supported:
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        compute = self.load_compute(ctx,
                                    check_roles=CREATE_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        if not self.backup_supported_on(compute):
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        _ctx = ctx.copy(task='get backup files of compute', data={})
        self.do_get_backup_files(_ctx, compute=compute)
        if _ctx.failed:
            ctx.set_error(errors.COMPUTE_BACKUP_FILE_GET_FAILED, status=406)
            return
        volumes = _ctx.response['data']
        num_of_bk_files = sum(len(vol['backups']) for vol in volumes)
        max_file = self.backup_file_max_allowed(compute=compute)
        if max_file and num_of_bk_files >= max_file:
            e = ValueError('Number of backup files exceeds the limitation value {} files.'.format(max_file))
            LOG.error(e)
            ctx.set_error(errors.COMPUTE_BACKUP_FILE_EXCEEDED, cause=e, status=406)
            return

        total_size = sum(sum(list(bak['size']for bak in vol['backups'])) for vol in volumes)
        max_size = self.backup_size_max_allowed(compute=compute)
        if max_size and total_size >= max_size * base.UNIT_GB:
            e = ValueError('Total size of backup files exceeds the limitation value {} GB.'.format(max_size))
            LOG.error(e)
            ctx.set_error(errors.COMPUTE_BACKUP_FILE_EXCEEDED, cause=e, status=406)
            return

        return self.do_create_backup_file(ctx, compute=compute)

    def do_create_backup_file(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_create_backup_file_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def update_backup_file(self, ctx):
        """
        Create a compute backup file.
        :param ctx:
        :return:
        """
        if not self.backup_supported:
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        compute = self.load_compute(ctx,
                                    check_roles=UPDATE_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        if not self.backup_supported_on(compute):
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        _ctx = ctx.copy(task='get backup files of compute', data={})
        self.do_get_backup_files(_ctx, compute=compute)
        if _ctx.failed:
            ctx.set_error(errors.COMPUTE_BACKUP_FILE_GET_FAILED, status=406)
            return
        bak_files = _ctx.response['data']

        max_file = self.backup_file_max_allowed(compute=compute)
        if max_file and len(bak_files) >= max_file:
            e = ValueError('Number of backup files exceeds the limitation value {} files.'.format(max_file))
            LOG.error(e)
            ctx.set_error(errors.COMPUTE_BACKUP_FILE_EXCEEDED, cause=e, status=406)
            return

        total_size = 0
        for bak in bak_files:
            total_size += bak['size']
        max_size = self.backup_size_max_allowed(compute=compute)
        if max_size and total_size >= max_size * base.UNIT_GB:
            e = ValueError('Total size of backup files exceeds the limitation value {} GB.'.format(max_size))
            LOG.error(e)
            ctx.set_error(errors.COMPUTE_BACKUP_FILE_EXCEEDED, cause=e, status=406)
            return

        return self.do_create_backup_file(ctx, compute=compute)

    def do_update_backup_file(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_update_backup_file_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def delete_backup_file(self, ctx):
        """
        Delete a compute backup file.
        :param ctx:
        :return:
        """
        if not self.backup_supported:
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        compute = self.load_compute(ctx,
                                    check_roles=DELETE_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        if not self.backup_supported_on(compute):
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        return self.do_delete_backup_file(ctx, compute=compute)

    def do_delete_backup_file(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_delete_backup_file_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def rollback_backup_file(self, ctx):
        """
        Rollback a compute backup file.
        :param ctx:
        :return:
        """
        if not self.backup_supported:
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        compute = self.load_compute(ctx,
                                    check_roles=UPDATE_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        if not self.backup_supported_on(compute):
            ctx.set_error(errors.COMPUTE_BACKUP_NOT_SUPPORTED, status=400)
            return

        return self.do_rollback_backup_file(ctx, compute=compute)

    def do_rollback_backup_file(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_rollback_backup_file_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    #######################################################
    # SEC GROUPS
    #######################################################

    def get_secgroup(self, ctx):
        """
        Do get compute secgroup.
        :param ctx:
        :return:
        """
        compute = self.load_compute(ctx,
                                    check_roles=GET_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        return self.do_get_secgroup(ctx, compute=compute)

    def do_get_secgroup(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def get_secgroups(self, ctx):
        """
        Get compute secgroups.
        :param ctx:
        :return:
        """
        compute = self.load_compute(ctx,
                                    check_roles=GET_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        return self.do_get_secgroups(ctx, compute=compute)

    def do_get_secgroups(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def create_secgroup(self, ctx):
        """
        Do create new compute secgroup.
        :param ctx:
        :return:
        """
        compute = self.load_compute(ctx,
                                    check_roles=CREATE_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        return self.do_create_secgroup(ctx, compute=compute)

    def do_create_secgroup(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_create_secgroup_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def update_secgroup(self, ctx):
        """
        Do update a compute secgroup.
        :param ctx:
        :return:
        """
        compute = self.load_compute(ctx,
                                    check_roles=UPDATE_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        return self.do_update_secgroup(ctx, compute=compute)

    def do_update_secgroup(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_update_secgroup_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def delete_secgroup(self, ctx):
        """
        Do delete a compute secgroup.
        :param ctx:
        :return:
        """
        compute = self.load_compute(ctx,
                                    check_roles=DELETE_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        return self.do_delete_secgroup(ctx, compute=compute)

    def do_delete_secgroup(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_delete_secgroup_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    #######################################################
    # SEC GROUP RULES
    #######################################################

    def get_secgroup_rule(self, ctx):
        """
        Do get compute secgroup rule.
        :param ctx:
        :return:
        """
        compute = self.load_compute(ctx,
                                    check_roles=GET_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        return self.do_get_secgroup_rule(ctx, compute=compute)

    def do_get_secgroup_rule(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def get_secgroup_rules(self, ctx):
        """
        Get compute secgroup rules.
        :param ctx:
        :return:
        """
        compute = self.load_compute(ctx,
                                    check_roles=GET_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        return self.do_get_secgroup_rules(ctx, compute=compute)

    def do_get_secgroup_rules(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def create_secgroup_rule(self, ctx):
        """
        Do create new compute secgroup rule.
        :param ctx:
        :return:
        """
        compute = self.load_compute(ctx,
                                    check_roles=CREATE_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        return self.do_create_secgroup_rule(ctx, compute=compute)

    def do_create_secgroup_rule(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_create_secgroup_rule_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def update_secgroup_rule(self, ctx):
        """
        Do update a compute secgroup rule.
        :param ctx:
        :return:
        """
        compute = self.load_compute(ctx,
                                    check_roles=UPDATE_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        return self.do_update_secgroup_rule(ctx, compute=compute)

    def do_update_secgroup_rule(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_update_secgroup_rule_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def delete_secgroup_rule(self, ctx):
        """
        Do delete a compute secgroup rule.
        :param ctx:
        :return:
        """
        compute = self.load_compute(ctx,
                                    check_roles=DELETE_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        return self.do_delete_secgroup_rule(ctx, compute=compute)

    def do_delete_secgroup_rule(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def on_delete_secgroup_rule_result(self, ctx, compute, **kw):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    #######################################################
    # PRODUCT PRICING
    #######################################################

    def do_get_price(self, ctx, product):
        """
        Subclass should override this method.
        :param ctx:
        :param product:
        :return:
        """
        parsed_info = self.validate_get_price(ctx, product=product)
        if ctx.failed:
            return

        pricing = product.pricing
        product_info = product.info
        hw_custom = product.name == 'custom'

        currency = parsed_info['currency']
        amount = parsed_info['amount']
        duration = parsed_info['duration']
        duration_str = '{} {}'.format(duration['value'], duration['unit'])

        if not hw_custom:  # Fixed Hardware
            months = duration['value']
            pricing = self.get_product_pricing(product=product, months=months)

            ctx.response = data_util.no_null_kv_dict({
                'id': product.id,
                'info': data_util.no_null_kv_dict({
                    'cpu': product_info['cpu'],
                    'mem': product_info['mem'],
                    'disk': product_info['disk'],
                    'disk_type': product_info.get('disk_type'),
                    'net_bandwidth': product_info.get('net_bandwidth'),
                    'snapshot_supported': product_info.get('snapshot_supported'),
                    'snapshot_size_max': product_info.get('snapshot_size_max'),
                    'backup_supported': product_info.get('backup_supported'),
                    'backup_size_max': product_info.get('backup_size_max'),
                }),
                'price': pricing['price'] * amount,
                'price_monthly': pricing['price_monthly'],
                'currency': currency,
                'amount': amount,
                'duration': duration_str,
                'promotion': pricing.get('promotion', False),
                'promotion_type': pricing.get('promotion_type'),
            })

        else:  # Custom Hardware

            def _get_field_price(name, value, pricing_info):
                # Pricing based on unit price
                if 'unit' in pricing_info:
                    return value * pricing_info['unit']
                # Pricing based on predefined prices
                if isinstance(value, list):
                    key = ','.join([str(x) for x in value])
                else:
                    key = str(value)
                return pricing_info[key]

            pricing = pricing['price']
            custom_data = ctx.data['data']

            # CPU price
            cpu_price = 0
            cpu = custom_data.get('cpu') or None
            if cpu:
                cpu_price = _get_field_price('CPU', cpu, pricing['cpu'])

            # Mem price
            mem_price = 0
            mem = custom_data.get('mem') or None
            if mem:
                mem_price = _get_field_price('Memory', mem, pricing['mem'])

            # Disk price
            disk_price = 0
            disk = custom_data.get('disk')
            if disk:
                disk_price = _get_field_price('Disk', disk, pricing['disk'])

            # Net bandwidth price
            net_bandwidth_price = 0
            net_bandwidth = custom_data.get('net_bandwidth') or None
            if net_bandwidth:
                net_bandwidth_price = _get_field_price('Network Bandwidth', net_bandwidth, pricing['net_bandwidth'])

            # Snapshot price
            snapshot_price = 0
            snapshot_size = custom_data.get('snapshot_size_max') or None
            if snapshot_size:
                snapshot_price = _get_field_price('Snapshot size', snapshot_size, pricing['snapshot'])

            # Backup price
            backup_price = 0
            backup_size = custom_data.get('backup_size_max') or None
            if backup_size:
                backup_price = _get_field_price('Backup size', backup_size, pricing['backup'])

            price_monthly = (cpu_price + mem_price + disk_price +
                             net_bandwidth_price + snapshot_price + backup_price)
            price_total = price_monthly * duration['value'] * amount
            ctx.response = data_util.no_null_kv_dict({
                'id': product.id,
                'info': data_util.no_null_kv_dict({
                    'cpu': cpu,
                    'mem': mem,
                    'disk': disk,
                    'disk_type': custom_data.get('disk_type'),
                    'net_bandwidth': net_bandwidth,
                    'snapshot_supported': True if snapshot_size else False,
                    'snapshot_size_max': snapshot_size,
                    'backup_supported': True if backup_size else False,
                    'backup_size_max': backup_size,
                }),
                'price': price_total,
                'price_monthly': price_monthly,
                'currency': currency,
                'amount': amount,
                'duration': duration_str,
                'promotion': False,
            })
        return ctx.response

    def validate_get_price(self, ctx, product):
        """
        Override super class method.
        :param ctx:
        :param product:
        :return:
        """
        parsed_info = super().validate_get_price(ctx, product=product)
        if ctx.failed:
            return

        data = ctx.data
        hw_custom = product.name == 'custom'
        product_info = product.info
        if hw_custom:
            custom_data = data['data']

            # Validate CPU
            cpu = custom_data.get('cpu')
            if cpu:
                if not self._validate_field(ctx, 'CPU (vCPU)', cpu, product_info['cpu']):
                    return

            # Validate Mem
            mem = custom_data.get('mem')
            if mem:
                if not self._validate_field(ctx, 'Memory (GB)', mem, product_info['mem']):
                    return

            # Validate Disk
            disk = custom_data.get('disk')
            if disk:
                if not self._validate_field(ctx, 'Disk (GB)', disk, product_info['disk']):
                    return

            # Validate Disk IOPS
            # TODO

            # Validate Net IP
            # TODO

            # Validate Net Bandwidth
            net_bw = custom_data.get('net_bandwidth')
            if net_bw:
                if not self._validate_field(ctx, 'Network bandwidth (Mbps)', net_bw, product_info['net_bandwidth']):
                    return

            # Validate Snapshot size
            snapshot_size = custom_data.get('snapshot_size_max')
            if snapshot_size:
                if not self._validate_field(ctx, 'Snapshot size (GB)', snapshot_size, product_info['snapshot']):
                    return

            # Validate Backup size
            backup_size = custom_data.get('backup_size_max')
            if backup_size:
                if not self._validate_field(ctx, 'Backup size (GB)', backup_size, product_info['backup']):
                    return

        return parsed_info

    def do_apply_promotion(self, ctx, promotion):
        """
        Override super class method.
        :param ctx:
        :param promotion:
        :return:
        """
        self.validate_promotion(ctx, promotion=promotion)
        if ctx.failed:
            return

        data = ctx.data
        pricing = data['pricing']
        compute_settings = (promotion.product_settings or {}).get('compute') or {}
        promo_settings = promotion.settings

        # TRIAL mode
        if promotion.type == md.PromotionType.TRIAL:
            pricing['promotion_type'] = md.PromotionType.TRIAL

            pricing['price_deal'] = 0
            if 'amount' in promo_settings:
                pricing['amount'] = promo_settings['amount']
            if 'duration' in promo_settings:
                pricing['duration'] = promo_settings['duration']

            info = pricing['info']
            trial_info = info['trial_info'] = dict(info)

            # CPU
            if 'max_cpu' in compute_settings:
                trial_info['cpu'] = min(trial_info.get('cpu') or 1, compute_settings['max_cpu'])
            # Mem
            if 'max_mem' in compute_settings:
                trial_info['mem'] = min(trial_info.get('mem') or 1, compute_settings['max_mem'])
            # Disk
            if 'max_disk' in compute_settings:
                trial_info['disk'] = min(trial_info.get('disk') or 20, compute_settings['max_disk'])

            # Disk read/write IOPS

            # Network IP

            # Network Bandwidth
            net_bandwidth = compute_settings.get('max_net_bandwidth')
            if net_bandwidth is not None:
                if 'net_bandwidth' in trial_info:
                    trial_info['net_bandwidth'] = min(trial_info['net_bandwidth'], net_bandwidth)
                else:
                    trial_info['net_bandwidth'] = net_bandwidth

            # Snapshot
            if 'snapshot_supported' in compute_settings:
                trial_info['snapshot_supported'] = compute_settings['snapshot_supported']
            snap_size = compute_settings.get('max_snapshot_size')
            if snap_size is not None:
                if 'snapshot_size_max' in trial_info:
                    trial_info['snapshot_size_max'] = min(trial_info['snapshot_size_max'] or 0, snap_size)
                else:
                    trial_info['snapshot_size_max'] = snap_size

            # Backup
            if 'backup_supported' in compute_settings:
                trial_info['backup_supported'] = compute_settings['backup_supported']
            backup_size = compute_settings.get('max_backup_size')
            if backup_size is not None:
                if 'backup_size_max' in trial_info:
                    trial_info['backup_size_max'] = min(trial_info['backup_size_max'] or 0, backup_size)
                else:
                    trial_info['backup_size_max'] = backup_size

        # DISCOUNT mode
        if promotion.type == md.PromotionType.DISCOUNT:
            pricing['promotion_type'] = md.PromotionType.DISCOUNT
            pricing['discount_code'] = data.get('discount_code')

            discount_rate = promo_settings['discount_rate']
            pricing['price_deal'] = int(pricing['price'] * (1.0 - discount_rate))
            if pricing.get('price_monthly') is not None:
                pricing['price_monthly'] = int(pricing['price_monthly'] * (1.0 - discount_rate))

        ctx.response = pricing
        return pricing

    def validate_promotion(self, ctx, promotion):
        """
        Override super class method.
        :param ctx:
        :param promotion:
        :return:
        """
        parsed_info = super().validate_promotion(ctx, promotion=promotion)
        if ctx.failed:
            return

        data = ctx.data
        product = data['product']
        if product.name == 'custom':
            info = data.get('data')
        else:
            info = product.info

        product_settings = promotion.product_settings
        compute_settings = product_settings.get('compute') if product_settings else None
        if compute_settings:
            cpu = info['cpu']
            min_cpu = compute_settings.get('min_cpu')
            max_cpu = compute_settings.get('max_cpu')
            mem = info['mem']
            min_mem = compute_settings.get('min_mem')
            max_mem = compute_settings.get('max_mem')
            disk = info['disk']
            min_disk = compute_settings.get('min_disk')
            max_disk = compute_settings.get('max_disk')

            snapshot_size = info.get('snapshot_size_max')
            min_snapshot_size = compute_settings.get('min_snapshot_size')
            max_snapshot_size = compute_settings.get('max_snapshot_size')
            backup_size = info.get('backup_size_max')
            min_backup_size = compute_settings.get('min_backup_size')
            max_backup_size = compute_settings.get('max_backup_size')
            if (
                (min_cpu is not None and cpu < min_cpu) or
                (max_cpu is not None and cpu > max_cpu) or
                (min_mem is not None and mem < min_mem) or
                (max_mem is not None and mem > max_mem) or
                (min_disk is not None and disk < min_disk) or
                (max_disk is not None and disk > max_disk) or
                (snapshot_size is not None and min_snapshot_size is not None and snapshot_size < min_snapshot_size) or
                (snapshot_size is not None and max_snapshot_size is not None and snapshot_size > max_snapshot_size) or
                (backup_size is not None and min_backup_size is not None and backup_size < min_backup_size) or
                (backup_size is not None and max_backup_size is not None and backup_size > max_backup_size)
            ):
                e = ValueError('Compute resources CPU={}/Mem={}Gb/Disk={}Gb/'
                               'SnapshotSize={}Gb/BackupSize={}Gb '
                               'exceed promotion limit.'
                               .format(cpu, mem, disk,
                                       snapshot_size, backup_size))
                LOG.debug(e)
                if compute_settings.get('warning_only'):
                    ctx.set_warning(errors.PROMOTION_RESOURCE_LIMIT, cause=e)
                else:
                    ctx.set_error(errors.PROMOTION_RESOURCE_LIMIT, cause=e, status=406)
                    return

        promo_settings = promotion.settings or {}

        # Validate discount code
        user_code = data.get('discount_code') or None
        server_code = promo_settings.get('discount_code') or None
        if user_code != server_code:
            e = ValueError('Order discount code {} is invalid.'.format(user_code))
            LOG.debug(e)
            ctx.set_error(errors.PROMOTION_CONDITION_NOT_MET, cause=e, status=406)
            return

        # Amount must be in range to be accepted for promotion
        amount = data['amount']
        amount_settings = promo_settings.get('amount')
        if isinstance(amount_settings, dict):
            min_amount = amount_settings.get('min')
            max_amount = amount_settings.get('max')
            if ((min_amount is not None and amount < min_amount) or
                (max_amount is not None and 0 < max_amount < amount)
            ):
                e = ValueError('Order amount {} is out of conditional range ({},{}).'
                               .format(amount, min_amount or 1, max_amount or 'N/A'))
                LOG.debug(e)
                ctx.set_error(errors.PROMOTION_CONDITION_NOT_MET, cause=e, status=406)
                return

            values = amount_settings.get('values')
            if values and amount not in values:
                e = ValueError('Order amount {} is out of conditional values.'
                               .format(amount))
                LOG.debug(e)
                ctx.set_error(errors.PROMOTION_CONDITION_NOT_MET, cause=e, status=406)
                return

        # Duration must be in range to be accepted for promotion
        duration = data['duration']
        dur_value, dur_unit = date_util.parse_duration(duration, target_unit='month')

        duration_settings = promo_settings.get('duration')
        if isinstance(duration_settings, dict):
            min_duration = duration_settings.get('min')
            max_duration = duration_settings.get('max')
            if ((min_duration is not None and dur_value < min_duration) or
                (max_duration is not None and 0 < max_duration < dur_value)
            ):
                e = ValueError('Order duration {} is out of conditional range ({},{}).'
                               .format(dur_value, min_duration or 1, max_duration or 'N/A'))
                LOG.debug(e)
                ctx.set_error(errors.PROMOTION_CONDITION_NOT_MET, cause=e, status=406)
                return

            values = duration_settings.get('values')
            if values and dur_value not in values:
                e = ValueError('Order duration {} is out of conditional values.'
                               .format(dur_value))
                LOG.debug(e)
                ctx.set_error(errors.PROMOTION_CONDITION_NOT_MET, cause=e, status=406)
                return

        # Currency must be in range to be accepted for promotion
        currency = data['currency']
        currency_settings = promo_settings.get('currency')
        if isinstance(currency_settings, (list, tuple)):
            if currency_settings and currency not in currency_settings:
                e = ValueError('Order currency {} is out of conditional values.'
                               .format(dur_value))
                LOG.debug(e)
                ctx.set_error(errors.PROMOTION_CONDITION_NOT_MET, cause=e, status=406)
                return

        return parsed_info

    def _validate_field(self, ctx, name, value, info):
        """
        Validate a field value for acceptance.
        :param name:
        :param value:
        :param info:
        :return:
        """
        values = info['values']
        if isinstance(values, dict):
            min_val = values.get('min') or 0
            max_val = values.get('max')
            if value < min_val or (max_val and value > max_val):
                e = ValueError('Value of {} {} is out of range ({},{}).'
                               .format(name, value, min_val, max_val or 'N/A'))
                LOG.debug(e)
                ctx.set_error(errors.ORDER_VALIDATION_FAILED, cause=e, status=406)
                return
        if isinstance(values, list):
            if value not in values:
                e = ValueError('Value of {} {} is not in list {}.'
                               .format(name, value, values))
                LOG.debug(e)
                ctx.set_error(errors.ORDER_VALIDATION_FAILED, cause=e, status=406)
                return
        return True

    def get_order_utilization(self, ctx, order):
        """
        Get utilization info of the referenced order item.
        :param ctx:
        :param order:
        :return:
        """
        data = ctx.data
        order = order or md.load_order(data.get('order') or data.get('order_id'))
        if order:
            used_count = md.query(md.Compute, order_id=order.id).count()
            total_count = order.amount
            ctx.response = {
                'used_count': used_count,
                'available_count': max(total_count - used_count, 0),
                'total_count': total_count,
            }
            return ctx.response

        ctx.set_error(errors.ORDER_NOT_FOUND, status=404)
        return

    def on_order_changed(self, ctx, order):
        """
        Called when an order has changed.
        :param ctx:
        :param order:
        :return:
        """
        data = ctx.data

        for compute in md.iterate(md.Compute, order_id=order.id):
            pass

    def run_bg_task_daily(self, ctx=None):
        """
        Background task scans daily (normally at 2AM-5AM).
        :param ctx:
        :return:
        """
        ctx = ctx or create_admin_context(task='compute background task daily')

        # To prevent race condition, acquire a lock in DB
        @base_mgr.with_lock(ctx, id='run_bg_task_daily', timeout=10000)
        def _exec():
            return self.do_run_bg_task_daily(ctx)

        # Execute the function
        return _exec()

    def do_run_bg_task_daily(self, ctx):
        """
        Subclass should override this method.
        :param ctx:
        :return:
        """

    def run_bg_task_weekly(self, ctx=None):
        """
        Background task scans weekly (normally at 2AM-5AM).
        :return:
        """
        ctx = ctx or create_admin_context(task='compute background task weekly')

        # To prevent race condition, acquire a lock in DB
        @base_mgr.with_lock(ctx, id='run_bg_task_weekly', timeout=10000)
        def _exec():
            return self.do_run_bg_task_weekly(ctx)

        # Execute the function
        return _exec()

    def do_run_bg_task_weekly(self, ctx):
        """
        Subclass should override this method.
        :param ctx:
        :return:
        """

    def run_bg_task(self, ctx):
        """
        Run background task.
        :return:
        """
        label = ctx.data.get('label') or 'daily'
        if label == 'daily':
            self.run_bg_task_daily(ctx)
        elif label == 'weekly':
            self.run_bg_task_weekly(ctx)
        else:
            e = ValueError('Task label "{}" not found.'.format(label))
            LOG.error(e)
            ctx.set_error(errors.COMPUTE_TASK_NOT_FOUND, cause=e, status=404)
            return

    def sync_compute(self, ctx):
        """
        Synchronize compute info with backend.
        :param ctx:
        :return:
        """
        compute = self.load_compute(ctx,
                                    check_roles=UPDATE_ROLES,
                                    check_status=ENABLED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        data = ctx.data
        source = data.get('source') or 'all'

        if source in ('all', 'infra', 'backend'):
            self.do_sync_compute_with_backend(ctx, compute=compute)
            if ctx.failed:
                return

        if source in ('all', 'order'):
            self.do_sync_compute_with_order(ctx, compute=compute)
            if ctx.failed:
                return

        ctx.data = {
            'compute': compute,
        }
        return self.get_compute(ctx)

    def do_sync_compute_with_backend(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def do_sync_compute_with_order(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """

    def manage_compute(self, ctx):
        """
        Manage compute.
        :param ctx:
        :return:
        """
        compute = self.load_compute(ctx,
                                    check_roles=UPDATE_ROLES,
                                    check_status=ENABLED_UNLOCKED_STATUS,
                                    check_expired=True)
        if ctx.failed:
            return

        return self.do_manage_compute(ctx, compute=compute)

    def do_manage_compute(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """
        data = ctx.data
        action = data['action']

        if action == 'send_mail_compute_info':
            return self.do_manage_compute_send_mail_compute_info(ctx, compute=compute)

        # Error
        ctx.set_error(errors.COMPUTE_MGMT_ACTION_INVALID, status=406)

    def do_manage_compute_send_mail_compute_info(self, ctx, compute):
        """
        Subclass should override this method.
        :param ctx:
        :param compute:
        :return:
        """
        if compute.status not in ENABLED_UNLOCKED_STATUS:
            e = ValueError('Compute status "{}" is not accepted for the action.'.format(compute.status))
            LOG.error(e)
            ctx.set_error(errors.COMPUTE_NOT_AVAILABLE, cause=e, status=406)
            return

        if not compute.public_ip or not compute.backend_id:
            e = ValueError('Compute has no public IP and Infra ID.')
            LOG.error(e)
            ctx.set_error(errors.COMPUTE_NOT_AVAILABLE, cause=e, status=406)
            return

        mail_util.send_mail_compute_info(user=compute.user, compute=compute,
                                         ssh_port=self.compute_config.get('compute_ssh_port') or 22)
