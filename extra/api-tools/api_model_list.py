
import codecs
import json
import pprint
import requests
import sys

import api_base as base


# user, configuration, order, compute, promotion, product
USER_ARGS = ['compute', 'list']
USER_DATA = {
    'page_size': 1000
}


ARGS = sys.argv[1:] or USER_ARGS
base.pp('ARGS:', ARGS)
MODEL = ARGS[0]
CMD = ARGS[1]

URL = base.URL_ADMIN_MODELS % MODEL if CMD == 'list' else base.URL_ADMIN_MODEL % MODEL
base.pp('URL:', URL)

r = requests.get(
    URL,
    headers={
        'Authorization': 'bearer %s' % (base.AUTH['access_token']),
    },
    json=USER_DATA,
    verify=base.VERIFY,
)
base.pp(json.dumps(r.json(encoding='utf-8'), indent=4))

with open('out_{}_{}.txt'.format(MODEL, CMD), 'w') as outfile:
    outfile.write(json.dumps(r.json(encoding='utf-8'), indent=4))
