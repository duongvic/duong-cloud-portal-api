#
# Copyright (c) 2020 FTI-CAS
#

import urllib.parse as urlparse

from application import app

LOG = app.logger


def get_request_arg(request, key, default_value=None):
    return request.args.get(key, default_value)


def get_client_ip(request):
    return request.access_route[0]


def unquote(value, **kw):
    return urlparse.unquote(value, **kw)


def api_request(api_func=None, api_path=None, method='GET', **kwargs):
    """
    Open a request to API server.
    :param api_func:
    :param api_path:
    :param method:
    :param kwargs:
    :return:
    """
    if app.config['RUN_API_SERVER']:
        args = kwargs['args']
        LOG.debug(args)
        resp, code = api_func(args=args)
        LOG.debug(resp)
        return resp, code

    raise NotImplementedError('Separated API server requires this implementation')
