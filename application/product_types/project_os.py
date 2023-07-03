#
# Copyright (c) 2020 FTI-CAS
#

from application import app
from application.base import errors
from application import models as md
from application.product_types import base, os_base
from application.product_types.openstack import os_api
from application.managers import base as base_mgr, task_mgr, user_mgr

LOG = app.logger

ADMIN_ROLES = (md.UserRole.ADMIN, md.UserRole.ADMIN_SALE, md.UserRole.ADMIN_IT)
GET_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
LIST_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
CREATE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)
UPDATE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)
DELETE_ROLES = (md.UserRole.USER, md.UserRole.ADMIN_IT, md.UserRole.ADMIN)


class OSProject(os_base.OSBase):
    """
    Openstack Project
    """

    def __init__(self):
        """
        Initialize Project
        """
        super().__init__()

    @property
    def supported(self):
        return True

    def get_project(self, ctx):
        """
        Get a project.

        :param ctx:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        data = ctx.data
        project = os_client.get_project(project_id=data['project_id'], filters=None)
        base_mgr.dump_object(ctx, object=project)
        return project

    def get_projects(self, ctx):
        """
        Get all projects created by user.

        :param ctx:
        :return:
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        projects = os_client.get_projects()
        base_mgr.dump_object(ctx, object=projects)
        return projects

    def create_project(self, ctx):
        """
        Create a new project.
        :param ctx:
        :return:
        """
        self.validate_create_project(ctx)
        if ctx.failed:
            return

        data = ctx.data

        # TODO use order instead of ctx.data
        order = md.load_order(data.get('order') or data['order_id'])
        if not order:
            ctx.set_error(errors.ORDER_NOT_FOUND, status=404)
            return

        user = ctx.target_user = order.user
        if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
            return

        os_info = self.get_os_user(ctx)
        if ctx.failed:
            return

        user_info = os_info['account']
        project_info = os_info['project']
        cluster = self.get_os_cluster(ctx, user_info['cluster'])
        project = {
            'project_id': project_info['id'],
            'name': data['name'],
            'port_security_enabled': data.get('port_security_enabled'),
            'mtu_size': data.get('mtu_size') or os_api.get_mtu_size(cluster=cluster),
        }
        self.do_create_project(ctx, project=project)

    def validate_create_project(self, ctx):
        """
        Validate project input
        :param ctx
        :return
        """
        data = ctx.data

        # Validate name
        if 'name' in data and not self.validate_project_name(ctx, name=data['name']):
            return
        # Validate mtu size
        if 'mtu_size' in data and not self.validate_project_mtu_size(ctx, mtu_size=data['mtu_size']):
            return

    def validate_project_name(self, ctx, name):
        """
        Validate project input
        :param ctx:
        :param name:
        :return:
        """
        name = name.strip() if name else None
        if not name or len(name) > 32:
            e = ValueError('Network name exceeds 32 characters length.')
            LOG.error(e)
            ctx.set_error(errors.NET_NAME_INVALID, cause=e, status=406)
            return
        ctx.data['name'] = name
        return True

    def validate_project_mtu_size(self, ctx, mtu_size):
        """
        Validate project input
        :param ctx:
        :param mtu_size:
        :return:
        """
        return True

    def do_create_project(self, ctx, project):
        """
        Subclass should override this.
        :param ctx:
        :param project:
        :return
        """
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return
        
        result = os_client.create_project(name=project['name'],
                                          project_id=project['project_id'],
                                          port_security_enabled=project['port_security_enabled'],
                                          mtu_size=project['mtu_size'])
        if result.get('error'):
            ctx.set_error(error=errors.NET_CREATE_FAILED, cause=result['error'], status=400)
            return

        ctx.status = 201
        base_mgr.dump_object(ctx, object=project)
        return project

    def update_project(self, ctx):
        """
        Update a project.
        :param ctx:
        :return:
        """

    def delete_project(self, ctx):
        """
        Delete a project.
        :param ctx:
        :return:
        """
        data = ctx.data
        os_client = self.get_os_client(ctx)
        if ctx.failed:
            return

        result = os_client.delete_project(project_id=data['project_id'])
        if result.get('error'):
            ctx.set_error(error=errors.NET_DELETE_FAILED, cause=result['error'], status=500)
            return
