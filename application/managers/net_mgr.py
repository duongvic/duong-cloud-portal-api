#
# Copyright (c) 2020 FTI-CAS
#

import ipaddress

from application import app
from application.base import errors
from application.base.context import create_admin_context
from application.managers import base as base_mgr, user_mgr
from application import models as md
from application.utils import date_util, net_util

LOG = app.logger

ADMIN_ROLES = (md.UserRole.ADMIN, md.UserRole.ADMIN_SALE, md.UserRole.ADMIN_IT)
GET_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
LIST_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
CREATE_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
UPDATE_ROLES = (md.UserRole.USER,) + ADMIN_ROLES
DELETE_ROLES = (md.UserRole.USER,) + ADMIN_ROLES

IP_ASSIGNING_TIMEOUT = 3600  # seconds


def get_ip(ctx):
    """
    Get IP.
    :param ctx: sample ctx data:
        {
            'ip': <ip object>,
            'ip_addr': <ip addr if ip object is not passed>,
            'fields': <fields to get as a list of str>,
        }
    :return:
    """
    data = ctx.data
    ip = md.load_ip(data.get('ip') or data['ip_addr'])
    if not ip:
        ctx.set_error(errors.NET_IP_NOT_FOUND, status=404)
        return

    if ctx.request_user.id != ip.user_id:
        ctx.target_user = ip.user
    if not user_mgr.check_user(ctx, roles=GET_ROLES):
        return

    base_mgr.dump_object(ctx, object=ip)
    return ip


def get_ips(ctx):
    """
    Get multiple IPs.
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
    admin_roles = md.UserRole.admin_roles_of(LIST_ROLES)

    # Admin can get IPs of a specific user or all users
    if ctx.check_request_user_role(admin_roles):
        user_id = ctx.data.get('user_id')
        override_condition = {'user_id': user_id} if user_id else None
    else:
        # User can only get his IPs
        override_condition = {'user_id': ctx.target_user.id}

    # Filter by compute_id if there is configuration
    compute_id = ctx.data.get('compute_id')
    if compute_id:
        override_condition = override_condition or {}
        override_condition['compute_id'] = compute_id

    return base_mgr.dump_objects(ctx,
                                 model_class=md.PublicIP,
                                 override_condition=override_condition)


def validate_ip(ctx, ip=None, type=None, version=None, status=None):
    """
    Validate IP params.
    :param ctx:
    :param ip:
    :param type:
    :param version:
    :param status:
    :return: the normalized ip if ip is passed.
    """
    if status is not None and not md.IPStatus.is_valid(status):
        e = ValueError('IP status {} invalid.'.format(status))
        LOG.error(e)
        ctx.set_error(errors.NET_IP_STATUS_INVALID, cause=e, status=406)
        return

    if version is not None and not md.IPVersion.is_valid(version):
        e = ValueError('IP version {} invalid.'.format(version))
        LOG.error(e)
        ctx.set_error(errors.NET_IP_VERSION_INVALID, cause=e, status=406)
        return

    if ip:
        try:
            if version is not None:
                ip = getattr(ipaddress, 'IPv{}Address'.format(version))(ip)
            else:
                ip = ipaddress.ip_address(ip)
        except BaseException as e:
            e = ValueError('IP address {} invalid.'.format(ip))
            LOG.error(e)
            ctx.set_error(errors.NET_IP_ADDRESS_INVALID, cause=e, status=406)
            return

    if ip:
        return ip

    return True


def create_ip(ctx):
    """
    Create IP object.
    :param ctx:
    :return:
    """
    if not user_mgr.check_user(ctx, roles=CREATE_ROLES):
        return

    user = ctx.target_user
    data = ctx.data
    ip_addr = str(data.get('ip') or data['ip_addr']).strip()

    ip = md.PublicIP.query.get(str(ip_addr))
    if ip and ip.status in (md.IPStatus.ASSIGNED, md.IPStatus.ASSIGNING):
        e = ValueError('IP address {} in use.'.format(ip_addr))
        LOG.error(e)
        ctx.set_error(errors.NET_IP_IN_USE, cause=e, status=406)
        return

    if ip:
        update_ip(ctx)
        return ip

    # To prevent race condition, create a lock in DB
    @base_mgr.with_lock(ctx, id='lock_ip:' + ip_addr, timeout=5)
    def _create_ip():
        type = data.get('type') or None
        version = data.get('version') or net_util.get_ip_version(ip_addr)
        status = data['status']
        start_date = data.get('start_date') or None
        end_date = data.get('end_date') or None
        user_id = user.id if user else data.get('user_id')
        compute_id = data.get('compute_id') or None

        if status in (md.IPStatus.ASSIGNING, md.IPStatus.ASSIGNED):
            start_date = date_util.utc_now()
        elif status == md.IPStatus.UNUSED:
            end_date = date_util.utc_now()

        ip = validate_ip(ctx, ip=ip_addr, type=type, version=version, status=status)
        if ctx.failed:
            return

        ip = md.PublicIP(addr=str(ip), type=type, version=version, status=status,
                         create_date=date_util.utc_now(), start_date=start_date,
                         end_date=end_date, user_id=user_id, compute_id=compute_id)

        error = md.save_new(ip)
        if error:
            ctx.set_error(errors.NET_IP_CREATE_FAILED, cause=error, status=500)
            return

        # Return the IP data to user
        ctx.data = {
            'ip': ip,
        }
        get_ip(ctx)
        return ip

    # Execute the function
    return _create_ip()


def update_ip(ctx):
    """
    Update IP object.
    :param ctx:
    :return:
    """
    if not user_mgr.check_user(ctx, roles=UPDATE_ROLES):
        return

    data = ctx.data
    ip = md.load_ip(data.get('ip') or data['ip_addr'])
    if not ip:
        ctx.set_error(errors.NET_IP_NOT_FOUND, status=404)
        return

    status = data.get('status') or ip.status
    # If target status is UNUSED, then call delete_ip()
    if status != ip.status and status == md.IPStatus.UNUSED:
        delete_ip(ctx)
        return

    # To prevent race condition, create a lock in DB
    @base_mgr.with_lock(ctx, id='lock_ip:' + ip.addr, timeout=5)
    def _update_ip():
        compute_id = data.get('compute_id') or ip.compute_id
        user_id = data.get('user_id') or ip.user_id
        start_date = data.get('start_date') or ip.start_date
        end_date = data.get('end_date') or ip.end_date

        if status != ip.status and status in (md.IPStatus.ASSIGNED, md.IPStatus.ASSIGNING):
            start_date = date_util.utc_now()
            end_date = None

        ip.status = status
        ip.compute_id = compute_id
        ip.user_id = user_id
        ip.start_date = start_date
        ip.end_date = end_date

        error = md.save(ip)
        if error:
            ctx.set_error(error, status=500)
            return

        # Return the IP data to user
        ctx.data = {
            'ip': ip,
        }
        get_ip(ctx)
        return ip

    # Execute the function
    return _update_ip()


def delete_ip(ctx):
    """
    Delete IP object.
    :param ctx:
    :return:
    """
    if not user_mgr.check_user(ctx, roles=DELETE_ROLES):
        return

    data = ctx.data
    ip = md.load_ip(data.get('ip') or data['ip_addr'])
    if not ip:
        ctx.set_error(errors.NET_IP_NOT_FOUND, status=404)
        return

    compute = ip.compute
    if compute and compute.public_ip == ip.addr:
        ctx.set_error(errors.NET_IP_IN_USE, status=406)
        return

    # To prevent race condition, create a lock in DB
    @base_mgr.with_lock(ctx, id='lock_ip:' + ip.addr, timeout=5)
    def _delete_ip():
        # NOT DELETE, just change IP status to UNUSED
        ip.status = md.IPStatus.UNUSED
        ip.compute_id = None
        ip.user_id = None
        ip.end_date = date_util.utc_now()

        error = md.save(ip)
        if error:
            ctx.set_error(error, status=500)
            return

    # Execute the function
    return _delete_ip()


def get_ip_config(ctx, config_name=None):
    """
    Get Net IP config from DB.
    :param ctx:
    :param config_name:
    :return:
    """
    ip_config = md.query(md.Configuration,
                         type=md.ConfigurationType.NETWORK_IP,
                         **({'name': config_name} if config_name else {}),
                         status=md.ConfigurationStatus.ENABLED,
                         order_by=md.Configuration.version.desc()).first()
    if not ip_config:
        e = ValueError('Config NETWORK_IP/{} not found in database.'
                       .format(config_name or ''))
        LOG.error(e)
        ctx.set_error(errors.CONFIG_NOT_FOUND, cause=e, status=404)
        return

    ctx.response = ip_config
    return ip_config


def validate_ip_config(ctx, config_name=None):
    """
    Get Net IP config from DB.
    :param ctx:
    :param config_name:
    :return:
    """
    ip_config = get_ip_config(ctx, config_name=config_name)
    if not ip_config:
        e = ValueError('Config NETWORK_IP/{} not found in database.'
                       .format(config_name or ''))
        LOG.error(e)
        ctx.set_error(errors.CONFIG_NOT_FOUND, cause=e, status=404)
        return

    contents = ip_config.contents
    ip_ver = contents['version']
    pools = contents['pools']
    IPNetCls = getattr(ipaddress, 'IPv{}Network'.format(ip_ver))

    last_net = None
    for pool in pools:
        cidr_list = pool['cidr']
        if isinstance(cidr_list, str):
            cidr_list = [cidr_list]
        for cidr in cidr_list:
            try:
                net = IPNetCls(cidr)
            except BaseException as e:
                e = ValueError('Network {} invalid. Error: {}.'.format(cidr, e))
                LOG.error(e)
                ctx.set_error(errors.NET_IP_POOL_INVALID, cause=e, status=406)
                return

            if last_net and net.overlaps(last_net):
                e = ValueError('Network {} and {} are overlap.'.format(str(last_net), str(net)))
                LOG.error(e)
                ctx.set_error(errors.NET_IP_POOL_INVALID, cause=e, status=406)
                return

            if last_net and net[0] < last_net[0]:
                e = ValueError('Network {} and {} are in incorrect order.'.format(str(last_net), str(net)))
                LOG.error(e)
                ctx.set_error(errors.NET_IP_POOL_INVALID, cause=e, status=406)
                return

            last_net = net

    ctx.response = ip_config
    return ip_config


def iterate_pool_ips(ctx, start_ip=None):
    """
    Iterate over all pools IPs.
    Usage:
        for ctx, ip, net, pool in iterate_pool_ips(...):
            if ctx.failed:
                return
            <do something with ip and net>

    :param ctx:
    :param start_ip:
    :return:
    """
    data = ctx.data
    ip_config = data.get('ip_config') or get_ip_config(ctx)
    if ctx.failed:
        return

    contents = ip_config.contents
    ip_ver = contents['version']
    pools = contents['pools']

    IPNetCls = getattr(ipaddress, 'IPv{}Network'.format(ip_ver))
    IPAddrCls = getattr(ipaddress, 'IPv{}Address'.format(ip_ver))

    if start_ip and not isinstance(start_ip, IPAddrCls):
        start_ip = IPAddrCls(start_ip)

    for pool in pools:
        cidr_list = pool['cidr']
        if isinstance(cidr_list, str):
            cidr_list = [cidr_list]

        for cidr in cidr_list:
            net = IPNetCls(cidr)
            if start_ip:
                if start_ip not in net:
                    continue
                ip = start_ip
                last_ip = net[-1]
                while ip <= last_ip:
                    yield ctx, ip, net, pool
                    ip = ip + 1
            else:
                for ip in net:
                    yield ctx, ip, net, pool


def get_pool_contains_ip(ctx, ip):
    """
    Check if an IP address is in pool.
    :param ctx:
    :param ip:
    :return:
    """
    data = ctx.data
    ip_config = data.get('ip_config') or get_ip_config(ctx)
    if ctx.failed:
        return

    contents = ip_config.contents
    ip_ver = contents['version']
    pools = contents['pools']

    IPNetCls = getattr(ipaddress, 'IPv{}Network'.format(ip_ver))
    IPAddrCls = getattr(ipaddress, 'IPv{}Address'.format(ip_ver))

    try:
        if isinstance(ip, IPAddrCls):
            ip_obj = ip
        else:
            ip_obj = IPAddrCls(ip)
    except BaseException as e:
        LOG.error(e)
        ctx.set_error(errors.NET_IP_ADDRESS_INVALID, cause=e, status=406)
        return

    try:
        for pool in pools:
            cidr_list = pool['cidr']
            if isinstance(cidr_list, str):
                cidr_list = [cidr_list]

            for cidr in cidr_list:
                if ip_obj in IPNetCls(cidr):
                    ctx.response = pool
                    return ctx.response
    except BaseException as e:
        LOG.error(e)
        ctx.set_error(errors.NET_IP_POOL_INVALID, cause=e, status=406)
        return

    e = ValueError('IP {} is out of pools config.'.format(ip))
    LOG.error(e)
    ctx.set_error(errors.NET_IP_OUT_OF_POOL, cause=e, status=406)
    return None


def find_unused_ip(ctx, max_count=5):
    """
    Find unused IPs.
    :param ctx:
    :param max_count:
    :return:
    """
    data = ctx.data
    ip_config = data.get('ip_config') or get_ip_config(ctx)
    if ctx.failed:
        return
    data['ip_config'] = ip_config

    def _add_ip(ip_list, ip):
        ip_list.append(ip)
        return len(ip_list) < max_count

    avail_ips = []

    # Query released IPs first
    for item in md.iterate(md.PublicIP,
                           status=md.IPStatus.UNUSED,
                           order_by=md.PublicIP.end_date.asc(),
                           page_size=min(max_count, 10)):
        ip_addr = item.addr
        item_ctx = ctx.copy(task='check ip in pools', data=data)
        if get_pool_contains_ip(item_ctx, ip=ip_addr):
            if not _add_ip(avail_ips, ip_addr):
                break
        else:
            LOG.warning('IP {} is not in configured pools.'.format(ip_addr))

    if avail_ips:
        ctx.response = {
            'ips': avail_ips,
        }
        return ctx.response

    # Try finding ASSIGNING IPs but timed out
    timeout = data.get('ip_assigning_timeout') or IP_ASSIGNING_TIMEOUT
    for item in md.iterate(md.PublicIP,
                           status=md.IPStatus.ASSIGNING,
                           order_by=md.PublicIP.start_date.asc(),
                           page_size=min(max_count, 10)):
        if date_util.utc_now() > date_util.datetime_add(item.start_date, seconds=timeout):
            ip_addr = item.addr
            item_ctx = ctx.copy(task='check ip in pools', data=data)
            if get_pool_contains_ip(item_ctx, ip=ip_addr):
                if not _add_ip(avail_ips, ip_addr):
                    break
            else:
                LOG.warning('IP {} is not in configured pools.'.format(ip_addr))
        else:
            # IP is still in assigning status, don't take it
            pass

    if avail_ips:
        ctx.response = {
            'ips': avail_ips,
        }
        return ctx.response

    # Query the last created IP, so we can guess next available ones
    item = md.query(md.PublicIP,
                    order_by=md.PublicIP.create_date.desc()).first()
    start_ip = ipaddress.ip_address(item.addr) + 1 if item else None

    test_ips = []
    for ctx, ip, net, pool in iterate_pool_ips(ctx, start_ip=start_ip):
        if ctx.failed:
            return
        if not _add_ip(test_ips, str(ip)):
            avail_ips = filter_unused_ips(test_ips)
            test_ips = []
            if avail_ips:
                break

    if test_ips:
        avail_ips = filter_unused_ips(test_ips)

    if avail_ips:
        ctx.response = {
            'ips': avail_ips,
        }
        return ctx.response

    ctx.set_error(errors.NET_IP_POOL_EXHAUSTED, status=503)
    return


def filter_unused_ips(ip_list):
    """
    Filter unused IPs from the list.
    :param ip_list:
    :return: a list a unused IPs.
    """
    addr_list = [str(ip) for ip in ip_list]
    items = md.query(md.PublicIP, md.PublicIP.addr.in_(addr_list)).all()
    used_addr_list = []
    for item in items:
        if item.status in (md.IPStatus.ASSIGNED, md.IPStatus.ASSIGNING):
            used_addr_list.append(item.addr)

    # All IPs are available
    if not used_addr_list:
        avail_list = ip_list
    else:
        avail_list = []
        for addr in ip_list:
            if addr not in used_addr_list:
                avail_list.append(addr)

    return avail_list


def ip_in_use(ip):
    """
    Check if IP is in use.
    :param ip:
    :return:
    """
    ip = md.PublicIP.query.get(str(ip))
    return ip if ip and ip.status in [md.IPStatus.ASSIGNED, md.IPStatus.ASSIGNING] else None


def _validate_ip_config_in_db():
    ctx = create_admin_context(task='validate IP config in DB')
    validate_ip_config(ctx)
    if ctx.failed:
        raise ValueError(str(ctx.error))


#
# Validate ip_config at startup.
#
# _validate_ip_config_in_db()
