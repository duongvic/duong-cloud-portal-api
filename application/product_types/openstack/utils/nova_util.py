#
# Copyright (c) 2020 FTI-CAS
#

import logging
import os

from novaclient import client as novaclient

from application import app
from application.product_types.openstack.utils import keystone_util as ks_util

LOG = app.logger

DEFAULT_NOVA_API_VERSION = 1.0


def get_nova_client_version():
    """
    Get Nova API version
    :return:
    """
    try:
        api_version = app.config['OS_SERVICES_VERSION']['nova']
    except KeyError:
        return DEFAULT_NOVA_API_VERSION
    else:
        return api_version


def get_nova_client(os_info):
    """
    Get nova client

    :param os_info:
    :return
    """
    sess = ks_util.get_session(os_info)
    return novaclient.Client(get_nova_client_version(), session=sess)


def get_flavor_id(nova_client, flavor_name):
    """
    Get a flavor from name

    :param nova_client:
    :param flavor_name:
    :return:
    """
    flavors = nova_client.flavors.list(detailed=True)
    flavor_id = None
    for f in flavors:
        if f.name == flavor_name:
            flavor_id = f.id
            break
    return flavor_id


def get_flavor(nova_client, flavor_id):
    """
    Get the flavor by name or ID.

    :param nova_client:
    :param flavor_id: ID of the flavor.
    :returns:
    """
    try:
        return nova_client.get(flavor=flavor_id)
    except Exception as e:
        LOG.error("Error [get_flavor(shade_client, '%s')]. "
                  "Exception message: %s", flavor_id, e)
        return None


def get_flavors(nova_client, detailed=True, is_public=True, limit=None):
    """
    Get all flavors

    :param nova_client:
    :param detailed: Whether flavor needs to be return with details
                     (optional).
    :param is_public: Filter flavors with provided access type (optional).
                      None means give all flavors and only admin has query
                      access to all flavor types.
    :param limit: maximum number of flavors to return (optional).
                  Note the API server has a configurable default limit.
                  If no limit is specified here or limit is larger than
                  default, the default limit will be used.
    :returns:
    """
    try:
        return nova_client.list(detailed=detailed, is_public=is_public, limit=limit)
    except Exception as e:
        LOG.error("Error [get_flavors(nova_client)]. "
                  "Exception message: %s", e)
        return None


def create_flavor(nova_client, name, ram, vcpus, disk, **kwargs):
    """
    Create a new flavor

    :param nova_client:
    :param name:
    :param ram:
    :param vcpus:
    :param disk:
    :param kwargs:
    :return:
    """
    try:
        return nova_client.flavors.create(name, ram, vcpus, disk, **kwargs)
    except Exception:
        LOG.exception("Error [create_flavor(nova_client, %s, %s, %s, %s, %s)]",
                      name, ram, disk, vcpus, kwargs['is_public'])
        return None


def delete_flavor(nova_client, flavor_id):
    """
    Delete the flavor

    :param nova_client:
    :param flavor_id:
    :return:
    """
    try:
        return nova_client.flavors.delete(flavor_id)
    except Exception as e:
        LOG.exception("Error [delete_flavor(nova_client, %s)], "
                      "Exception message: %s", flavor_id, e)
        return None


def start_instance(nova_client, instance_id):
    """
    Start the instance.

    :param nova_client:
    :param instance_id:
    :return:
    """
    try:
        return nova_client.servers.start(server=instance_id)
    except Exception as e:
        LOG.exception("Error [start_instance(nova_client, %s)], "
                      "Exception message: %s", instance_id, e)
        return None


def stop_instance(nova_client, instance_id):
    """
    Stop the instance.

    :param nova_client:
    :param instance_id:
    :return:
    """
    try:
        return nova_client.servers.stop(server=instance_id)
    except Exception as e:
        LOG.exception("Error [stop_instance(nova_client, %s)], "
                      "Exception message: %s", instance_id, e)
        return None


def pause_instance(nova_client, instance_id):
    """
    Pause the instance.

    :param nova_client:
    :param instance_id:
    :return:
    """
    try:
        return nova_client.servers.pause(server=instance_id)
    except Exception as e:
        LOG.exception("Error [pause_instance(nova_client, %s)], "
                      "Exception message: %s", instance_id, e)
        return None


def unpause_instance(nova_client, instance_id):
    """
    Unpause the instance.

    :param nova_client:
    :param instance_id:
    :return:
    """
    try:
        return nova_client.servers.unpause(server=instance_id)
    except Exception as e:
        LOG.exception("Error [unpause_instance(nova_client, %s)], "
                      "Exception message: %s", instance_id, e)
        return None


def lock_instance(nova_client, instance_id):
    """
    Lock the instance.

    :param nova_client:
    :param instance_id:
    :return:
    """
    try:
        return nova_client.servers.lock(server=instance_id)
    except Exception as e:
        LOG.exception("Error [lock_instance(nova_client, %s)], "
                      "Exception message: %s", instance_id, e)
        return None


def unlock_instance(nova_client, instance_id):
    """
    Unlock the instance.

    :param nova_client:
    :param instance_id:
    :return:
    """
    try:
        return nova_client.servers.unlock(server=instance_id)
    except Exception as e:
        LOG.exception("Error [unlock_instance(nova_client, %s)], "
                      "Exception message: %s", instance_id, e)
        return None


def suspend_instance(nova_client, instance_id):
    """
    Suspend the instance.

    :param nova_client:
    :param instance_id:
    :return:
    """
    try:
        return nova_client.servers.suspend(server=instance_id)
    except Exception as e:
        LOG.exception("Error [suspend_instance(nova_client, %s)], "
                      "Exception message: %s", instance_id, e)
        return None


def resume_instance(nova_client, instance_id):
    """
    Resume the instance.

    :param nova_client:
    :param instance_id:
    :return:
    """
    try:
        return nova_client.servers.resume(server=instance_id)
    except Exception as e:
        LOG.exception("Error [resume_instance(nova_client, %s)], "
                      "Exception message: %s", instance_id, e)
        return None


def reboot_instance(nova_client, instance_id, reboot_type='HARD'):
    """
    Reboot the instance.

    :param nova_client:
    :param instance_id:
    :param reboot_type: ['HARD', 'SOFT']
    :return:
    """
    try:
        return nova_client.servers.reboot(server=instance_id, reboot_type=reboot_type)
    except Exception as e:
        LOG.exception("Error [reboot_instance(nova_client, %s)], "
                      "Exception message: %s", instance_id, e)
        return None
