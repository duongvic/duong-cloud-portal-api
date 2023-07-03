#
# Copyright (c) 2020 FTI-CAS
#

from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args

from application import app
from application.api.v1 import base
from application.base import context
from application.managers import support_mgr
from application import models as md

LOCATION = 'default'
auth = base.auth


#####################################################################
# TICKETS
#####################################################################

def do_get_ticket(args):
    """
    Do get ticket.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get ticket',
        data=args)
    return base.exec_manager_func(support_mgr.get_ticket, ctx)


def do_get_tickets(args):
    """
    Do get multiple tickets.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get tickets',
        data=args)
    return base.exec_manager_func(support_mgr.get_tickets, ctx)


def do_create_ticket(args):
    """
    Do create ticket.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create ticket',
        data=args)
    return base.exec_manager_func_with_log(support_mgr.create_ticket, ctx,
                                           action=md.HistoryAction.CREATE_TICKET)


def do_update_ticket(args):
    """
    Do update ticket.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update ticket',
        data=args)
    return base.exec_manager_func_with_log(support_mgr.update_ticket, ctx,
                                           action=md.HistoryAction.UPDATE_TICKET)


def do_delete_ticket(args):
    """
    Do delete ticket.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete ticket',
        data=args)
    return base.exec_manager_func_with_log(support_mgr.delete_ticket, ctx,
                                           action=md.HistoryAction.DELETE_TICKET)


class Tickets(Resource):
    get_tickets_args = base.LIST_OBJECTS_ARGS

    create_ticket_args = {
        # TODO
    }

    @auth.login_required
    @use_args(get_tickets_args, location=LOCATION)
    def get(self, args):
        return do_get_tickets(args=args)

    @auth.login_required
    @use_args(create_ticket_args, location=LOCATION)
    def post(self, args):
        return do_create_ticket(args=args)


class Ticket(Resource):
    get_ticket_args = base.GET_OBJECT_ARGS

    update_ticket_args = {
        # TODO
    }

    delete_ticket_args = {
    }

    @auth.login_required
    @use_args(get_ticket_args, location=LOCATION)
    def get(self, args, ticket_id):
        args['ticket_id'] = ticket_id
        return do_get_ticket(args=args)

    @auth.login_required
    @use_args(update_ticket_args, location=LOCATION)
    def put(self, args, ticket_id):
        args['ticket_id'] = ticket_id
        return do_update_ticket(args=args)

    @auth.login_required
    @use_args(delete_ticket_args, location=LOCATION)
    def delete(self, args, ticket_id):
        args['ticket_id'] = ticket_id
        return do_delete_ticket(args=args)


#####################################################################
# SUPPORTS
#####################################################################

def do_get_support(args):
    """
    Do get support.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get support',
        data=args)
    return base.exec_manager_func(support_mgr.get_support, ctx)


def do_get_supports(args):
    """
    Do get multiple supports.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get supports',
        data=args)
    return base.exec_manager_func(support_mgr.get_supports, ctx)


def do_create_support(args):
    """
    Do create support.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create support',
        data=args)
    return base.exec_manager_func_with_log(support_mgr.create_support, ctx,
                                           action=md.HistoryAction.CREATE_SUPPORT)


def do_update_support(args):
    """
    Do update support.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update support',
        data=args)
    return base.exec_manager_func_with_log(support_mgr.update_support, ctx,
                                           action=md.HistoryAction.UPDATE_SUPPORT)


def do_delete_support(args):
    """
    Do delete support.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete support',
        data=args)
    return base.exec_manager_func_with_log(support_mgr.delete_support, ctx,
                                           action=md.HistoryAction.DELETE_SUPPORT)


class Supports(Resource):
    get_supports_args = base.LIST_OBJECTS_ARGS

    create_support_args = {
        # TODO
    }

    @auth.login_required
    @use_args(get_supports_args, location=LOCATION)
    def get(self, args):
        return do_get_supports(args=args)

    @auth.login_required
    @use_args(create_support_args, location=LOCATION)
    def post(self, args):
        return do_create_support(args=args)


class Support(Resource):
    get_support_args = base.GET_OBJECT_ARGS

    update_support_args = {
        # TODO
    }

    delete_support_args = {
    }

    @auth.login_required
    @use_args(get_support_args, location=LOCATION)
    def get(self, args, support_id):
        args['support_id'] = support_id
        return do_get_support(args=args)

    @auth.login_required
    @use_args(update_support_args, location=LOCATION)
    def put(self, args, support_id):
        args['support_id'] = support_id
        return do_update_support(args=args)

    @auth.login_required
    @use_args(delete_support_args, location=LOCATION)
    def delete(self, args, support_id):
        args['support_id'] = support_id
        return do_delete_support(args=args)
