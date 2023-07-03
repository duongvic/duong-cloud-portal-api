#
# Copyright (c) 2020 FTI-CAS
#

from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args

from application import app
from application.api.v1 import base
from application.base import context
from application import models as md
from application import product_types
from application.utils import hash_util

LOCATION = 'default'
auth = base.auth


compute_os = product_types.get_product_type(
    context.create_admin_context(task='get os compute type'),
    product_type=md.ProductType.COMPUTE)


#####################################################################
# COMPUTE CRUD
#####################################################################

def do_get_compute(args):
    """
    Do get compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get compute',
        data=args)
    return base.exec_manager_func(compute_os.get_compute, ctx)


def do_get_computes(args):
    """
    Do get multiple computes.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get computes',
        data=args)
    return base.exec_manager_func(compute_os.get_computes, ctx)


def do_create_compute(args):
    """
    Do create compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create compute',
        data=args)

    def _log_func(ctx, history):
        data = base.default_log_filter(ctx)
        # Remove some sensitive info
        if 'ssh_key' in data:
            data['ssh_key'] = '***'
        history.contents.update(data)

    return base.exec_manager_func_with_log(compute_os.create_compute, ctx,
                                           action=md.HistoryAction.CREATE_COMPUTE,
                                           log_func=_log_func)


def do_update_compute(args):
    """
    Do update compute.
    :param args:
    :return:
        """
    ctx = context.create_context(
        task='update compute',
        data=args)

    def _log_func(ctx, history):
        data = base.default_log_filter(ctx)
        # Remove some sensitive info
        if 'ssh_key' in data:
            data['ssh_key'] = '***'
        history.contents.update(data)

    return base.exec_manager_func_with_log(compute_os.update_compute, ctx,
                                           action=md.HistoryAction.UPDATE_COMPUTE,
                                           log_func=_log_func)


def do_delete_compute(args):
    """
    Do delete compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete compute',
        data=args)
    return base.exec_manager_func_with_log(compute_os.delete_compute, ctx,
                                           action=md.HistoryAction.DELETE_COMPUTE)


class Computes(Resource):
    get_computes_args = base.LIST_OBJECTS_ARGS

    create_compute_args = {
        'order_id': fields.Int(required=False),  # Either order_id or recreate_compute_id must be passed
        'recreate_compute_id': fields.Int(required=False),  # In case no order_id passed
        'name': fields.Str(required=False),
        'description': fields.Str(required=False),
        'notify_when_created': fields.Str(required=False),  # Can be 'e-mail', ....
        'create_count': fields.Int(required=False),
        'username': fields.Str(required=False),
        'password': fields.Str(required=False),
        'ssh_key': fields.Str(required=False),
        'network': fields.Str(required=False),
        'subnet': fields.Str(required=False),
        'assign_ip': fields.Bool(required=False, missing=True),
        # Admin fields
        'backend_id': fields.Str(required=False),
    }

    @auth.login_required
    @use_args(get_computes_args, location=LOCATION)
    def get(self, args):
        return do_get_computes(args=args)

    @auth.login_required
    @use_args(create_compute_args, location=LOCATION)
    def post(self, args):
        return do_create_compute(args=args)


class Compute(Resource):
    get_compute_args = base.GET_OBJECT_ARGS

    update_compute_args = {
    }

    delete_compute_args = {
    }

    @auth.login_required
    @use_args(get_compute_args, location=LOCATION)
    def get(self, args, compute_id=None):
        args['compute_id'] = compute_id
        return do_get_compute(args=args)

    @auth.login_required
    @use_args(update_compute_args, location=LOCATION)
    def put(self, args, compute_id=None):
        args['compute_id'] = compute_id
        return do_update_compute(args=args)

    @auth.login_required
    @use_args(delete_compute_args, location=LOCATION)
    def delete(self, args, compute_id):
        args['compute_id'] = compute_id
        return do_delete_compute(args=args)


#####################################################################
# COMPUTE STATUS
#####################################################################

def do_get_compute_status(args):
    """
    Do get compute status.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get compute status',
        data=args)
    return base.exec_manager_func(compute_os.get_compute_status, ctx)


class ComputeStatus(Resource):
    get_status_args = base.GET_OBJECT_ARGS

    @auth.login_required
    @use_args(get_status_args, location=LOCATION)
    def get(self, args, compute_id=None):
        args['compute_id'] = compute_id
        return do_get_compute_status(args=args)

#####################################################################
# COMPUTE ACTIONS
#####################################################################


def do_get_compute_actions(args):
    """
    Do list actions of compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get compute actions',
        data=args)
    ctx.response = compute_os.supported_actions
    return base.process_result_context(ctx)


def do_compute_action(args):
    """
    Do an action on compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='perform compute action',
        data=args)
    return base.exec_manager_func_with_log(compute_os.perform_action, ctx,
                                           action=md.HistoryAction.PERFORM_COMPUTE_ACTION)


class ComputeActions(Resource):
    get_actions_args = base.LIST_OBJECTS_ARGS

    @auth.login_required
    @use_args(get_actions_args, location=LOCATION)
    def get(self, args, compute_id=None):
        args['compute_id'] = compute_id
        return do_get_compute_actions(args=args)


class ComputeAction(Resource):
    compute_action_args = {
        'action': fields.Str(required=True),
    }

    @auth.login_required
    @use_args(compute_action_args, location=LOCATION)
    def post(self, args, compute_id=None):
        args['compute_id'] = compute_id
        return do_compute_action(args=args)


#####################################################################
# COMPUTE SNAPSHOTS
#####################################################################

def do_get_snapshot(args):
    """
    Do get snapshot of compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get snapshot',
        data=args)
    return base.exec_manager_func(compute_os.get_snapshot, ctx)


def do_get_snapshots(args):
    """
    Do get multiple snapshots of compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get snapshots',
        data=args)
    return base.exec_manager_func(compute_os.get_snapshots, ctx)


def do_create_snapshot(args):
    """
    Do create snapshot for compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create snapshot',
        data=args)
    return base.exec_manager_func_with_log(compute_os.create_snapshot, ctx,
                                           action=md.HistoryAction.CREATE_SNAPSHOT)


def do_update_snapshot(args):
    """
    Do update snapshot for compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update snapshot',
        data=args)
    return base.exec_manager_func_with_log(compute_os.update_snapshot, ctx,
                                           action=md.HistoryAction.UPDATE_SNAPSHOT)


def do_delete_snapshot(args):
    """
    Do delete snapshot of compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete snapshot',
        data=args)
    return base.exec_manager_func_with_log(compute_os.delete_snapshot, ctx,
                                           action=md.HistoryAction.DELETE_SNAPSHOT)


def do_rollback_snapshot(args):
    """
    Do rollback snapshot for compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='rollback snapshot',
        data=args)
    return base.exec_manager_func_with_log(compute_os.rollback_snapshot, ctx,
                                           action=md.HistoryAction.ROLLBACK_SNAPSHOT)


class ComputeSnapshots(Resource):
    get_snapshots_args = {
        **base.LIST_OBJECTS_ARGS,
        'structured': fields.Bool(required=False, missing=False),
        'volume_id': fields.Str(required=False),
    }

    create_snapshot_args = {
        'name': fields.Str(required=True),
        'description': fields.Str(required=False, missing='snapshot'),
    }

    @auth.login_required
    @use_args(get_snapshots_args, location=LOCATION)
    def get(self, args, compute_id=None):
        args['compute_id'] = compute_id
        return do_get_snapshots(args=args)

    @auth.login_required
    @use_args(create_snapshot_args, location=LOCATION)
    def post(self, args, compute_id=None):
        args['compute_id'] = compute_id
        return do_create_snapshot(args=args)


class ComputeSnapshot(Resource):
    get_snapshot_args = {
        **base.GET_OBJECT_ARGS,
    }

    update_snapshot_args = {
        'name': fields.Str(required=True),
        'description': fields.Str(required=False, missing='snapshot'),
    }

    rollback_snapshot_args = {
        'volume_id': fields.Str(required=True),
    }

    delete_snapshot_args = {
        'force': fields.Boolean(required=False, missing=False),
    }

    @auth.login_required
    @use_args(get_snapshot_args, location=LOCATION)
    def get(self, args, snapshot_id, compute_id=None):
        args['compute_id'] = compute_id
        args['snapshot_id'] = snapshot_id
        return do_get_snapshot(args=args)

    @auth.login_required
    @use_args(rollback_snapshot_args, location=LOCATION)
    def post(self, args, snapshot_id, compute_id=None):
        args['compute_id'] = compute_id
        args['snapshot_id'] = snapshot_id
        return do_rollback_snapshot(args=args)

    @auth.login_required
    @use_args(update_snapshot_args, location=LOCATION)
    def put(self, args, snapshot_id, compute_id=None):
        args['compute_id'] = compute_id
        args['snapshot_id'] = snapshot_id
        return do_update_snapshot(args=args)

    @auth.login_required
    @use_args(delete_snapshot_args, location=LOCATION)
    def delete(self, args, snapshot_id,compute_id=None):
        args['compute_id'] = compute_id
        args['snapshot_id'] = snapshot_id
        return do_delete_snapshot(args=args)


#####################################################################
# COMPUTE BACKUP JOBS
#####################################################################

def do_get_backup_job(args):
    """
    Do get backup job.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get backup job',
        data=args)
    return base.exec_manager_func(compute_os.get_backup_job, ctx)


def do_get_backup_jobs(args):
    """
    Do get multiple backup jobs.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get backup jobs',
        data=args)
    return base.exec_manager_func(compute_os.get_backup_jobs, ctx)


def do_create_backup_job(args):
    """
    Do create backup job.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create backup job',
        data=args)
    return base.exec_manager_func_with_log(compute_os.create_backup_job, ctx,
                                           action=md.HistoryAction.CREATE_BACKUP_JOB)


def do_update_backup_job(args):
    """
    Do update backup job.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update backup job',
        data=args)
    return base.exec_manager_func_with_log(compute_os.update_backup_job, ctx,
                                           action=md.HistoryAction.UPDATE_BACKUP_JOB)


def do_delete_backup_job(args):
    """
    Do delete backup job.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete backup job',
        data=args)
    return base.exec_manager_func_with_log(compute_os.delete_backup_job, ctx,
                                           action=md.HistoryAction.DELETE_BACKUP_JOB)


class ComputeBackupJobs(Resource):
    get_backup_jobs_args = base.LIST_OBJECTS_ARGS

    create_backup_job_args = {
        **base.REGION_ARGS,
        'name': fields.Str(required=True),
        'description': fields.Str(required=False, allow_none=True),
    }

    @auth.login_required
    @use_args(get_backup_jobs_args, location=LOCATION)
    def get(self, args, compute_id=None):
        args['compute_id'] = compute_id
        return do_get_backup_jobs(args=args)

    @auth.login_required
    @use_args(create_backup_job_args, location=LOCATION)
    def post(self, args, compute_id=None):
        args['compute_id'] = compute_id
        return do_create_backup_job(args=args)


class ComputeBackupJob(Resource):
    get_backup_job_args = {
        **base.GET_OBJECT_ARGS,
        'backup_id': fields.Str(required=True),
    }

    update_backup_job_args = {
        'name': fields.Str(required=False),
        'volume_id': fields.Str(required=True),
        'backup_id': fields.Str(required=True),
    }

    delete_backup_job_args = {
        'backup_id': fields.Str(required=True),
    }

    @auth.login_required
    @use_args(get_backup_job_args, location=LOCATION)
    def get(self, args, compute_id=None):
        args['compute_id'] = compute_id
        return do_get_backup_job(args=args)

    @auth.login_required
    @use_args(update_backup_job_args, location=LOCATION)
    def put(self, args, compute_id=None):
        args['compute_id'] = compute_id
        return do_update_backup_job(args=args)

    @auth.login_required
    @use_args(delete_backup_job_args, location=LOCATION)
    def delete(self, args, compute_id=None):
        args['compute_id'] = compute_id
        return do_delete_backup_job(args=args)


#####################################################################
# COMPUTE BACKUP DATA
#####################################################################

def do_get_backup_file(args):
    """
    Do get backup file.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get backup file',
        data=args)
    return base.exec_manager_func(compute_os.get_backup_file, ctx)


def do_get_backup_files(args):
    """
    Do get multiple backup files.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get backup files',
        data=args)
    return base.exec_manager_func(compute_os.get_backup_files, ctx)


def do_create_backup_file(args):
    """
    Do create backup file.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create backup file',
        data=args)
    return base.exec_manager_func_with_log(compute_os.create_backup_file, ctx,
                                           action=md.HistoryAction.CREATE_BACKUP_FILE)


def do_update_backup_file(args):
    """
    Do update backup file.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='update backup file',
        data=args)
    return base.exec_manager_func_with_log(compute_os.update_backup_file, ctx,
                                           action=md.HistoryAction.UPDATE_BACKUP_FILE)


def do_delete_backup_file(args):
    """
    Do delete backup file.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='delete backup file',
        data=args)
    return base.exec_manager_func_with_log(compute_os.delete_backup_file, ctx,
                                           action=md.HistoryAction.DELETE_BACKUP_FILE)


def do_rollback_backup_file(args):
    """
    Do rollback backup for compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='rollback backup file',
        data=args)
    return base.exec_manager_func_with_log(compute_os.rollback_backup_file, ctx,
                                           action=md.HistoryAction.ROLLBACK_BACKUP_FILE)


class ComputeBackupFiles(Resource):
    get_backup_files_args = {
        ** base.LIST_OBJECTS_ARGS,
        'structured': fields.Bool(required=False, missing=False),
        'volume_id': fields.Str(required=False),
    }

    create_backup_file_args = {
        'name': fields.Str(required=True),
        'description': fields.Str(required=False, missing='backup'),
    }

    @auth.login_required
    @use_args(get_backup_files_args, location=LOCATION)
    def get(self, args, compute_id=None):
        args['compute_id'] = compute_id
        return do_get_backup_files(args=args)

    @auth.login_required
    @use_args(create_backup_file_args, location=LOCATION)
    def post(self, args, compute_id=None):
        args['compute_id'] = compute_id
        return do_create_backup_file(args=args)


class ComputeBackupFile(Resource):
    get_backup_file_args = {
        **base.GET_OBJECT_ARGS,
    }

    update_backup_file_args = {

    }

    rollback_backup_file_args = {
        'name': fields.Str(required=False),
    }

    delete_backup_file_args = {
    }

    @auth.login_required
    @use_args(get_backup_file_args, location=LOCATION)
    def get(self, args, backup_id, compute_id=None):
        args['compute_id'] = compute_id
        args['backup_id'] = backup_id
        return do_get_backup_file(args=args)

    @auth.login_required
    @use_args(update_backup_file_args, location=LOCATION)
    def put(self, args, backup_id, compute_id=None):
        args['compute_id'] = compute_id
        args['backup_id'] = backup_id
        return do_update_backup_file(args=args)

    @auth.login_required
    @use_args(rollback_backup_file_args, location=LOCATION)
    def post(self, args, backup_id, compute_id=None):
        args['compute_id'] = compute_id
        return do_rollback_backup_file(args=args)

    @auth.login_required
    @use_args(delete_backup_file_args, location=LOCATION)
    def delete(self, args, backup_id, compute_id=None):
        args['compute_id'] = compute_id
        args['backup_id'] = backup_id
        return do_delete_backup_file(args=args)


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
    return base.exec_manager_func(compute_os.get_secgroup, ctx)


def do_get_secgroups(args):
    """
    Do get multiple secgroups of compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get sg rules',
        data=args)
    return base.exec_manager_func(compute_os.get_secgroups, ctx)


def do_create_secgroup(args):
    """
    Do create sg rule for compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create sg rule',
        data=args)
    return base.exec_manager_func_with_log(compute_os.create_secgroup, ctx,
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
    return base.exec_manager_func_with_log(compute_os.update_secgroup, ctx,
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
    return base.exec_manager_func_with_log(compute_os.delete_secgroup, ctx,
                                           action=md.HistoryAction.DELETE_SECGROUP)


class ComputeSecgroups(Resource):
    get_secgroups_args = base.LIST_OBJECTS_ARGS

    create_secgroups_args = {
        'secgroup_id': fields.Str(required=False)
    }

    @auth.login_required
    @use_args(get_secgroups_args, location=LOCATION)
    def get(self, args, compute_id=None):
        args['compute_id'] = compute_id
        return do_get_secgroups(args=args)

    @auth.login_required
    @use_args(create_secgroups_args, location=LOCATION)
    def post(self, args, compute_id=None):
        args['compute_id'] = compute_id
        return do_create_secgroup(args=args)


class ComputeSecgroup(Resource):
    get_secgroup_args = base.GET_OBJECT_ARGS

    update_secgroup_args = {

    }

    delete_secgroup_args = {
    }

    @auth.login_required
    @use_args(get_secgroup_args, location=LOCATION)
    def get(self, args, compute_id=None, secgroup_id=None):
        args['compute_id'] = compute_id
        args['secgroup_id'] = secgroup_id
        return do_get_secgroup(args=args)

    @auth.login_required
    @use_args(update_secgroup_args, location=LOCATION)
    def put(self, args, compute_id=None, secgroup_id=None):
        args['compute_id'] = compute_id
        args['secgroup_id'] = secgroup_id
        return do_update_secgroup(args=args)

    @auth.login_required
    @use_args(delete_secgroup_args, location=LOCATION)
    def delete(self, args, compute_id=None, secgroup_id=None):
        args['compute_id'] = compute_id
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
    return base.exec_manager_func(compute_os.get_secgroup_rule, ctx)


def do_get_secgroup_rules(args):
    """
    Do get multiple secgroup rules of compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='get secgroup rules',
        data=args)
    return base.exec_manager_func(compute_os.get_secgroup_rules, ctx)


def do_create_secgroup_rule(args):
    """
    Do create sg rule for compute.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='create secgroup rule',
        data=args)
    return base.exec_manager_func_with_log(compute_os.create_secgroup_rule, ctx,
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
    return base.exec_manager_func_with_log(compute_os.update_secgroup_rule, ctx,
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
    return base.exec_manager_func_with_log(compute_os.delete_secgroup_rule, ctx,
                                           action=md.HistoryAction.DELETE_SECGROUP_RULE)


class ComputeSecgroupRules(Resource):
    get_secgroup_rules_args = base.LIST_OBJECTS_ARGS

    create_secgroup_rule_args = {
        'direction': fields.Str(required=True),
        'ether_type': fields.Str(required=True),
        'port_range': fields.Str(required=True),
        'source_ip': fields.Str(required=True),
        'protocol': fields.Str(required=True),
    }

    @auth.login_required
    @use_args(get_secgroup_rules_args, location=LOCATION)
    def get(self, args, compute_id=None, secgroup_id=None):
        args['compute_id'] = compute_id
        args['secgroup_id'] = secgroup_id
        return do_get_secgroup_rules(args=args)

    @auth.login_required
    @use_args(create_secgroup_rule_args, location=LOCATION)
    def post(self, args, compute_id=None, secgroup_id=None):
        args['compute_id'] = compute_id
        args['secgroup_id'] = secgroup_id
        return do_create_secgroup_rule(args=args)


class ComputeSecgroupRule(Resource):
    get_secgroup_rule_args = base.GET_OBJECT_ARGS

    update_secgroup_rule_args = {
    }

    delete_secgroup_rule_args = {
    }

    @auth.login_required
    @use_args(get_secgroup_rule_args, location=LOCATION)
    def get(self, args, compute_id=None, secgroup_id=None, rule_id=None):
        args['compute_id'] = compute_id
        args['secgroup_id'] = secgroup_id
        args['rule_id'] = rule_id
        return do_get_secgroup_rule(args=args)

    @auth.login_required
    @use_args(update_secgroup_rule_args, location=LOCATION)
    def put(self, args, compute_id=None, secgroup_id=None, rule_id=None):
        args['compute_id'] = compute_id
        args['id'] = secgroup_id
        args['rule_id'] = rule_id
        return do_update_secgroup_rule(args=args)

    @auth.login_required
    @use_args(delete_secgroup_rule_args, location=LOCATION)
    def delete(self, args, compute_id=None, secgroup_id=None, rule_id=None):
        args['compute_id'] = compute_id
        args['secgroup_id'] = secgroup_id
        args['rule_id'] = rule_id
        return do_delete_secgroup_rule(args=args)

#####################################################################
# COMPUTE SSH KEY
#####################################################################

def do_get_ssh_key(args):
    """
    Do get ssh key.
    :param args:
    :return:
    """
    bit_count = args.get('bit_count') or 2048
    create_count = args.get('create_count') or 1
    if create_count == 1:
        priv_key, pub_key = hash_util.gen_ssh_key(bit_count=bit_count)
        return {
            'private_key': priv_key,
            'public_key': pub_key,
        }, 200
    else:
        result = []
        for i in range(create_count):
            priv_key, pub_key = hash_util.gen_ssh_key(bit_count=bit_count)
            result.append({
                'private_key': priv_key,
                'public_key': pub_key,
            })
        return result, 200


class ComputeSSHKey(Resource):
    get_ssh_key_args = {
        **base.GET_OBJECT_ARGS,
        'bit_count': fields.Int(required=False, missing=2048),
        'create_count': fields.Int(required=False, missing=1),
    }

    @auth.login_required
    @use_args(get_ssh_key_args, location=LOCATION)
    def get(self, args):
        return do_get_ssh_key(args=args)


#####################################################################
# COMPUTE TASK
#####################################################################

def do_run_compute_task(args):
    """
    Do computes background task.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='do run compute task',
        data=args)
    return base.exec_manager_func(compute_os.run_bg_task, ctx)


class ComputesTask(Resource):
    run_task_args = {
        'label': fields.Str(required=False, missing='daily'),  # daily, weekly
    }

    @auth.login_required
    @use_args(run_task_args, location=LOCATION)
    def post(self, args):
        return do_run_compute_task(args=args)


#####################################################################
# COMPUTE SYNC
#####################################################################

def do_sync_compute(args):
    """
    Do sync compute info with backend.
    :param args:
    :return:
    """
    ctx = context.create_context(
        task='synchronize compute',
        data=args)
    return base.exec_manager_func_with_log(compute_os.sync_compute, ctx,
                                           log_action=md.HistoryAction.SYNCHRONIZE_COMPUTE)


class ComputeSync(Resource):
    do_sync_args = {
        'source': fields.Str(required=False, missing='infra'),  # all, order, infra
        'target': fields.Str(required=False, missing='compute'),
    }

    @auth.login_required
    @use_args(do_sync_args, location=LOCATION)
    def post(self, args, compute_id=None):
        args['compute_id'] = compute_id
        return do_sync_compute(args=args)
