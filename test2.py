#!/usr/bin/env python3

import sys
import json
import bse_ng

def pprint(d):
    print(json.dumps(d, indent=4))


bs = bse_ng.get_full_basis('6-31gss')
pprint(bs)
