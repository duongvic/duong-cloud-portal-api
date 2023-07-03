#
# Copyright (c) 2020 FTI-CAS
#

from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args

from application import app
from application.api.v1 import base
from application.base import context
from application.managers import task_mgr

LOCATION = 'default'
auth = base.auth


#####################################################################
# TASKS
#####################################################################

def do_get_task(args):
    """
    Do get task.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get task',
        data=args)
    return base.exec_manager_func(task_mgr.get_task, ctx)


def do_get_tasks(args):
    """
    Do get multiple tasks.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get tasks',
        data=args)
    return base.exec_manager_func(task_mgr.get_tasks, ctx)


def do_create_task(args):
    """
    Do create task.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create task',
        data=args)
    return base.exec_manager_func(task_mgr.create_task, ctx)


def do_update_task(args):
    """
    Do update task.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update task',
        data=args)
    return base.exec_manager_func(task_mgr.update_task, ctx)


def do_delete_task(args):
    """
    Do delete task.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete task',
        data=args)
    return base.exec_manager_func(task_mgr.delete_task, ctx)


class Tasks(Resource):
    get_tasks_args = base.LIST_OBJECTS_ARGS

    create_task_args = {
        # TODO
    }

    @auth.login_required
    @use_args(get_tasks_args, location=LOCATION)
    def get(self, args):
        return do_get_tasks(args=args)

    @auth.login_required
    @use_args(create_task_args, location=LOCATION)
    def post(self, args):
        return do_create_task(args=args)


class Task(Resource):
    get_task_args = base.GET_OBJECT_ARGS

    update_task_args = {
        # TODO
    }

    delete_task_args = {
    }

    @auth.login_required
    @use_args(get_task_args, location=LOCATION)
    def get(self, args, task_id):
        args['task_id'] = task_id
        return do_get_task(args=args)

    @auth.login_required
    @use_args(update_task_args, location=LOCATION)
    def put(self, args, task_id):
        args['task_id'] = task_id
        return do_update_task(args=args)

    @auth.login_required
    @use_args(delete_task_args, location=LOCATION)
    def delete(self, args, task_id):
        args['task_id'] = task_id
        return do_delete_task(args=args)
