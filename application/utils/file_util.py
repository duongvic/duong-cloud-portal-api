#
# Copyright (c) 2020 FTI-CAS
#

from application import app

LOG = app.logger


def read_content(file):
    """
    Read file content.
    """
    with open(file, mode='r') as f:
        return f.read()
