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


network_os = product_types.get_product_type(
    context.create_admin_context(task='get os network type'),
    product_type=md.ProductType.NETWORK)

#####################################################################
# NETWORKS
#####################################################################


def do_get_network(args):
    """
    Get an network
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get network',
        data=args)
    return base.exec_manager_func(network_os.get_network, ctx)


def do_get_networks(args):
    """
    Get all networks of project
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get networks',
        data=args)
    return base.exec_manager_func(network_os.get_networks, ctx)


def do_create_network(args):
    """
    Create an new network
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create network',
        data=args)
    return base.exec_manager_func_with_log(network_os.create_network, ctx,
                                           action=md.HistoryAction.CREATE_NETWORK)


def do_update_network(args):
    """
    Update an existed network
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update network',
        data=args)
    return base.exec_manager_func_with_log(network_os.update_network, ctx,
                                           action=md.HistoryAction.UPDATE_NETWORK)


def do_delete_network(args):
    """
    Delete a network
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete network',
        data=args)
    return base.exec_manager_func_with_log(network_os.delete_network, ctx,
                                           action=md.HistoryAction.DELETE_NETWORK)


class Networks(Resource):
    get_networks_args = base.LIST_OBJECTS_ARGS

    create_network_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=True, validate=data_util.validate_name),
        'port_security_enabled': fields.Bool(required=False, missing=True),
        'mtu_size': fields.Int(required=False),
    }

    @auth.login_required
    @use_args(get_networks_args, location=LOCATION)
    def get(self, args):
        return do_get_networks(args=args)

    @auth.login_required
    @use_args(create_network_args, location=LOCATION)
    def post(self, args):
        return do_create_network(args=args)


class Network(Resource):
    get_network_args = base.GET_OBJECT_ARGS

    update_network_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=False, validate=data_util.validate_name),
        'port_security_enabled': fields.Bool(required=False, missing=True),
        'mtu_size': fields.Int(required=False),
    }

    delete_network_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_network_args, location=LOCATION)
    def get(self, args, network_id=None):
        args['network_id'] = network_id
        return do_get_network(args=args)

    @auth.login_required
    @use_args(update_network_args, location=LOCATION)
    def put(self, args, network_id=None):
        args['network_id'] = network_id
        return do_update_network(args=args)

    @auth.login_required
    @use_args(delete_network_args, location=LOCATION)
    def delete(self, args, network_id):
        args['network_id'] = network_id
        return do_delete_network(args=args)


#####################################################################
# SUBNETS
#####################################################################

def do_get_subnet(args):
    """
    Get an existed subnet
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get subnet',
        data=args)
    return base.exec_manager_func(network_os.get_subnet, ctx)


def do_get_subnets(args):
    """
    List all subnets
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get subnets',
        data=args)
    return base.exec_manager_func(network_os.get_subnets, ctx)


def do_create_subnet(args):
    """
    Create an new subnet
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create subnet',
        data=args)
    return base.exec_manager_func_with_log(network_os.create_subnet, ctx,
                                           action=md.HistoryAction.CREATE_SUBNET)


def do_update_subnet(args):
    """
    Update an existed subnet
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update subnet',
        data=args)
    return base.exec_manager_func_with_log(network_os.update_subnet, ctx,
                                           action=md.HistoryAction.UPDATE_SUBNET)


def do_delete_subnet(args):
    """
    Delete an existed subnet
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete subnet',
        data=args)
    return base.exec_manager_func_with_log(network_os.delete_subnet, ctx,
                                           action=md.HistoryAction.DELETE_SUBNET)


class Subnets(Resource):
    get_subnet_args = base.LIST_OBJECTS_ARGS

    create_subnet_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=False, validate=data_util.validate_name),
        'cidr': fields.Str(required=True, validate=data_util.validate_subnet),
        'enable_dhcp': fields.Bool(required=False, missing=False),
        'allocation_pools': fields.List(required=False, cls_or_instance=fields.Dict()),
        'ip_version': fields.Int(required=False, missing=4),
        'disable_gateway_ip': fields.Bool(required=False, missing=True),
        'gateway_ip': fields.Str(required=False, validate=data_util.validate_ip),
    }

    @auth.login_required
    @use_args(get_subnet_args, location=LOCATION)
    def get(self, args, network_id):
        args['network_id'] = network_id
        return do_get_subnets(args=args)

    @auth.login_required
    @use_args(create_subnet_args, location=LOCATION)
    def post(self, args, network_id):
        args['network_id'] = network_id
        return do_create_subnet(args=args)


class Subnet(Resource):
    get_subnet_args = base.GET_OBJECT_ARGS

    update_subnet_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=False),
        'allocation_pools': fields.List(required=False, cls_or_instance=fields.Dict()),
        'enable_dhcp': fields.Bool(required=False, missing=False),
        'disable_gateway_ip': fields.Bool(required=False, missing=False),
        'gateway_ip': fields.Str(required=False, validate=data_util.validate_ip),
    }

    delete_subnet_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_subnet_args, location=LOCATION)
    def get(self, args, subnet_id=None, network_id=None):
        args['subnet_id'] = subnet_id
        args['network_id'] = network_id
        return do_get_subnet(args=args)

    @auth.login_required
    @use_args(update_subnet_args, location=LOCATION)
    def put(self, args, subnet_id,  network_id=None):
        args['subnet_id'] = subnet_id
        args['network_id'] = network_id
        return do_update_subnet(args=args)

    @auth.login_required
    @use_args(delete_subnet_args, location=LOCATION)
    def delete(self, args, subnet_id, network_id):
        args['subnet_id'] = subnet_id
        args['network_id'] = network_id
        return do_delete_subnet(args=args)


#####################################################################
# Router
#####################################################################
def do_get_router(args):
    """
    Get an existed router
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get router',
        data=args)
    return base.exec_manager_func(network_os.get_router, ctx)


def do_get_routers(args):
    """
    List all routers
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get routers',
        data=args)
    return base.exec_manager_func(network_os.get_routers, ctx)


def do_create_router(args):
    """
    Create an new router
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create router',
        data=args)
    return base.exec_manager_func_with_log(network_os.create_router, ctx,
                                           action=md.HistoryAction.CREATE_ROUTER)


def do_update_router(args):
    """
    Update an existed router
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update router',
        data=args)
    return base.exec_manager_func_with_log(network_os.update_router, ctx,
                                           action=md.HistoryAction.UPDATE_ROUTER)


def do_delete_router(args):
    """
    Delete an existed router
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete router',
        data=args)
    return base.exec_manager_func_with_log(network_os.delete_router, ctx,
                                           action=md.HistoryAction.DELETE_ROUTER)


class Routers(Resource):
    get_router_args = base.LIST_OBJECTS_ARGS

    create_router_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=False),
        'ext_gateway_net_id': fields.Str(required=False),
        'enable_snat': fields.Bool(required=False, missing=False),
    }

    @auth.login_required
    @use_args(get_router_args, location=LOCATION)
    def get(self, args):
        return do_get_routers(args=args)

    @auth.login_required
    @use_args(create_router_args, location=LOCATION)
    def post(self, args):
        return do_create_router(args=args)


class Router(Resource):
    get_router_args = base.GET_OBJECT_ARGS

    update_router_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=False),
        'ext_gateway_net_id': fields.Str(required=False),
        'enable_snat': fields.Bool(required=False, missing=False),
    }

    delete_router_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_router_args, location=LOCATION)
    def get(self, args, router_id=None):
        args['router_id'] = router_id
        return do_get_router(args=args)

    @auth.login_required
    @use_args(update_router_args, location=LOCATION)
    def put(self, args, router_id):
        args['router_id'] = router_id
        return do_update_router(args=args)

    @auth.login_required
    @use_args(delete_router_args, location=LOCATION)
    def delete(self, args, router_id):
        args['router_id'] = router_id
        return do_delete_router(args=args)


#####################################################################
# Router
#####################################################################
def do_get_router_interface(args):
    """
    Get an existed router_interface
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get router_interface',
        data=args)
    return base.exec_manager_func(network_os.get_router_interface, ctx)


def do_get_router_interfaces(args):
    """
    List all router_interfaces
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get router_interfaces',
        data=args)
    return base.exec_manager_func(network_os.get_router_interfaces, ctx)


def do_create_router_interface(args):
    """
    Create an new router_interface
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create router_interface',
        data=args)
    return base.exec_manager_func_with_log(network_os.create_router_interface, ctx,
                                           action=md.HistoryAction.CREATE_ROUTER_INTERFACE)


def do_update_router_interface(args):
    """
    Update an existed router_interface
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update router_interface',
        data=args)
    return base.exec_manager_func_with_log(network_os.update_router_interface, ctx,
                                           action=md.HistoryAction.UPDATE_ROUTER_INTERFACE)


def do_delete_router_interface(args):
    """
    Delete an existed router_interface
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete router_interface',
        data=args)
    return base.exec_manager_func_with_log(network_os.delete_router_interface, ctx,
                                           action=md.HistoryAction.DELETE_ROUTER_INTERFACE)


class RouterInterfaces(Resource):
    get_router_interface_args = base.LIST_OBJECTS_ARGS

    create_router_interface_args = {
        **base.REGION_ARGS,
        'subnet_id': fields.Str(required=True),
        'port_id': fields.Str(required=True),
    }

    @auth.login_required
    @use_args(get_router_interface_args, location=LOCATION)
    def get(self, args):
        return do_get_router_interfaces(args=args)

    @auth.login_required
    @use_args(create_router_interface_args, location=LOCATION)
    def post(self, args):
        return do_create_router_interface(args=args)


class RouterInterface(Resource):
    get_router_interface_args = base.GET_OBJECT_ARGS

    update_router_interface_args = {
        **base.REGION_ARGS,
        'subnet_id': fields.Str(required=False),
        'port_id': fields.Str(required=False),
    }

    delete_router_interface_args = {
        **base.REGION_ARGS,
        'subnet_id': fields.Str(required=False),
        'port_id': fields.Str(required=False),
    }

    @auth.login_required
    @use_args(get_router_interface_args, location=LOCATION)
    def get(self, args, router_id=None):
        args['router_id'] = router_id
        return do_get_router_interface(args=args)

    @auth.login_required
    @use_args(update_router_interface_args, location=LOCATION)
    def put(self, args, router_id):
        args['router_id'] = router_id
        return do_update_router_interface(args=args)

    @auth.login_required
    @use_args(delete_router_interface_args, location=LOCATION)
    def delete(self, args, router_id):
        args['router_id'] = router_id
        return do_delete_router_interface(args=args)

#####################################################################
# COMPUTE SEC GROUP
#####################################################################

def do_get_secgroup(args):
    """
    Do get secgroup of compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get secgroup',
        data=args)
    return base.exec_manager_func(network_os.get_secgroup, ctx)

def do_get_secgroups(args):
    """
    Do get multiple secgroups of compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get sg rules',
        data=args)
    return base.exec_manager_func(network_os.get_secgroups, ctx)

def do_create_secgroup(args):
    """
    Do create sg rule for compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create sg rule',
        data=args)
    return base.exec_manager_func_with_log(network_os.create_secgroup, ctx,
                                           action=md.HistoryAction.CREATE_SECGROUP)

def do_update_secgroup(args):
    """
    Do update sg rule of compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update sg rule',
        data=args)
    return base.exec_manager_func_with_log(network_os.update_secgroup, ctx,
                                           action=md.HistoryAction.UPDATE_SECGROUP)

def do_delete_secgroup(args):
    """
    Do delete sg rule of compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete sg rule',
        data=args)
    return base.exec_manager_func_with_log(network_os.delete_secgroup, ctx,
                                           action=md.HistoryAction.DELETE_SECGROUP)


class ComputeSecgroups(Resource):
    get_secgroups_args = base.LIST_OBJECTS_ARGS

    create_secgroups_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=True),
        'description': fields.Str(required=False),
    }

    @auth.login_required
    @use_args(get_secgroups_args, location=LOCATION)
    def get(self, args):
        return do_get_secgroups(args=args)

    @auth.login_required
    @use_args(create_secgroups_args, location=LOCATION)
    def post(self, args):
        return do_create_secgroup(args=args)


class ComputeSecgroup(Resource):
    get_secgroup_args = base.GET_OBJECT_ARGS

    update_secgroup_args = {
        **base.REGION_ARGS,
        "name": fields.Str(required=False),
        "description": fields.Str(required=False),
    }

    delete_secgroup_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_secgroup_args, location=LOCATION)
    def get(self, args, secgroup_id):
        args['secgroup_id'] = secgroup_id
        return do_get_secgroup(args=args)

    @auth.login_required
    @use_args(update_secgroup_args, location=LOCATION)
    def put(self, args, secgroup_id):
        args['secgroup_id'] = secgroup_id
        return do_update_secgroup(args=args)

    @auth.login_required
    @use_args(delete_secgroup_args, location=LOCATION)
    def delete(self, args, secgroup_id):
        args['secgroup_id'] = secgroup_id
        return do_delete_secgroup(args=args)


#####################################################################
# COMPUTE SEC GROUP RULES
#####################################################################

def do_get_secgroup_rule(args):
    """
    Do get secgroup rule of compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get secgroup rule',
        data=args)
    return base.exec_manager_func(network_os.get_secgroup_rule, ctx)


def do_get_secgroup_rules(args):
    """
    Do get multiple secgroup rules of compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get secgroup rules',
        data=args)
    return base.exec_manager_func(network_os.get_secgroup_rules, ctx)


def do_create_secgroup_rule(args):
    """
    Do create sg rule for compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create secgroup rule',
        data=args)
    return base.exec_manager_func_with_log(network_os.create_secgroup_rule, ctx,
                                           action=md.HistoryAction.CREATE_SECGROUP_RULE)


def do_update_secgroup_rule(args):
    """
    Do update sg rule of compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update secgroup rule',
        data=args)
    return base.exec_manager_func_with_log(network_os.update_secgroup_rule, ctx,
                                           action=md.HistoryAction.UPDATE_SECGROUP_RULE)


def do_delete_secgroup_rule(args):
    """
    Do delete sg rule of compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete secgroup rule',
        data=args)
    return base.exec_manager_func_with_log(network_os.delete_secgroup_rule, ctx,
                                           action=md.HistoryAction.DELETE_SECGROUP_RULE)


class ComputeSecgroupRules(Resource):
    get_secgroup_rules_args = base.LIST_OBJECTS_ARGS

    create_secgroup_rule_args = {
        **base.REGION_ARGS,
        'direction': fields.Str(required=True),
        'ether_type': fields.Str(required=True),
        'port_range': fields.Str(required=True),
        'source_ip': fields.Str(required=True),
        'protocol': fields.Str(required=True),
    }

    @auth.login_required
    @use_args(get_secgroup_rules_args, location=LOCATION)
    def get(self, args, secgroup_id=None):
        args['secgroup_id'] = secgroup_id
        return do_get_secgroup_rules(args=args)

    @auth.login_required
    @use_args(create_secgroup_rule_args, location=LOCATION)
    def post(self, args, secgroup_id=None):
        args['secgroup_id'] = secgroup_id
        return do_create_secgroup_rule(args=args)


class ComputeSecgroupRule(Resource):
    get_secgroup_rule_args = base.GET_OBJECT_ARGS

    update_secgroup_rule_args = {
        **base.REGION_ARGS,
    }

    delete_secgroup_rule_args = {
        **base.REGION_ARGS,
    }

    @auth.login_required
    @use_args(get_secgroup_rule_args, location=LOCATION)
    def get(self, args, secgroup_id=None, rule_id=None):
        args['secgroup_id'] = secgroup_id
        args['rule_id'] = rule_id
        return do_get_secgroup_rule(args=args)

    @auth.login_required
    @use_args(update_secgroup_rule_args, location=LOCATION)
    def put(self, args, secgroup_id=None, rule_id=None):
        args['secgroup_id'] = secgroup_id
        args['rule_id'] = rule_id
        return do_update_secgroup_rule(args=args)

    @auth.login_required
    @use_args(delete_secgroup_rule_args, location=LOCATION)
    def delete(self, args, secgroup_id=None, rule_id=None):
        args['secgroup_id'] = secgroup_id
        args['rule_id'] = rule_id
        return do_delete_secgroup_rule(args=args)

