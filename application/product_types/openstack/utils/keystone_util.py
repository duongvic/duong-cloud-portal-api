#
# Copyright (c) 2020 FTI-CAS
#

import os

from keystoneauth1 import loading
from keystoneauth1 import session
from keystoneclient.v3 import client

from application import app
from application.utils.data_util import valid_kwargs

LOG = app.logger


def get_credentials(os_info):
    """
    Returns a creds dictionary filled with parsed from env
    Keystone API version used is 3;
    environment variable 'OS_TENANT_NAME' is replaced by
    'OS_PROJECT_NAME'.
    """
    credentials = os_info['auth']

    if not credentials:

        credentials = {
            'username': os.environ.get('OS_USERNAME'),
            'password': os.environ.get('OS_PASSWORD'),
            'auth_url': os.environ.get('OS_AUTH_URL'),
            'project_name': os.environ.get('OS_PROJECT_NAME'),
        }
        if os.getenv('OS_USER_DOMAIN_NAME'):
            credentials['user_domain_name'] = os.getenv('OS_USER_DOMAIN_NAME')

        if os.getenv('OS_PROJECT_DOMAIN_NAME'):
            credentials['project_domain_name'] = os.getenv('OS_PROJECT_DOMAIN_NAME')

    return credentials


def get_session_auth(os_info):
    """
    Get authentication session
    :return:
    """
    loader = loading.get_plugin_loader('password')
    creds = get_credentials(os_info)
    auth = loader.load_from_options(**creds)
    return auth


def get_session(os_info):
    """
    Get s new session
    :return:
    """
    auth = get_session_auth(os_info)
    try:
        cacert = os.environ['OS_CACERT']
    except KeyError:
        return session.Session(auth=auth)
    else:
        insecure = os.getenv('OS_INSECURE', '').lower() == 'true'
        cacert = False if insecure else cacert
        return session.Session(auth=auth, verify=cacert)


def get_endpoint(os_info, service_type, endpoint_type='publicURL'):
    """
    Get s new session
    :param os_info
    :param service_type
    :param endpoint_type
    :return:
    """
    auth = get_session_auth(os_info)
    # for multi-region, we need to specify region
    # when finding the endpoint
    session_ = get_session(os_info)
    return session_.get_endpoint(auth=auth, service_type=service_type,
                                 endpoint_type=endpoint_type,
                                 region_name=os_info['region_name'])


def get_keystone_client(os_info):
    """
    Get Keystone client

    :param os_info
    :return:
    """
    sess = get_session(os_info)
    return client.Client(session=sess)


def get_project(ks_client, project_id):
    """
    Get a project
    :param ks_client:
    :param project_id: ID of Project
    :return:
    """
    try:
        return ks_client.projects.get(project=project_id)
    except Exception as e:
        LOG.error("Error [get_project(keystone_client)]. "
                  "Exception message, '%s'", e)
    return None


def get_projects(ks_client, domain_id=None, user=None, parent=None, **kwargs):
    """
    Get all projects matched

    :param ks_client:
    :param domain_id: ID of domain
    :param user: ID of user who created projects
    :param parent:
    :param kwargs: other options
    :return:
    """
    try:
        return ks_client.projects.list(domain=domain_id, user=user, parent=parent, **kwargs)
    except Exception as e:
        LOG.error("Error [get_projects(keystone_client)]. "
                  "Exception message, '%s'", e)
        return None


@valid_kwargs('tags', 'immutable')
def create_project(ks_client, name, description=None, domain_id='default',
                   enabled=True, parent_id=None, **kwargs):
    """
    Create a new Project

    :param ks_client:
    :param name: name of project
    :param description:
    :param domain_id:
    :param enabled:
    :param parent_id:
    :param kwargs:
    :return:
    """
    try:
        return ks_client.projects.create(name=name, domain=domain_id, description=description,
                                         enabled=enabled, parent=parent_id, **kwargs)
    except Exception as e:
        LOG.error("Error [create_project(keystone_client)]. "
                  "Exception message, '%s'", e)
        return None


@valid_kwargs('tags', 'immutable')
def update_project(ks_client, project_id, name=None, domain_id=None, description=None,
                   enabled=None, **kwargs):
    """
    Update a project

    :param ks_client:
    :param project_id: ID of project
    :param name: Name of project
    :param domain_id: ID of domain
    :param description:
    :param enabled:
    :param kwargs: Other options
    :return:
    """
    try:
        return ks_client.projects.update(project=project_id, name=name, domain=domain_id,
                                         description=description, enabled=enabled, **kwargs)
    except Exception as e:
        LOG.error("Error [update_project(keystone_client)]. "
                  "Exception message, '%s'", e)
        return None


def delete_project(ks_client, project_id):
    """
    Delete a project

    :param ks_client:
    :param project_id: ID of project
    :return:
    """
    try:
        ks_client.projects.delete(project=project_id)
    except Exception as e:
        LOG.error("Error [delete_project(keystone_client)]. "
                  "Exception message, '%s'", e)
    return False


def get_user(ks_client, user_id=None):
    """
    Get a user by user's id

    :param ks_client:
    :param user_id: ID of user
    :return:
    """
    try:
        return ks_client.users.get(user=user_id)
    except Exception as e:
        LOG.error("Error [get_user(keystone_client)]. "
                  "Exception message, '%s'", e)
        return None


def get_users(ks_client, project_id=None, domain_id='default', group=None, **kwargs):
    """
    Get all users matched

    :param ks_client:
    :param project_id: ID of project
    :param domain_id: ID of domain
    :param group: ID of User
    :param kwargs: Other options
    :return:
    """
    try:
        return ks_client.users.list(project=project_id, domain=domain_id, group=group, **kwargs)
    except Exception as e:
        LOG.error("Error [get_users(keystone_client)]. "
                  "Exception message, '%s'", e)


@valid_kwargs('ignore_change_password_upon_first_use', 'ignore_password_expiry',
              'ignore_lockout_failure_attempts', 'lock_password',
              'multi_factor_auth_enabled', 'multi_factor_auth_rules', 'ignore_user_inactivity')
def create_user(ks_client, name, domain_id=None, project_id=None, password=None,
                email=None, description=None, enabled=True,
                default_project_id=None, **kwargs):
    """
    Create a new project

    :param ks_client:
    :param name:
    :param domain_id: ID of domain
    :param project_id: ID of project
    :param password:
    :param email:
    :param description:
    :param enabled:
    :param default_project_id:
    :param kwargs:
    :return:
    """
    try:
        return ks_client.users.create(name=name, domain=domain_id, project=project_id, email=email,
                                      password=password, description=description, enabled=enabled,
                                      default_project=default_project_id, **kwargs)
    except Exception as e:
        LOG.error("Error [create_user(keystone_client)]. "
                  "Exception message, '%s'", e)
        return None


def assign_role(ks_client, role_id, user_id=None, project_id=None, domain_id=None, group_id=None,
                system=None, os_inherit_extension_inherited=False, **kwargs):
    """
    Grant a role to a user or group on a domain or project.

    :param ks_client
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
        return ks_client.roles.grant(role=role_id, user=user_id, project=project_id,
                                     domain=domain_id, group=group_id, system=system,
                                     os_inherit_extension_inherited=os_inherit_extension_inherited,
                                     **kwargs)
    except Exception as e:
        LOG.error("Error [assign_role(keystone_client)]. "
                  "Exception message, '%s'", e)
        return None


def get_roles(ks_client, user_id=None, group_id=None, system=None, domain_id=None,
              project_id=None, os_inherit_extension_inherited=False, **kwargs):
    """
    Get all roles
    :param ks_client
    :param user_id
    :param project_id:
    :param domain_id
    :param group_id:
    :param system
    :param os_inherit_extension_inherited:
    :param kwargs
    """
    try:
        return ks_client.roles.list(user=user_id, project=project_id, domain=domain_id, group=group_id,
                                    system=system, os_inherit_extension_inherited=os_inherit_extension_inherited,
                                    **kwargs)
    except Exception as e:
        LOG.error("Error [get_roles(keystone_client)]. "
                  "Exception message, '%s'", e)
        return None


@valid_kwargs('ignore_change_password_upon_first_use', ' ',
              'ignore_lockout_failure_attempts', 'lock_password',
              'multi_factor_auth_enabled', 'multi_factor_auth_rules', 'ignore_user_inactivity')
def update_user(ks_client, user_id, name=None, domain_id=None, project_id=None, password=None,
                email=None, description=None, enabled=True,
                default_project_id=None, **kwargs):
    """
    Update an existed user

    :param ks_client:
    :param user_id:
    :param name:
    :param domain_id: ID of domain
    :param project_id: ID of project
    :param password:
    :param email:
    :param description:
    :param enabled:
    :param default_project_id:
    :param kwargs:
    :return:
    """
    try:
        return ks_client.users.update(user=user_id, name=name, domain=domain_id, project=project_id,
                                      password=password, email=email, description=description, enabled=enabled,
                                      default_project=default_project_id, **kwargs)
    except Exception as e:
        LOG.error("Error [update_user(keystone_client)]. "
                  "Exception message, '%s'", e)
        return None


def delete_user(ks_client, user_id):
    """
    Delete an user

    :param ks_client:
    :param user_id: ID of user
    :return:
    """
    try:
        ks_client.users.delete(user=user_id)
        return True
    except Exception as e:
        LOG.error("Error [delete_user(keystone_client)]. "
                  "Exception message, '%s'", e)
    return False
