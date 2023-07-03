#
# Copyright (c) 2020 FTI-CAS
#

import unittest
import os
# from os import environ as env
# from application.product_types.openstack.tests.utils import test_keystone_client as tk
# from application.product_types.openstack.tests.utils import test_shade_client as ts
# from application.product_types.openstack.tests.contexts import test_undeploy as td
# from application.product_types.openstack.tests.contexts import test_deploy as td
from application.product_types.openstack.tests.utils import test_os_api as td
#
# # _test_heat_context = unittest.TestLoader().loadTestsFromTestCase(tk.KeystoneClientTestCase)
# # unittest.TextTestRunner(verbosity=2).run(_test_heat_context)
#
# # _test_heat_context = unittest.TestLoader().loadTestsFromTestCase(ts.ShadeClientTestCase)
# # unittest.TextTestRunner(verbosity=2).run(_test_heat_context)
#
# # _test_heat_context = unittest.TestLoader().loadTestsFromTestCase(td.HeatContextDeployTestCase)
# # unittest.TextTestRunner(verbosity=2).run(_test_heat_context)
#
# # _test_heat_context = unittest.TestLoader().loadTestsFromTestCase(td.HeatContextUnDeployTestCase)
# # unittest.TextTestRunner(verbosity=2).run(_test_heat_context)
#
_test_heat_context = unittest.TestLoader().loadTestsFromTestCase(td.OSApiTestCase)
unittest.TextTestRunner(verbosity=2).run(_test_heat_context)
