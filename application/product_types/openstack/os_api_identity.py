#
# Copyright (c) 2020 FTI-CAS
#

from foxcloud import exceptions as fox_exc

from application import app
from application.utils.data_util import valid_kwargs

LOG = app.logger


class OSIdentityMixin(object):

    def ks_get_project(self, project_id, listing={}):
        """
        Get a project
        :param project_id: ID of Project
        :return:
        """
        try:
            data = self.client.shade.shade.get_project(project_id=project_id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [ks_get_project(%s)]: %s.", project_id, e)
            return self.fail(e)

    def ks_get_projects(self, domain_id=None, user=None, parent=None, listing={}, **kw):
        """
        Get all projects matched

        :param domain_id: ID of domain
        :param user: ID of user who created projects
        :param parent:
        :param kw: other options
        :return:
        """

        try:
            data = self.client.shade.get_projects(domain=domain_id, user_id=user, parent=parent, **kw)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [ks_get_projects()]: %s.", e)
            return self.fail(e)

    @valid_kwargs('tags', 'immutable')
    def ks_create_project(self, name, description=None, domain_id=None,
                          enabled=True, parent_id=None, **kwargs):
        """
        Create a new Project

        :param name: name of project
        :param description:
        :param domain_id:
        :param enabled:
        :param parent_id:
        :param kwargs:
        :return:
        """
        try:
            domain_id = domain_id or self.default_domain
            data = self.client.shade.create_project(name=name, domain_id=domain_id, description=description,
                                                    enabled=enabled, parent=parent_id, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [ks_create_project(%s)]: %s.", name, e)
            return self.fail(e)

    @valid_kwargs('tags', 'immutable')
    def ks_update_project(self, project_id, name=None, domain_id=None, description=None,
                          enabled=None, **kwargs):
        """
        Update a project

        :param project_id: ID of project
        :param name: Name of project
        :param domain_id: ID of domain
        :param description:
        :param enabled:
        :param kwargs: Other options
        :return:
        """
        try:
            data = self.client.shade.update_project(project_id=project_id, name=name,
                                                    domain_id=domain_id,
                                                    description=description,
                                                    enabled=enabled, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [ks_update_project(%s)]: %s.", project_id, e)
            return self.fail(e)

    def ks_delete_project(self, project_id):
        """
        Delete a project

        :param project_id: ID of project
        :return:
        """
        try:
            data = self.client.shade.delete_project(project_id=project_id)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [ks_delete_project(%s)]: %s.", project_id, e)
            return self.fail(e)

    def ks_get_user(self, user_id=None, listing={}):
        """
        Get a user by user's id

        :param user_id: ID of user
        :return:
        """
        try:
            data = self.client.shade.get_user(user_id=user_id)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [ks_get_user(%s)]: %s.", user_id, e)
            return self.fail(e)

    def ks_get_users(self, project_id=None, domain_id=None, group=None,
                     default_project_id=None, listing={}, **kw):
        """
        Get all users matched

        :param project_id: ID of project
        :param domain_id: ID of domain
        :param group: ID of User
        :param default_project_id
        :param kw: Other options
        :return:
        """
        try:
            domain_id = domain_id or self.default_domain
            data = self.client.shade.get_users(project=project_id, domain=domain_id, group=group,
                                               default_project_id=default_project_id, **kw)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [ks_get_users()]: %s.", e)
            return self.fail(e)

    def ks_create_user(self, name, domain_id=None, project_id=None, password=None,
                       email=None, description=None, enabled=True,
                       default_project_id=None, **kwargs):
        try:
            domain_id = domain_id or self.default_domain
            data = self.client.shade.create_user(name=name, domain_id=domain_id, project_id=project_id,
                                                 password=password, email=email, description=description,
                                                 enabled=enabled, default_project_id=default_project_id,
                                                 **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [ks_get_users()]: %s.", e)
            return self.fail(e)

    def ks_update_user(self, user_id, name, domain_id=None, project_id=None, password=None,
                       email=None, description=None, enabled=True,
                       default_project_id=None, **kwargs):
        try:
            domain_id = domain_id or self.default_domain
            data = self.client.shade.update_user(user_id=user_id, name=name, domain_id=domain_id,
                                                 project_id=project_id, password=password, email=email,
                                                 description=description, enabled=enabled,
                                                 default_project_id=default_project_id, **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [ks_get_users()]: %s.", e)
            return self.fail(e)

    def ks_assign_role(self, role_id, user_id=None, project_id=None, domain_id=None, group_id=None,
                       system=None, os_inherit_extension_inherited=False, **kwargs):
        """
        Grant a role to a user or group on a domain or project.

        :param role_id:
        :param user_id
        :param project_id:
        :param domain_id
        :param group_id:
        :param system
        :param os_inherit_extension_inherited:
        :param kwargs
        :return
        """
        try:
            data = self.client.shade.assign_role(role=role_id, user=user_id, project_id=project_id,
                                                 domain_id=domain_id, group_id=group_id, system=system,
                                                 os_inherit_extension_inherited=os_inherit_extension_inherited,
                                                 **kwargs)
            return data.parse()
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [ks_assign_role(%s)]: %s.", role_id, e)
            return self.fail(e)

    def ks_get_roles(self, user_id=None, group_id=None, system=None, domain_id=None,
                     project_id=None, os_inherit_extension_inherited=False, listing={}, **kw):
        """
        Get all roles
        :param user_id
        :param project_id:
        :param domain_id
        :param group_id:
        :param system
        :param os_inherit_extension_inherited:
        :param kw
        """
        try:
            data = self.client.shade.get_roles(user_id=user_id, project_id=project_id, domain_id=domain_id,
                                               group_id=group_id, system=system,
                                               os_inherit_extension_inherited=os_inherit_extension_inherited,
                                               **kw)
            return data.parse(**listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [ks_get_roles()]: %s.", e)
            return self.fail(e)

    # *************************************
    # PROJECT
    # *************************************

    def get_project(self, project_id, filters=None, domain_id=None, listing={}):
        """
        Get a project

        :param project_id
        :param filters
        :param domain_id
        :return
        """
        try:
            p = self.client.shade.get_project(name_or_id=project_id, filters=filters,
                                              domain_id=domain_id)
            return self.parse(p, **listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_project(%s)]: %s.", project_id, e.orig_message)
            return self.fail(e)

    def get_projects(self, domain_id=None, name_or_id=None, filters=None, listing={}):
        """
        Get all projects

        :param domain_id
        :param name_or_id
        :param filters
        :return
        """
        try:
            p = self.client.shade.list_projects(name_or_id=name_or_id, filters=filters,
                                                domain_id=domain_id)
            return self.parse(p, **listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_projects(%s)]: %s.", name_or_id, e.orig_message)
            return self.fail(e)

    def create_project(self, name, description=None, domain_id=None, enabled=True):
        """
        Create a new project
        Only the admin has permission to create project

        :param name
        :param description
        :param domain_id
        :param enabled
        :return
        """
        try:
            domain_id = domain_id or self.default_domain
            p = self.client.shade.create_project(name=name, description=description,
                                                 domain_id=domain_id, enabled=enabled)
            return self.parse(p)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_project(%s)]: %s.", name, e.orig_message)
            return self.fail(e)

    def update_project(self, project_id, description, enabled=True, **kw):
        """
        Update a project being created
        Only the admin has permission to update project

        :param project_id:
        :param description:
        :param enabled:
        :param kw: ('description')
        :return
        """
        try:
            p = self.client.shade.update_project(name_or_id=project_id,
                                                 description=description,
                                                 enabled=enabled, **kw)
            return self.parse(p)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [update_project(%s)]: %s.", project_id, e.orig_message)
            return self.fail(e)

    def delete_project(self, project_id, domain_id=None):
        """
        Delete a project being created
        Only the admin has permission to delete project

        :param project_id
        :param domain_id
        :return
        """
        try:
            p = self.client.shade.delete_project(name_or_id=project_id,
                                                 domain_id=domain_id)
            return self.parse(p)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_project(%s)]: %s.", project_id, e.orig_message)
            return self.fail(e)

    # *************************************
    # USER
    # *************************************

    def get_user(self, user_id, filters=None, listing={}, **kw):
        """
        Get the user

        :param user_id:
        :param filters:
        :param kw: ('domain_id')
        :return
        """
        try:
            u = self.client.shade.get_user(name_or_id=user_id, filters=filters, **kw)
            return self.parse(u, **listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_user(%s)]: %s.", user_id, e.orig_message)
            return self.fail(e)

    def get_users(self, domain_id=None, listing={}):
        """
        Get all users

        :param domain_id
        :return
        """
        try:
            u = self.client.shade.list_users()
            return self.parse(u, **listing)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [get_users(%s)] : %s.", domain_id, e.orig_message)
            return self.fail(e)

    def create_user(self, name, project_id=None, password=None, domain_id=None, email=None,
                    description=None, enabled=True, default_project=None):
        """
        Create a new project

        :param name:
        :param project_id: ID of project
        :param password:
        :param domain_id:
        :param email:
        :param description:
        :param enabled:
        :param default_project:
        :return:
        """
        try:
            domain_id = domain_id or self.default_domain
            u = self.client.shade.create_user(name=name, password=password, email=email,
                                              default_project=default_project, enabled=enabled,
                                              domain_id=domain_id, project=project_id,
                                              description=description)
            return self.parse(u)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [create_user(%s)]: %s.", name, e.orig_message)
            return self.fail(e)

    def update_user(self, user_id, **kwargs):
        """
        Update an user being created

        :param user_id:
        :param kwargs: ('name', 'email', 'enabled', 'domain_id', 'password',
                        'description', 'default_project')
        :return:
        """
        try:
            u = self.client.shade.update_user(name_or_id=user_id, **kwargs)
            return self.parse(u)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [update_user(%s)]: %s.", user_id, e.orig_message)
            return self.fail(e)

    def delete_user(self, user_id, **kwargs):
        """
        Delete an user being created

        :param user_id: ID of user
        :param kwargs: ('domain_id')
        :return:
        """
        try:
            u = self.client.shade.delete_user(name_or_id=user_id, **kwargs)
            return self.parse(u)
        except fox_exc.FoxCloudException as e:
            LOG.error("Error [delete_user(%s)]: %s.", user_id, e.orig_message)
            return self.fail(e)
