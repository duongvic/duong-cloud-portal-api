#
# Copyright (c) 2020 FTI-CAS
#

from flask import _request_ctx_stack, request as flask_request
from werkzeug.local import LocalProxy

import application
from application import app
from application.base import errors
from application import models as md

LOG = app.logger

# A proxy for the current context
current_context = LocalProxy(lambda: _get_context())


def _get_context():
    return getattr(_request_ctx_stack.top, 'context', None)


class Context(object):
    def __init__(self, task,
                 request_user=None, target_user=None,
                 check_token=True,
                 request=None, response=None,
                 data=None, status=None,
                 db_session=None):
        self.task = task
        self.request_user = request_user
        self.target_user = target_user
        self.check_token = check_token
        self.request = request
        self.response = response
        self.data = data
        self.status = status
        self.db_session = db_session or md.get_session()
        self.error = None
        self.warning = None
        self.log_args = dict(data) if data else {}

    def copy(self, task=None, data=None):
        return Context(task=task if task is not None else self.task,
                       request_user=self.request_user,
                       target_user=self.target_user,
                       data=data if data is not None else self.data,
                       request=self.request,
                       db_session=self.db_session)

    @property
    def succeed(self):
        return False if self.error else True

    @property
    def failed(self):
        return True if self.error else False

    def add_response(self, key, value):
        if not self.response:
            self.response = {}
        self.response[key] = value

    def get_response_value(self, key):
        if not self.response:
            return None
        return self.response.get(key)

    def clear_response(self):
        self.response = None

    def set_error(self, error, cause=None, status=500, clear=True):
        if clear:
            self.clear_error()
        if isinstance(error, str):
            error = errors.Error(message=error, cause=cause)
        self.add_error(error)
        self.status = status

    def add_error(self, error):
        if not isinstance(error, list):
            error = [error]
        all_errors = self.error
        if not isinstance(all_errors, list):
            all_errors = [all_errors] if all_errors else []
        all_errors.extend(error)
        self.error = all_errors if len(all_errors) > 1 else all_errors[0]

    def clear_error(self):
        self.error = None
        self.status = None

    def copy_error(self, ctx):
        self.set_error(ctx.error, status=ctx.status)

    def set_warning(self, warning, cause=None, clear=True):
        if clear:
            self.clear_warning()
        if isinstance(warning, str):
            warning = errors.Error(message=warning, cause=cause)
        self.add_warning(warning)

    def add_warning(self, warning):
        if not isinstance(warning, list):
            warning = [warning]
        all_warnings = self.warning
        if not isinstance(all_warnings, list):
            all_warnings = [all_warnings] if all_warnings else []
        all_warnings.extend(warning)
        self.warning = all_warnings if len(all_warnings) > 1 else all_warnings[0]

    def clear_warning(self):
        self.warning = None

    def copy_warning(self, ctx):
        self.add_warning(ctx.warning)

    def error_json(self):
        error = self.error
        if isinstance(error, errors.Error):
            return error.to_json()
        if isinstance(error, list):
            return [item.to_json() for item in error]
        return None

    def warning_json(self):
        warning = self.warning
        if isinstance(warning, errors.Error):
            return warning.to_json()
        if isinstance(warning, list):
            return [item.to_json() for item in warning]
        return None

    @property
    def is_cross_user_request(self):
        request_id = self.request_user.id if self.request_user else None
        target_id = self.target_user.id if self.target_user else None
        return request_id != target_id

    @property
    def is_self_request(self):
        return not self.is_cross_user_request

    @property
    def is_user_request(self):
        if self.request_user:
            return self.check_request_user_role(md.UserRole.USER)
        return True

    @property
    def is_super_admin_request(self):
        if self.request_user:
            return self.check_request_user_role(md.UserRole.ADMIN)
        return False

    @property
    def is_admin_request(self):
        if self.request_user:
            return self.check_request_user_role(md.UserRole.admin_all())
        return False

    @property
    def is_admin_sale_request(self):
        return self.check_request_user_role(md.UserRole.ADMIN_SALE)

    @property
    def is_admin_it_request(self):
        return self.check_request_user_role(md.UserRole.ADMIN_IT)

    def check_request_user_role(self, roles):
        if self.request_user:
            return self._check_roles(self.request_user.role, roles)
        return None

    def check_target_user_role(self, roles):
        if self.target_user:
            return self._check_roles(self.target_user.role, roles)
        return None

    def _check_roles(self, roles, expected_roles):
        _roles = roles.split(',')
        if isinstance(expected_roles, str):
            return expected_roles in _roles
        else:
            for role in _roles:
                if role in expected_roles:
                    return True
            return False

    def compare_roles(self):
        return md.UserRole.compare(self.request_user.role, self.target_user.role)

    def close_db_session(self):
        session = self.db_session
        if session:
            session.close()
            self.db_session = None

    def expunge(self):
        session = self.db_session
        if session:
            session.expunge(self.request_user)
            session.expunge(self.target_user)

    def load_users(self):
        data = self.data or {}
        from application import api
        current_user = api.api_auth.current_user()

        if self.check_token:
            user_id = getattr(current_user, 'id', None)
            if not user_id:
                self.set_error(errors.USER_NOT_AUTHORIZED, status=401)
                return
            self.request_user = md.User.query.get(user_id)
            if not self.request_user:
                self.set_error(errors.USER_NOT_AUTHORIZED, status=401)
                return

        # Target user
        target_user = (self.target_user or data.get('user_id') or
                       data.get('user_name') or self.request_user)
        self.target_user = md.load_user(target_user) if target_user else None

        # Request user
        request_user = self.request_user or getattr(current_user, 'id', None) or self.target_user
        self.request_user = md.load_user(request_user) if request_user else None

        # A lower user role cannot access higher user data
        if self.request_user and self.target_user:
            if self.is_cross_user_request and self.compare_roles() <= 0:
                self.set_error(errors.USER_ACTION_NOT_ALLOWED, status=403)
                return


def create_context(task,
                   request_user=None, target_user=None,
                   check_token=True,
                   request=flask_request, response=None,
                   data=None, status=None,
                   db_session=None):
    """
    Create context from arguments.
    :param task:
    :param request_user:
    :param target_user:
    :param check_token:
    :param request:
    :param response:
    :param data:
    :param status:
    :param db_session:
    :return:
    """
    ctx = Context(task=task,
                  request_user=request_user, target_user=target_user,
                  check_token=check_token,
                  request=request, response=response,
                  data=data, status=status,
                  db_session=db_session)
    ctx.load_users()
    LOG.debug('TASK: ' + ctx.task)

    # Push the context to the request context
    ctx_stack_top = _request_ctx_stack.top
    ctx_stack_top.context = ctx

    return ctx


def create_admin_context(task,
                         target_user=None,
                         request=flask_request,
                         response=None,
                         data=None,
                         status=None,
                         db_session=None):
    """
    Create admin context for tasks.
    :param task:
    :param target_user:
    :param request:
    :param response:
    :param data:
    :param status:
    :param db_session:
    :return:
    """
    ctx = Context(task=task,
                  data=data,
                  request_user=application.admin,
                  target_user=target_user,
                  check_token=False,
                  request=request,
                  response=response,
                  status=status,
                  db_session=db_session)

    # Load target user
    if ctx.target_user:
        ctx.target_user = md.load_user(ctx.target_user)
    LOG.debug('TASK: ' + task)
    return ctx
