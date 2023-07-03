#
# Copyright (c) 2020 FTI-CAS
#

from concurrent import futures

from application import app, thread_executor, process_executor
from application.base import errors
from application.managers import base as base_mgr, user_mgr
from application import models as md
from application.product_types import base
from application.product_types.openstack import os_api
from application.utils import data_util, date_util, mail_util, str_util

LOG = app.logger

ADMIN_ROLES = (md.UserRole.ADMIN, md.UserRole.ADMIN_SALE, md.UserRole.ADMIN_IT)
GET_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
LIST_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
CREATE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)
UPDATE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)
DELETE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)


class OSBase(base.ProductType):
    """
    Openstack base product type.
    """

    _backend_config = None

    def __init__(self):
        # Load backend config
        if not self._backend_config:
            self.init_backend_config()

    def init_backend_config(self):
        backend_config = md.query(md.Configuration,
                                  type=md.ConfigurationType.BACKEND,
                                  name='os_config',
                                  status=md.ConfigurationStatus.ENABLED,
                                  order_by=md.Configuration.version.desc()).first()
        if not backend_config:
            raise ValueError('Config BACKEND/os_config not found in database.')
        self._backend_config = backend_config.contents
        os_api.init_clusters(self._backend_config)

    @property
    def backend_config(self):
        return self._backend_config

    def os_base(self):
        return self

    def get_cluster(self, ctx):
        """
        Get cluster.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=GET_ROLES):
            return

        return self.do_get_cluster(ctx)

    def do_get_cluster(self, ctx):
        """
        Subclass should override this method.
        :param ctx:
        :return:
        """
        return self.get_os_cluster(ctx, cluster=ctx.data['cluster'])

    def get_clusters(self, ctx):
        """
        Get multiple clusters.
        :param ctx:
        :return:
        """
        admin_roles = md.UserRole.admin_roles_of(LIST_ROLES)
        if not user_mgr.check_user(ctx, roles=admin_roles):
            return False

        return self.do_get_clusters(ctx)

    def do_get_clusters(self, ctx):
        """
        Subclass should override this method.
        :param ctx:
        :return:
        """
        clusters = []
        for cl in self.backend_config['clusters']:
            clusters.append({
                'cluster': cl['cluster'],
                'enabled': cl.get('enabled'),
                'region_id': cl.get('region_id'),
            })

        ctx.response = response = {
            'data': clusters,
            'has_more': False,
        }
        return response

    def create_cluster(self, ctx):
        """
        Create cluster.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        return self.do_create_cluster(ctx)

    def do_create_cluster(self, ctx):
        """

        :param ctx:
        :return:
        """
        ctx.set_error('Not Implemented Yet', status=500)

    def update_cluster(self, ctx):
        """
        Update cluster.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
            return

        return self.do_update_cluster(ctx)

    def do_update_cluster(self, ctx):
        """
        Update cluster.
        :param ctx:
        :return:
        """
        ctx.set_error('Not Implemented Yet', status=500)

    def delete_cluster(self, ctx):
        """
        Delete cluster.
        :param ctx:
        :return:
        """
        if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
            return

        return self.do_delete_cluster(ctx)

    def do_delete_cluster(self, ctx):
        """
        Delete cluster.
        :param ctx:
        :return:
        """
        ctx.set_error('Not Implemented Yet', status=500)

    def parse_ctx_cluster(self, ctx):
        """
        Parse cluster info.
        :param ctx:
        :return:
        """
        data = ctx.data
        region_id = data['region_id']
        region_zone = data.get('region_zone') or '1'
        return region_id + '_' + region_zone

    def parse_ctx_listing(self, ctx):
        """
        Parse listing info.
        :param ctx:
        :return:
        """
        data = ctx.data
        page = int(data.get('page') or 1)
        page_size = int(data.get('page_size') or 1000)
        sort_by = data.get('sort_by')
        fields = data.get('fields') or None
        extra_fields = data.get('extra_fields') or None

        sort_bys = []
        if isinstance(sort_by, str):
            sort_by = sort_by.split(',')
            for item in sort_by:
                item = item.split('__')
                attr = item[0]
                direction = item[1] if len(item) == 2 else 'asc'
                sort_bys.append((attr, direction))

        return {
            'page': page,
            'page_size': page_size,
            'sort_by': sort_bys or None,
            'fields': fields,
            'extra_fields': extra_fields,
        }

    def get_os_cluster(self, ctx, cluster=None):
        """
        Find cluster
        :param ctx:
        :param cluster:
        :return
        """
        cluster = cluster or self.parse_ctx_cluster(ctx)
        if ctx.failed:
            return

        result = None
        for cl in self.backend_config['clusters']:
            if cl['cluster'] == cluster:
                ctx.response = result = cl
                break
        if not result:
            ctx.set_error(errors.BACKEND_CLUSTER_NOT_FOUND, status=404)
            return
        return result

    def get_os_config(self, ctx, cluster=None):
        """
        Get openstack client
        :param ctx:
        :param cluster:
        :return
        """
        cluster = cluster or self.parse_ctx_cluster(ctx)
        if ctx.failed:
            return
        cluster_dict = self.get_os_cluster(ctx, cluster=cluster)
        if ctx.failed:
            return
        cluster_os_info = cluster_dict['os_info']

        os_user_info = self.get_os_user(ctx, user=ctx.target_user)
        if ctx.failed:
            return

        os_project_info = self.get_os_project(ctx, user=ctx.target_user, cluster=cluster)
        if ctx.failed:
            return

        ctx.response = os_config = {
            'region_name': cluster_os_info['region_name'],
            'auth': {
                'username': os_user_info['username'],
                'password': os_user_info['password'],
                'user_domain_name': os_user_info['domain_name'],
                'project_name': os_project_info['project_name'],
                'project_domain_name': os_project_info['domain_name'],
                'auth_url': cluster_os_info['auth']['auth_url'],
            }
        }
        return os_config

    def get_admin_os_config(self, ctx, cluster=None):
        """
        Get openstack config
        :param ctx:
        :param cluster:
        :return
        """
        cluster = cluster or self.parse_ctx_cluster(ctx)
        if ctx.failed:
            return
        cluster_dict = self.get_os_cluster(ctx, cluster=cluster)
        if ctx.failed:
            return
        cluster_os_info = cluster_dict['os_info']

        ctx.response = os_config = {
            'region_name': cluster_os_info['region_name'],
            'auth': cluster_os_info['auth'],
        }
        return os_config

    def get_os_client(self, ctx, cluster=None, engine='console', services='shade'):
        """
        Get openstack client
        :param ctx:
        :param cluster:
        :param engine:
        :param services:
        :return
        """
        cluster = cluster or self.parse_ctx_cluster(ctx)
        if ctx.failed:
            return
        os_config = self.get_os_config(ctx, cluster=cluster)
        if ctx.failed:
            return
        return os_api.get_os_client(cluster=cluster, os_config=os_config, engine=engine, services=services)

    def get_admin_os_client(self, ctx, cluster=None):
        """
        Get openstack client
        :param ctx:
        :param cluster:
        :return
        """
        cluster = cluster or self.parse_ctx_cluster(ctx)
        if ctx.failed:
            return
        os_config = self.get_admin_os_config(ctx, cluster=cluster)
        if ctx.failed:
            return
        return os_api.get_admin_os_client(cluster=cluster, os_config=os_config)

    def get_os_user(self, ctx, user):
        """
        Get openstack user info.
        :param ctx:
        :param user:
        :return
        """
        try:
            user_data = user.data
            ldap_info = user_mgr.decrypt_ldap_info(user_data['ldap_info'])
            os_info = user_data['os_info']
            result = {
                'username': ldap_info['cn'],
                'password': ldap_info['password'],
                'domain_name': os_info['domain_name'],
            }
            ctx.data['os_user_info'] = result  # Cache for later use
            return result
        except Exception as e:
            ctx.set_error(errors.USER_OS_INFO_NOT_FOUND, cause=e, status=404)

    def get_os_project(self, ctx, user, cluster):
        """
        Get openstack project info.
        :param ctx:
        :param user:
        :param cluster:
        :return
        """
        try:
            user_data = user.data

            return {
                'project_name':  'u1',
                'domain_name': 'tripleodomain',
            }
        except Exception as e:
            ctx.set_error(errors.USER_OS_PROJECT_NOT_FOUND, cause=e, status=404)

    def execute_client_func(self, ctx, func, on_result, method='sync'):
        """
        Execute client func.
        :param ctx:
        :param func:
        :param on_result:
        :param method: accepted values: 'sync', 'thread', 'process', 'mq'
        """
        data = ctx.data
        ctx.response = None
        method = data.get('call_method') or method
        on_result = data.get('callback') or on_result

        if method == 'sync':
            func_result = func()
            return on_result(ctx, result=func_result)
        elif method == 'mq':
            # TODO: need support
            ctx.status = 202  # Accepted but not finished yet
        else:
            request_user_id = ctx.request_user.id if ctx.request_user else None
            target_user_id = ctx.target_user.id if ctx.target_user else None

            def _executor_callback(future):
                ctx.db_session = md.get_session()
                try:
                    # Get result from future
                    # CancelledError will be raised if task is cancelled
                    if future.exception() is not None:
                        result = '{}. Cause {}.'.format(errors.BACKEND_ERROR, str(future.exception())), None
                    else:
                        result = future.result()
                        result = result if isinstance(result, tuple) else (None, result)
                except futures.CancelledError:
                    result = 'task cancelled', None

                ctx.request_user = md.load(md.User, id=request_user_id) if request_user_id else None
                ctx.target_user = md.load(md.User, id=target_user_id) if target_user_id else None
                with app.app_context():
                    # Callback
                    on_result(ctx=ctx, result=result)
                    # Close DB session
                    ctx.close_db_session()

            if method == 'process':
                future_obj = process_executor.submit(func)
            else:
                future_obj = thread_executor.submit(func)
            future_obj.add_done_callback(_executor_callback)
            ctx.status = 202  # Accepted but not finished yet

    def start_action_log(self, ctx):
        """
        Setup a action log.
        :param ctx:
        :return:
        """

    def finish_action_log(self, ctx, error=None, save=True):
        """
        Finish action log.
        :param ctx:
        :param error:
        :param save:
        :return:
        """
        log_id = ctx.log_args.get('log_id')
        history = md.load_history(log_id) if log_id else None
        if history:
            history.status = md.HistoryStatus.FAILED if error else md.HistoryStatus.SUCCEEDED
            history.end_date = date_util.utc_now()
            contents = history.contents
            if error:
                contents['error'] = self.parse_error(error)
            history.flag_modified('contents')
            if save:
                log_error = md.save(history)
                if log_error:
                    LOG.error('Error saving history log: {}.'.format(log_error))
            return history

    def parse_error(self, error):
        """
        Parse error.
        :param error:
        :return:
        """
        if isinstance(error, Exception):
            return repr(error)

        return str(error)
