
import codecs
import json
import pprint
import requests
import sys

URL_LOCAL = 'http://localhost:5000'
URL_BASE = URL_LOCAL

AUTH_INFO_LOCAL = {
    'user_name': 'admin.foxcloud.vn',
    'password': 'FTI-CAS-19%102&z0*#@37',
}
AUTH_INFO_ODS_DEMO = {
    'user_name': 'admin.foxcloud.vn',
    'password': 'FTI-CAS-19%102&z0*#@37',
}
AUTH_INFO = AUTH_INFO_ODS_DEMO


VERIFY = False

URL_API = URL_BASE + '/api/v1'
URL_AUTH = URL_API + '/auth'

URL_COMPUTES = URL_API + '/computes'
URL_COMPUTE = URL_API + '/compute/%s'
URL_COMPUTE_SYNC = URL_API + '/compute/%s/sync'
URL_COMPUTE_CONFIG = URL_API + '/compute/%s/config'
URL_COMPUTE_STATUS = URL_API + '/compute/%s/status'
URL_COMPUTE_STATS = URL_API + '/compute/%s/stats'

URL_ADMIN_MODELS = URL_API + '/admin/models/%s'
URL_ADMIN_MODEL = URL_API + '/admin/model/%s'


def pp(d, *a, **kw):
    if isinstance(d, dict):
        print(json.dumps(d, indent=4))
    else:
        print(d, *a, **kw)


# Login
r = requests.post(
    URL_AUTH,
    json=AUTH_INFO,
    verify=VERIFY,
)
AUTH = r.json()
pp(AUTH)
