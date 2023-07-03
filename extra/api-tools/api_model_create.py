
import codecs
import json
import pprint
import requests
import sys

import api_base as base


# user, configuration, order, compute, promotion, product ADMIN_SALE
USER_ARGS = ['user', 'create']
USER_DATA = {
    'data': {
            "user_name": "thangnt41@fpt.com.vn",
            "email": "thangnt41@fpt.com.vn",
            "status": "ENABLED",
            "create_date": "2020-08-25 04:18:36",
            "role": "ADMIN_SALE",
            "full_name": "Nguy\u1ec5n Ti\u1ebfn Th\u1eafng",
            "cellphone": "0348955989",
            "language": "vi",
            "password_hash": "pbkdf2:sha256:150000$YTNdcAFL$59700f67ff240cd8b70151d646ed0d4686458ffc959ce2a47f3e41afde150ea1"
    },
}


ARGS = sys.argv[1:] or USER_ARGS
base.pp('ARGS:', ARGS)
MODEL = ARGS[0]
CMD = ARGS[1]

URL = base.URL_ADMIN_MODELS % MODEL if CMD == 'list' else base.URL_ADMIN_MODEL % MODEL
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
