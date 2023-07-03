#
# Copyright (c) 2020 FTI-CAS
#

from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args

from application import app
from application.api.v1 import base

LOCATION = 'default'
auth = base.auth


#####################################################################
# TESTS
#####################################################################

def do_test(args):
    """
    Do a test.
    :param args:
    :return:
    """
    test_id = args['test_id']
    if test_id == 'os':
        from application.tests import test_os as test
    elif test_id == 'ldap':
        from application.tests import test_ldap as test
    test.do_test()


class Test(Resource):

    exec_test_args = {
    }

    @use_args(exec_test_args, location=LOCATION)
    def post(self, args, test_id):
        args['test_id'] = test_id
        return do_test(args=args)
