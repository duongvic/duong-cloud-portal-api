
import codecs
import json
import pprint
import requests
import sys

import api_base as base


USER_ARGS = ['compute', 'sync']
USER_DATA = {
    'source': 'infra'
}
COMPUTE_ID = 17

ARGS = sys.argv[1:] or USER_ARGS
base.pp('ARGS:', ARGS)
MODEL = ARGS[0]
CMD = ARGS[1]

URL = base.URL_COMPUTE_SYNC % COMPUTE_ID
base.pp('URL:', URL)

r = requests.post(
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
