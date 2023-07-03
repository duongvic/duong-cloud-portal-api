#
# Copyright (c) 2020 FTI-CAS
#

import re

from foxcloud import client as fox_client

from application import app
from application.base import errors
from application.managers import base as base_mgr
from application import models as md
from application.utils import date_util, mail_util, str_util

LOG = app.logger


ADMIN_ROLES = (md.UserRole.ADMIN, md.UserRole.ADMIN_SALE, md.UserRole.ADMIN_IT)
GET_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
LIST_ROLES = ADMIN_ROLES
CREATE_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
UPDATE_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
DELETE_ROLES = ADMIN_ROLES


def get_ldap_config(ctx):
    """
    Get LDAP config from DB.
    :param ctx:
    :return:
    """
    ldap_config = md.query(md.Configuration,
                           type=md.ConfigurationType.BACKEND,
                           name='ldap_config',
                           status=md.ConfigurationStatus.ENABLED,
                           order_by=md.Configuration.version.desc()).first()
    if not ldap_config:
        e = ValueError('Config BACKEND/ldap_config not found in database.')
        LOG.error(e)
        ctx.set_error(errors.CONFIG_NOT_FOUND, cause=e, status=404)
        return
    return ldap_config.contents


def encrypt_ldap_info(ldap_info):
    """
    Encrypt user LDAP info.
    :param ldap_info:
    :return:
    """
    return str_util.jwt_encode_token(ldap_info)


def decrypt_ldap_info(data):
    """
    Decrypt user LDAP info.
    :param data:
    :return:
    """
    return str_util.jwt_decode_token(data)


def create_ldap_dn(ldap_info):
    """
    Create LDAP dn from ldap_info.
    :param ldap_info:
    :return:
    """
    return 'cn={},ou={},{}'.format(ldap_info['cn'], ldap_info['ou'], ldap_info['dc'])


def create_ldap_client(ctx, user=None):
    """
    Create LDAP client.
    :param ctx:
    :param user: LDAP account, if None, use admin account
    :return:
    """
    ldap_config = get_ldap_config(ctx)
    if ctx.failed:
        return
    if not ldap_config['enabled']:
        return None

    ctx.data = ctx.data or {}
    ctx.data['ldap_config'] = ldap_config

    params = {
        'ldap_endpoint': ldap_config['url'],
    }
    if user:
        ldap_info = decrypt_ldap_info(user.data['ldap_info'])
        params.update({
            'dn': create_ldap_dn(ldap_info),
            'password': ldap_info['password'],
        })
    else:
        params.update({
            'dn': 'cn={},{}'.format(ldap_config['cn'], ldap_config['dc']),
            'password': ldap_config['password'],
        })
    return fox_client.Client('1', engine='console', services='ldap', **params).ldap


def create_ldap_user(ctx, user):
    ldap_client = create_ldap_client(ctx)  # Use LDAP admin account to create user
    if not ldap_client or ctx.failed:
        return

    data = ctx.data
    try:
        dc = data['ldap_config']['dc']
        username = user.user_name
        password = data['password']
        ldap_client.create_user(base=dc, username=username, password=password)

        # Update user model object
        user_data = user.data or {}
        user_data['ldap_info'] = encrypt_ldap_info({
            'dc': dc,
            'ou': 'Users',
            'cn': username,
            'password': password,
        })
        user.data = user_data
        user.flag_modified('data')
    except Exception as e:
        error = str(e)
        try:
            error = str(e.orig_message.args[0]['desc']).lower()
            if 'already exists' in error:
                error = errors.USER_ALREADY_EXISTS
        except:
            pass
        ctx.set_error(error, cause=e, status=500)

    finally:  # Destroy client session
        try:
            ldap_client.unbind()
        except Exception as e:
            LOG.warning('Failed to close LDAP session: %s', e)


def update_ldap_user(ctx, user):
    ldap_client = create_ldap_client(ctx)  # Use LDAP admin account to update user
    if not ldap_client or ctx.failed:
        return

    data = ctx.data
    try:
        ldap_info = decrypt_ldap_info(user.data['ldap_info'])

        # Change user password
        password = data.get('password')
        if password:
            ldap_client.change_password(dn=create_ldap_dn(ldap_info),
                                        old_password=ldap_info['password'],
                                        new_password=password)

            # Update user model object
            ldap_info.update({
                'password': password,
            })
            user.data['ldap_info'] = encrypt_ldap_info(ldap_info)
            user.flag_modified('data')

    except Exception as e:
        error = str(e)
        try:
            error = str(e.orig_message.args[0]['desc'])
        except:
            pass
        ctx.set_error(error, cause=e, status=500)

    finally:  # Destroy client session
        try:
            ldap_client.unbind()
        except Exception as e:
            LOG.warning('Failed to close LDAP session: %s', e)


def delete_ldap_user(ctx, user):
    ldap_client = create_ldap_client(ctx)  # Use LDAP admin account to create user
    if not ldap_client or ctx.failed:
        return

    try:
        ldap_info = decrypt_ldap_info(user.data['ldap_info'])
        ldap_client.delete_user(dn=create_ldap_dn(ldap_info))

        # Update user model object
        (user.data or {}).pop('ldap_info', None)
        user.flag_modified('data')

    except Exception as e:
        error = str(e)
        try:
            error = str(e.orig_message.args[0]['desc'])
        except:
            pass
        ctx.set_error(error, cause=e, status=500)

    finally:  # Destroy client session
        try:
            ldap_client.unbind()
        except Exception as e:
            LOG.warning('Failed to close LDAP session: %s', e)


def check_user(ctx, roles):
    """
    Check request user permission.
    :param ctx:
    :param roles:
    :return:
    """
    if roles and not ctx.check_request_user_role(roles):
        ctx.set_error(errors.USER_ACTION_NOT_ALLOWED, status=403)
        return

    if ctx.is_cross_user_request:
        # Cross user request, but request user role is lower than target user role
        if ctx.compare_roles() <= 0:
            ctx.set_error(errors.USER_ACTION_NOT_ALLOWED, status=403)
            return

    else:  # request_user == target_user
        user = ctx.target_user
        if not user:
            ctx.set_error(errors.USER_NOT_FOUND, status=404)
            return

        if user.status != md.UserStatus.ENABLED:
            if user.status == md.UserStatus.DEACTIVATED:
                ctx.set_error(errors.USER_NOT_ACTIVATED, status=403)
                return

            if user.status in (md.UserStatus.BLOCKED, md.UserStatus.DELETED):
                ctx.set_error(errors.USER_BLOCKED_OR_DELETED, status=403)
                return

            ctx.set_error(errors.USER_ACTION_NOT_ALLOWED, status=403)
            return

    return True


def get_user(ctx):
    """
    Get user attributes from ctx.target_user.
    :param ctx:
    :return:
    """
    if not check_user(ctx, roles=GET_ROLES):
        return

    user = ctx.target_user
    base_mgr.dump_object(ctx, object=user)
    return user


def get_users(ctx):
    """
    Get multiple users. Only ADMIN can do this action.
    :param ctx: sample ctx data:
        {
            'page': <page index starts from 0>,
            'page_size': <page size>,
            'sort_by': <attr to sort by>,
            'fields': <attrs to get as a list of str>,
            'condition': <reserved, custom query>,
        }
    :return:
    """
    return base_mgr.dump_objects(ctx, model_class=md.User, roles_required=LIST_ROLES)


def create_user(ctx):
    """
    Create a new user.
    :param ctx:
    :return:
    """
    data = ctx.data
    user_name = data['user_name'] = data['user_name'].lower().strip()
    email = data['email'] = data['email'].lower().strip()

    # If username is '###', we use email instead
    if user_name == '###':
        user_name = data['user_name'] = email
    else:
        # Validate user info
        # User name pattern
        pattern = '^[a-z][a-z0-9@_\\.\\-]*$'
        if not re.match(pattern, user_name):
            ctx.set_error(errors.USER_NAME_INVALID, status=406)
            return

    # Check e-mail validity
    if not str_util.valid_email(email):
        ctx.set_error(errors.USER_EMAIL_INVALID, status=406)
        return

    # Check user exists
    names = [user_name, email]
    if md.query(md.User, md.User.user_name.in_(names) | md.User.email.in_(names)).first():
        ctx.set_error(errors.USER_ALREADY_EXISTS, status=406)
        return

    user = md.User(user_name=user_name, email=email,
                   role=md.UserRole.USER, status=md.UserStatus.DEACTIVATED,
                   create_date=date_util.utc_now())
    ctx.target_user = user
    ctx.request_user = ctx.request_user or user

    # Set user attributes
    _update_user_attrs(ctx, user, action='create_user')
    if ctx.failed:
        return

    # Create user in LDAP backend
    create_ldap_user(ctx, user=user)
    if ctx.failed:
        return

    success = True
    try:
        if user.status == md.UserStatus.DEACTIVATED:
            try:
                # Send activation e-mail
                mail_util.send_mail_user_activation(user)
            except BaseException as e:
                success = False
                LOG.error(e)
                ctx.set_error(errors.MAIL_ACTIVATION_SEND_FAILED, cause=e, status=500)
                return
    finally:
        # Remove newly created user in LDAP backend
        if not success:
            delete_ldap_user(ctx.copy(), user)

    # Save user to DB
    error = md.save_new(user)
    if error:
        ctx.set_error(error, status=500)
        return


def _update_user_attrs(ctx, user, action='update_user'):
    """
    Update user data fields.
    :param ctx:
    :param action: 'create_user', 'update_user', 'reset_password'
    :return:
    """
    data = ctx.data
    is_admin = ctx.check_request_user_role(ADMIN_ROLES)

    # Set role (Admin only)
    role = data.get('role') if is_admin else None
    if role:
        if not md.UserRole.is_valid(role):
            ctx.set_error(errors.USER_ROLE_INVALID, status=406)
            return

        # User with lower role cannot set higher role for another user
        if md.UserRole.compare(role, ctx.request_user.role) > 0:
            ctx.set_error(errors.USER_ACTION_NOT_ALLOWED, status=403)
            return

        user.role = role

    # Set status (Admin only)
    status = data.get('status') if is_admin else None
    if status:
        if not md.UserStatus.is_valid(status):
            ctx.set_error(errors.USER_STATUS_INVALID, status=406)
            return

        user.status = status

    # Set password (required when create new and reset password)
    password = data['password'] if action in ('create_user', 'reset_password') else data.get('password')
    if password:
        # User must provide current password to check for matching (if updates)
        if not is_admin:
            if action == 'update_user' and not str_util.check_user_password(user.password_hash, data['old_password']):
                ctx.set_error(errors.USER_PASSWORD_INVALID, status=406)
                return

        # New password must meet some requirements
        requirement = app.config['PASSWORD_REQUIREMENT']
        if not str_util.valid_user_password(password, requirement=requirement):
            e = ValueError('Password requirements: ' +
                           str_util.password_requirement_desc(requirement))
            LOG.error(e)
            ctx.set_error(errors.USER_PASSWORD_REQUIREMENT_NOT_MET, cause=e, status=406)
            return

        user.set_password(password)

    # Other attributes
    for attr in md.User.__user_update_fields__:
        if attr in data:
            value = data[attr]
            if isinstance(value, str):
                value = value.strip() or None
            setattr(user, attr, value)


def update_user(ctx):
    """
    Update user data.
    :param ctx:
    :return:
    """
    if not check_user(ctx, roles=UPDATE_ROLES):
        return

    user = ctx.target_user

    # Common user attributes
    _update_user_attrs(ctx, user, action='update_user')
    if ctx.failed:
        return

    # Update underlying LDAP user
    # TODO: LDAP may support other attrs rather than only password?
    if 'password' in ctx.data:
        update_ldap_user(ctx, user)
        if ctx.failed:
            return

    # Save user to DB
    error = md.save(user)
    if error:
        ctx.set_error(error, status=500)
        return

    return user


def delete_user(ctx):
    """
    Delete user.
    :param ctx:
    :return:
    """
    if not check_user(ctx, roles=DELETE_ROLES):
        return

    user = ctx.target_user
    remove_from_db = ctx.data.get('remove_from_db', False)
    if remove_from_db:
        # Delete the user in LDAP backend
        delete_ldap_user(ctx, user)
        if ctx.failed:
            return

        error = md.remove(user)
    else:
        # just mark the user as deleted
        user.status = md.UserStatus.DELETED
        error = md.save(user)

    if error:
        ctx.set_error(error, status=500)
        return


def login(ctx):
    """
    Login an user.
    :param ctx: {
        'user_name': <user name or email>,
        'password': <str>,
        'remember_me': <bool>,
        'get_user_data': <true to get user attrs>,
    }
    :return:
    """
    if not check_user(ctx, roles=None):
        return

    data = ctx.data
    password = data['password']

    user = ctx.target_user
    if not str_util.check_user_password(user.password_hash, password):
        ctx.set_error(errors.USER_PASSWORD_INVALID, status=401)
        return

    access_token_exp = app.config['API_ACCESS_TOKEN_EXPIRATION'].total_seconds()
    refresh_token_exp = app.config['API_REFRESH_TOKEN_EXPIRATION'].total_seconds()
    base_data = {
        'id': user.id,
        'user_name': user.user_name,
        'email': user.email,
        'role': user.role,
        'token_type': 'Bearer',
        'access_token': user.gen_token(expires_in=access_token_exp),
        'expires_in': access_token_exp,
        'expires_on': date_util.utc_future(seconds=access_token_exp),
        'refresh_token': user.gen_token(expires_in=refresh_token_exp),
        'refresh_token_expires_in': refresh_token_exp,
        'refresh_token_expires_on': date_util.utc_future(seconds=refresh_token_exp),
    }

    if data.get('get_user_data'):
        base_mgr.dump_object(ctx, object=user)
        if ctx.failed:
            return
        ctx.response.update(base_data)
    else:
        ctx.response = base_data

    return ctx.response


def logout(ctx):
    """
    Log out an user.
    :param ctx:
    :return:
    """


def refresh_token(ctx):
    """
    Refresh token for user.
    :param ctx:
    :return:
    """
    if not check_user(ctx, roles=None):
        return

    user = ctx.target_user
    access_token_exp = app.config['API_ACCESS_TOKEN_EXPIRATION'].total_seconds()
    refresh_token_exp = app.config['API_REFRESH_TOKEN_EXPIRATION'].total_seconds()
    response = {
        'token_type': 'Bearer',
        'access_token': user.gen_token(expires_in=access_token_exp),
        'expires_in': access_token_exp,
        'expires_on': date_util.utc_future(seconds=access_token_exp),
        'refresh_token': user.gen_token(expires_in=refresh_token_exp),
        'refresh_token_expires_in': refresh_token_exp,
        'refresh_token_expires_on': date_util.utc_future(seconds=refresh_token_exp),
    }
    ctx.response = response
    return response


def activate_user(ctx):
    """
    Activate user account.
    :param ctx:
    :return:
    """
    data = ctx.data
    activation_token = data['token']

    try:
        user_name = str_util.jwt_decode_token(activation_token)
    except BaseException as e:
        ctx.set_error(errors.USER_TOKEN_INVALID, cause=e, status=401)
        return

    user = md.query(md.User, user_name=user_name).first()
    if not user:
        ctx.set_error(errors.USER_NOT_FOUND, status=404)
        return

    ctx.target_user = user
    ctx.request_user = ctx.request_user or user

    if user.status == md.UserStatus.ENABLED:
        ctx.set_error(errors.USER_ALREADY_ACTIVATED, status=406)
        return

    if user.status != md.UserStatus.DEACTIVATED:
        ctx.set_error(errors.USER_BLOCKED_OR_DELETED, status=403)
        return

    user.status = md.UserStatus.ENABLED
    error = md.save(user)
    if error:
        ctx.set_error(error, status=500)
        return

    return user


def request_reset_password(ctx):
    """
    Request resetting password for an user.
    :param ctx:
    :return:
    """
    if not check_user(ctx, roles=UPDATE_ROLES):
        return

    user = ctx.target_user

    try:
        # Send reset password e-mail
        mail_util.send_mail_password_reset(user)
    except BaseException as e:
        LOG.error(e)
        ctx.set_error(errors.MAIL_RESET_PASSWORD_SEND_FAILED, cause=e, status=500)
        return

    return user


def reset_password(ctx):
    """
    Reset password for an user.
    :param ctx:
    :return:
    """
    data = ctx.data
    reset_token = data['token']

    try:
        user_name = str_util.jwt_decode_token(reset_token)
    except BaseException as e:
        ctx.set_error(errors.USER_TOKEN_INVALID, cause=e, status=401)
        return

    user = md.query(md.User, user_name=user_name).first()
    if not user:
        ctx.set_error(errors.USER_NOT_FOUND, status=404)
        return

    ctx.target_user = user
    ctx.request_user = ctx.request_user or user

    if not check_user(ctx, roles=UPDATE_ROLES):
        return

    # New password for user
    ctx.data = {
        'password': data['password'],
    }
    update_user(ctx)
    if ctx.failed:
        return

    error = md.save(user)
    if error:
        ctx.set_error(error, status=500)
        return

    return user
