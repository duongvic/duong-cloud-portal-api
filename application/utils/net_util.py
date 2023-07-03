#
# Copyright (c) 2020 FTI-CAS
#

import ipaddress
import platform
import subprocess

from application import app

LOG = app.logger


def get_ip_version(ip):
    """
    Detect IP version from IP address.
    :param ip: ip address in string or integer
    :return:
    """
    return ipaddress.ip_address(ip).version


def ping(host, count=3):
    """
    Check host available by ping command.
    :param host:
    :param count:
    :return:
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, str(count), host]
    return subprocess.call(command) == 0


def validate_ipaddress(ip_address):
    try:
        ip = ipaddress.ip_address(ip_address)
        return True if ip else False
    except:
        return False
