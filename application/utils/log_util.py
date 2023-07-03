#
# Copyright (c) 2020 FTI-CAS
#

from application import app

LOG = app.logger


class RaisingLogger(object):
    """
    For testing purpose only.
    """
    DEBUG = 'debug'
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'

    MAP = {
        'debug': 0,
        'info': 1,
        'warning': 2,
        'error': 3,
    }

    def __init__(self, target_logger, level=ERROR, message=None):
        self.target_logger = target_logger
        self.level = level
        self.message = message

    def debug(self, *a, **kw):
        self._log('debug', *a, **kw)

    def info(self, *a, **kw):
        self._log('info', *a, **kw)

    def warning(self, *a, **kw):
        self._log('warning', *a, **kw)

    def error(self, *a, **kw):
        self._log('error', *a, **kw)

    def _log(self, level, *a, **kw):
        e = None
        if a:
            e = a[0]
        if isinstance(e, Exception) and self.MAP[level] >= self.MAP[self.level]:
            raise e
        getattr(self.target_logger, level)(*a, **kw)
