#
# Copyright (c) 2020 FTI-CAS
#

from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args

from application import app
from application.api.v1 import base
from application.base import context, common
from application import product_types
from application import models as md
from application.utils import data_util

LOCATION = 'default'
auth = base.auth

lbaas_os = product_types.get_product_type(
    context.create_admin_context(task='get os lbaas type'),
    product_type=md.ProductType.LBAAS)


#####################################################################
# LB
#####################################################################
def do_get_lb(args):
    """
    Get a lb
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get lb',
        data=args)
    return base.exec_manager_func(lbaas_os.get_lb, ctx)


def do_get_lbs(args):
    """
    Get all lbs of user
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get lbs',
        data=args)
    return base.exec_manager_func(lbaas_os.get_lbs, ctx)


def do_create_lb(args):
    """
    Create a new lb
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create lb',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.create_lb, ctx,
                                           action=md.HistoryAction.CREATE_LB)


def do_update_lb(args):
    """
    Update a lb
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update lb',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.update_lb, ctx,
                                           action=md.HistoryAction.UPDATE_LB)


def do_delete_lb(args):
    """
    Delete a lb
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete lb',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.delete_lb, ctx,
                                           action=md.HistoryAction.DELETE_LB)


class LBs(Resource):
    get_lbs_args = {
        **base.LIST_OBJECTS_ARGS,
        'filters': fields.List(fields.Dict(), required=False, missing={})
    }

    create_lb_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=True, validate=data_util.validate_name),
        'description': fields.Str(required=False),
        'subnet_id': fields.Str(required=True, validate=data_util.validate_subnet),
        'vip_address': fields.Str(required=False, validate=data_util.validate_ip),
        'flavor_id': fields.Str(required=False),
        'tags': fields.List(fields.Str, required=False),
        'wait': fields.Bool(required=False, missing=False),
    }

    @auth.login_required
    @use_args(get_lbs_args, location=LOCATION)
    def get(self, args):
        return do_get_lbs(args=args)

    @auth.login_required
    @use_args(create_lb_args, location=LOCATION)
    def post(self, args):
        return do_create_lb(args=args)


class LB(Resource):
    get_lb_args = {
        **base.LIST_OBJECTS_ARGS,
        'filters': fields.List(fields.Dict, required=False)
    }

    update_lb_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=False, validate=data_util.validate_name),
        'description': fields.Str(required=False),
        'tags': fields.List(fields.Str, required=False)
    }

    delete_lb_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_lb_args, location=LOCATION)
    def get(self, args, lb_id):
        args['lb_id'] = lb_id
        return do_get_lb(args=args)

    @auth.login_required
    @use_args(update_lb_args, location=LOCATION)
    def put(self, args, lb_id):
        args['lb_id'] = lb_id
        return do_update_lb(args=args)

    @auth.login_required
    @use_args(delete_lb_args, location=LOCATION)
    def delete(self, args, lb_id):
        args['lb_id'] = lb_id
        return do_delete_lb(args=args)


#####################################################################
# Listener
#####################################################################
def do_get_listener(args):
    """
    Get a listener
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get listener',
        data=args)
    return base.exec_manager_func(lbaas_os.get_listener, ctx)


def do_get_listeners(args):
    """
    Get all listeners of user
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get listeners',
        data=args)
    return base.exec_manager_func(lbaas_os.get_listeners, ctx)


def do_create_listener(args):
    """
    Create a new listener
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create listener',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.create_listener, ctx,
                                           action=md.HistoryAction.CREATE_LISTENER)


def do_update_listener(args):
    """
    Update a listener
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update listener',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.update_listener, ctx,
                                           action=md.HistoryAction.UPDATE_LISTENER)


def do_delete_listener(args):
    """
    Delete a listener
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create listener',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.delete_listener, ctx,
                                           action=md.HistoryAction.DELETE_LISTENER)


class Listeners(Resource):
    get_listeners_args = {
        **base.LIST_OBJECTS_ARGS,
    }

    create_listener_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=True, validate=data_util.validate_name),
        'description': fields.Str(required=False),
        'protocol': fields.Str(required=True,
                               validate=validate.OneOf(['HTTP', 'HTTPS', 'PROXY',
                                                        'PROXYV2', 'SCTP', 'TCP',
                                                        'UDP'])),
        'port': fields.Int(required=True),
        'lb_id': fields.Str(required=True),
        'timeout_client_data': fields.Int(required=False),
        'timeout_member_data': fields.Int(required=False),
        'timeout_member_connect': fields.Int(required=False),
        'timeout_tcp_inspect': fields.Int(required=False),
        'connection_limit': fields.Int(required=False),
        'tags': fields.List(fields.Str, required=False),
        'wait': fields.Bool(required=False, missing=False)
    }

    @auth.login_required
    @use_args(get_listeners_args, location=LOCATION)
    def get(self, args):
        return do_get_listeners(args=args)

    @auth.login_required
    @use_args(create_listener_args, location=LOCATION)
    def post(self, args):
        return do_create_listener(args=args)


class Listener(Resource):
    get_listener_args = {
        **base.LIST_OBJECTS_ARGS
    }

    update_listener_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=True, validate=data_util.validate_name),
        'description': fields.Str(required=False),
        'connection_limit': fields.Int(required=False),
        'tags': fields.List(fields.Str, required=False)
    }

    delete_listener_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_listener_args, location=LOCATION)
    def get(self, args, listener_id):
        args['listener_id'] = listener_id
        return do_get_listener(args=args)

    @auth.login_required
    @use_args(update_listener_args, location=LOCATION)
    def put(self, args, listener_id):
        args['listener_id'] = listener_id
        return do_update_listener(args=args)

    @auth.login_required
    @use_args(delete_listener_args, location=LOCATION)
    def delete(self, args, listener_id):
        args['listener_id'] = listener_id
        return do_delete_listener(args=args)


#####################################################################
# POOL
#####################################################################
def do_get_pool(args):
    """
    Get a pool
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get pool',
        data=args)
    return base.exec_manager_func(lbaas_os.get_pool, ctx)


def do_get_pools(args):
    """
    Get all pools of user
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get pools',
        data=args)
    return base.exec_manager_func(lbaas_os.get_pools, ctx)


def do_create_pool(args):
    """
    Create a new pool
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create pool',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.create_pool, ctx,
                                           action=md.HistoryAction.CREATE_POOL)


def do_update_pool(args):
    """
    Update a pool
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update pool',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.update_pool, ctx,
                                           action=md.HistoryAction.UPDATE_POOL)


def do_delete_pool(args):
    """
    Delete a pool
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create pool',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.delete_pool, ctx,
                                           action=md.HistoryAction.DELETE_POOL)


class Pools(Resource):
    get_pools_args = {
        'user_id': fields.Str(required=False),
        **base.LIST_OBJECTS_ARGS
    }

    create_pool_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=True, validate=data_util.validate_name),
        'description': fields.Str(required=False),
        'protocol': fields.Str(required=True, validate=data_util.validate_protocol),
        'lb_algorithm': fields.Str(required=True,
                                   validate=validate.OneOf(["LEAST_CONNECTIONS", "ROUND_ROBIN",
                                                            "SOURCE_IP", "SOURCE_IP_PORT"])),
        'listener_id': fields.Str(required=False),
        'lb_id': fields.Str(required=False),
        'session_persistence': fields.Str(required=False),
        'tags': fields.List(fields.Str, required=False),
        'wait': fields.Bool(required=False, missing=False)
    }

    @auth.login_required
    @use_args(get_pools_args, location=LOCATION)
    def get(self, args):
        return do_get_pools(args=args)

    @auth.login_required
    @use_args(create_pool_args, location=LOCATION)
    def post(self, args):
        return do_create_pool(args=args)


class Pool(Resource):
    get_pool_args = {
        **base.LIST_OBJECTS_ARGS
    }

    update_pool_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=True),
        'description': fields.Str(required=False),
        'lb_algorithm': fields.Str(required=True,
                                   validate=validate.OneOf(["LEAST_CONNECTIONS", "ROUND_ROBIN",
                                                            "SOURCE_IP", "SOURCE_IP_PORT"])),
        'session_persistence': fields.Str(required=False),
        'tags': fields.List(fields.Str, required=False)
    }

    delete_pool_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_pool_args, location=LOCATION)
    def get(self, args, pool_id):
        args['pool_id'] = pool_id
        return do_get_pool(args=args)

    @auth.login_required
    @use_args(update_pool_args, location=LOCATION)
    def put(self, args, pool_id):
        args['pool_id'] = pool_id
        return do_update_pool(args=args)

    @auth.login_required
    @use_args(delete_pool_args, location=LOCATION)
    def delete(self, args, pool_id):
        args['pool_id'] = pool_id
        return do_delete_pool(args=args)


#####################################################################
# POOL MEMBER
#####################################################################
def do_get_pool_member(args):
    """
    Get a pool_member
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get pool_member',
        data=args)
    return base.exec_manager_func(lbaas_os.get_pool_member, ctx)


def do_get_pool_members(args):
    """
    Get all pool_members of user
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get pool_members',
        data=args)
    return base.exec_manager_func(lbaas_os.get_pool_members, ctx)


def do_create_pool_member(args):
    """
    Create a new pool_member
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create pool_member',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.create_pool_member, ctx,
                                           action=md.HistoryAction.CREATE_POOL_MEMBER)


def do_update_pool_member(args):
    """
    Update a pool_member
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update pool_member',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.update_pool_member, ctx,
                                           action=md.HistoryAction.UPDATE_POOL_MEMBER)


def do_delete_pool_member(args):
    """
    Delete a pool_member
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create pool_member',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.delete_pool_member, ctx,
                                           action=md.HistoryAction.DELETE_POOL_MEMBER)


class PoolMembers(Resource):
    get_pool_members_args = {
        **base.LIST_OBJECTS_ARGS,
    }

    create_pool_member_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=True, validate=data_util.validate_name),
        'address': fields.Str(required=True, validate=data_util.validate_ip),
        'port': fields.Int(required=True, validate=validate.Range(min=1, max=65535)),
        'weight': fields.Int(required=False, missing=1),
        'monitor_address': fields.Str(required=False, validate=data_util.validate_ip),
        'monitor_port': fields.Int(required=False, validate=validate.Range(min=1, max=65535)),
        'tags': fields.List(fields.Str, required=False),
        'wait': fields.Bool(required=False, missing=False)
    }

    @auth.login_required
    @use_args(get_pool_members_args, location=LOCATION)
    def get(self, args, pool_id):
        args['pool_id'] = pool_id
        return do_get_pool_members(args=args)

    @auth.login_required
    @use_args(create_pool_member_args, location=LOCATION)
    def post(self, args, pool_id):
        args['pool_id'] = pool_id
        return do_create_pool_member(args=args)


class PoolMember(Resource):
    get_pool_member_args = {
        **base.LIST_OBJECTS_ARGS
    }

    update_pool_member_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=True, validate=data_util.validate_name),
        'weight': fields.Int(required=False, missing=1),
        'monitor_address': fields.Str(required=False, validate=data_util.validate_ip),
        'monitor_port': fields.Int(required=False, validate=validate.Range(min=1, max=65535)),
        'tags': fields.List(fields.Str, required=False)
    }

    delete_pool_member_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_pool_member_args, location=LOCATION)
    def get(self, args, member_id, pool_id):
        args['member_id'] = member_id
        args['pool_id'] = pool_id
        return do_get_pool_member(args=args)

    @auth.login_required
    @use_args(update_pool_member_args, location=LOCATION)
    def put(self, args, member_id, pool_id):
        args['member_id'] = member_id
        args['pool_id'] = pool_id
        return do_update_pool_member(args=args)

    @auth.login_required
    @use_args(delete_pool_member_args, location=LOCATION)
    def delete(self, args, member_id, pool_id):
        args['member_id'] = member_id
        args['pool_id'] = pool_id
        return do_delete_pool_member(args=args)


#####################################################################
# Monitor
#####################################################################
def do_get_monitor(args):
    """
    Get a monitor
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get monitor',
        data=args)
    return base.exec_manager_func(lbaas_os.get_monitor, ctx)


def do_get_monitors(args):
    """
    Get all monitors of user
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get monitors',
        data=args)
    return base.exec_manager_func(lbaas_os.get_monitors, ctx)


def do_create_monitor(args):
    """
    Create a new monitor
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create monitor',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.create_monitor, ctx,
                                           action=md.HistoryAction.CREATE_MONITOR)


def do_update_monitor(args):
    """
    Update a monitor
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update monitor',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.update_monitor, ctx,
                                           action=md.HistoryAction.UPDATE_MONITOR)


def do_delete_monitor(args):
    """
    Delete a monitor
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create monitor',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.delete_monitor, ctx,
                                           action=md.HistoryAction.DELETE_MONITOR)


class Monitors(Resource):
    get_monitors_args = {
        'user_id': fields.Str(required=False),
        **base.LIST_OBJECTS_ARGS
    }

    create_monitor_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=True),
        'pool_id': fields.Str(required=True),
        'delay': fields.Int(required=False, missing=10),
        'timeout': fields.Int(required=False, missing=10),
        'http_method': fields.Str(required=False, missing='GET', validate=data_util.validate_http_method),
        'max_retries': fields.Int(required=False, missing=3, validate=validate.Range(min=1, max=10)),
        'max_retries_down': fields.Str(required=False, missing=3, validate=validate.Range(min=1, max=10)),
        'url_path': fields.Str(required=False, missing="/", validate=validate.Regexp('^[/]')),
        'expected_codes': fields.Str(required=False, missing='200',
                                     validate=validate.OneOf(['201', '202', '203', '204'])),
        'tags': fields.List(fields.Str, required=False),
        'wait': fields.Bool(required=False, missing=False)
    }

    @auth.login_required
    @use_args(get_monitors_args, location=LOCATION)
    def get(self, args):
        return do_get_monitors(args=args)

    @auth.login_required
    @use_args(create_monitor_args, location=LOCATION)
    def post(self, args):
        return do_create_monitor(args=args)


class Monitor(Resource):
    get_monitor_args = {
        **base.LIST_OBJECTS_ARGS
    }

    update_monitor_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=False),
        'delay': fields.Int(required=False),
        'timeout': fields.Int(required=False),
        'http_method': fields.Str(required=False, validate=data_util.validate_http_method),
        'max_retries': fields.Int(required=False, validate=validate.Range(min=1, max=10)),
        'max_retries_down': fields.Str(required=False, validate=validate.Range(min=1, max=10)),
        'url_path': fields.Str(required=False, validate=validate.Regexp('^[/]')),
        'expected_codes': fields.Str(required=False, validate=validate.OneOf(['201', '202', '203', '204'])),
        'tags': fields.List(fields.Str, required=False),
    }

    delete_monitor_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_monitor_args, location=LOCATION)
    def get(self, args, monitor_id):
        args['monitor_id'] = monitor_id
        return do_get_monitor(args=args)

    @auth.login_required
    @use_args(update_monitor_args, location=LOCATION)
    def put(self, args, monitor_id):
        args['monitor_id'] = monitor_id
        return do_update_monitor(args=args)

    @auth.login_required
    @use_args(delete_monitor_args, location=LOCATION)
    def delete(self, args, monitor_id):
        args['monitor_id'] = monitor_id
        return do_delete_monitor(args=args)


#####################################################################
# l7policy
#####################################################################
def do_get_l7policy(args):
    """
    Get a l7policy
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get l7policy',
        data=args)
    return base.exec_manager_func(lbaas_os.get_l7policy, ctx)


def do_get_l7policies(args):
    """
    Get all l7policys of user
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get l7policys',
        data=args)
    return base.exec_manager_func(lbaas_os.get_l7policies, ctx)


def do_create_l7policy(args):
    """
    Create a new l7policy
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create l7policy',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.create_l7policy, ctx,
                                           action=md.HistoryAction.CREATE_L7POLICY)


def do_update_l7policy(args):
    """
    Update a l7policy
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update l7policy',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.update_l7policy, ctx,
                                           action=md.HistoryAction.UPDATE_L7POLICY)


def do_delete_l7policy(args):
    """
    Delete a l7policy
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create l7policy',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.delete_l7policy, ctx,
                                           action=md.HistoryAction.DELETE_L7POLICY)


class L7policies(Resource):
    get_l7policies_args = {
        **base.LIST_OBJECTS_ARGS
    }

    create_l7policy_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=True, validate=data_util.validate_name),
        'description': fields.Str(required=False),
        'action': fields.Str(required=True, validate=validate.OneOf(['REDIRECT_PREFIX', 'REDIRECT_TO_POOL',
                                                                     'REDIRECT_TO_URL', 'REJECT'])),
        'listener_id': fields.Str(required=False),
        'position': fields.Int(required=True),
        'redirect_http_code': fields.Str(required=False,
                                         validate=validate.Range(min=301, max=308)),
        'redirect_pool_id': fields.Str(required=False),
        'redirect_prefix': fields.Str(required=False),
        'redirect_url': fields.Str(required=False, validate=data_util.validata_url),
        'tags': fields.List(fields.Str, required=False),
        'wait': fields.Bool(required=False, missing=False)
    }

    @auth.login_required
    @use_args(get_l7policies_args, location=LOCATION)
    def get(self, args):
        return do_get_l7policies(args=args)

    @auth.login_required
    @use_args(create_l7policy_args, location=LOCATION)
    def post(self, args):
        return do_create_l7policy(args=args)


class L7policy(Resource):
    get_l7policy_args = {
        **base.LIST_OBJECTS_ARGS
    }

    update_l7policy_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=True, validate=data_util.validate_name),
        'description': fields.Str(required=False),
        'action': fields.Str(required=True),
        'position': fields.Int(required=True),
        'redirect_http_code': fields.Str(required=False,
                                         validate=validate.Range(min=301, max=308)),
        'redirect_pool_id': fields.Str(required=False),
        'redirect_prefix': fields.Str(required=False),
        'redirect_url': fields.Str(required=False, validate=data_util.validata_url),
        'tags': fields.List(fields.Str, required=False),
    }

    delete_l7policy_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_l7policy_args, location=LOCATION)
    def get(self, args, l7policy_id):
        args['l7policy_id'] = l7policy_id
        return do_get_l7policy(args=args)

    @auth.login_required
    @use_args(update_l7policy_args, location=LOCATION)
    def put(self, args, l7policy_id):
        args['l7policy_id'] = l7policy_id
        return do_update_l7policy(args=args)

    @auth.login_required
    @use_args(delete_l7policy_args, location=LOCATION)
    def delete(self, args, l7policy_id):
        args['l7policy_id'] = l7policy_id
        return do_delete_l7policy(args=args)


#####################################################################
# l7rule
#####################################################################
def do_get_l7rule(args):
    """
    Get a l7rule
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get l7rule',
        data=args)
    return base.exec_manager_func(lbaas_os.get_l7rule, ctx)


def do_get_l7rules(args):
    """
    Get all l7rules of user
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get l7rules',
        data=args)
    return base.exec_manager_func(lbaas_os.get_l7rules, ctx)


def do_create_l7rule(args):
    """
    Create a new l7rule
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create l7rule',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.create_l7rule, ctx,
                                           action=md.HistoryAction.CREATE_L7POLICY_RULE)


def do_update_l7rule(args):
    """
    Update a l7rule
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update l7rule',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.update_l7rule, ctx,
                                           action=md.HistoryAction.UPDATE_L7POLICY_RULE)


def do_delete_l7rule(args):
    """
    Delete a l7rule
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create l7rule',
        data=args)
    return base.exec_manager_func_with_log(lbaas_os.delete_l7rule, ctx,
                                           action=md.HistoryAction.DELETE_L7POLICY_RULE)


class L7Rules(Resource):
    get_l7rules_args = {
        **base.LIST_OBJECTS_ARGS
    }

    create_l7rule_args = {
        **base.REGION_ARGS,
        'compare_type': fields.Str(required=True,
                                   validate=validate.OneOf(['CONTAINS', 'ENDS_WITH',
                                                            'EQUAL_TO', 'REGEX', 'STARTS_WITH'])),
        'type': fields.Str(required=True,
                   validate=validate.OneOf(['COOKIE', 'FILE_TYPE', 'HEADER', 'HOST_NAME',
                                            'PATH', 'SSL_CONN_HAS_CERT', 'SSL_VERIFY_RESULT',
                                            'SSL_DN_FIELD'])),
        'value': fields.Str(required=True),
        'invert': fields.Bool(required=False, missing=False),
        'tags': fields.List(fields.Str, required=False),
        'wait': fields.Bool(required=False, missing=False)
    }

    @auth.login_required
    @use_args(get_l7rules_args, location=LOCATION)
    def get(self, args, l7policy_id):
        args['l7policy_id'] = l7policy_id
        return do_get_l7rules(args=args)

    @auth.login_required
    @use_args(create_l7rule_args, location=LOCATION)
    def post(self, args, l7policy_id):
        args['l7policy_id'] = l7policy_id
        return do_create_l7rule(args=args)


class L7Rule(Resource):
    get_l7rule_args = {
        **base.LIST_OBJECTS_ARGS
    }

    update_l7rule_args = {
        **base.REGION_ARGS,
        'compare_type': fields.Str(required=True,
                                   validate=validate.OneOf(['CONTAINS', 'ENDS_WITH',
                                                            'EQUAL_TO', 'REGEX', 'STARTS_WITH'])),
        'type': fields.Str(required=True,
                           validate=validate.OneOf(['COOKIE', 'FILE_TYPE', 'HEADER', 'HOST_NAME',
                                                    'PATH', 'SSL_CONN_HAS_CERT', 'SSL_VERIFY_RESULT',
                                                    'SSL_DN_FIELD'])),
        'value': fields.Str(required=True),
        'invert': fields.Bool(required=False, missing=False),
        'tags': fields.List(fields.Str, required=False),
    }

    delete_l7rule_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_l7rule_args, location=LOCATION)
    def get(self, args, l7rule_id, l7policy_id):
        args['l7rule_id'] = l7rule_id
        args['l7policy_id'] = l7policy_id
        return do_get_l7rule(args=args)

    @auth.login_required
    @use_args(update_l7rule_args, location=LOCATION)
    def put(self, args, l7rule_id, l7policy_id):
        args['l7rule_id'] = l7rule_id
        args['l7policy_id'] = l7policy_id
        return do_update_l7rule(args=args)

    @auth.login_required
    @use_args(delete_l7rule_args, location=LOCATION)
    def delete(self, args, l7rule_id, l7policy_id):
        args['l7rule_id'] = l7rule_id
        args['l7policy_id'] = l7policy_id
        return do_delete_l7rule(args=args)
