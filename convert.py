#!/usr/bin/env python3

import sys
import bse_ng
from bse_ng.converters import g94 

bsjs = g94.g94_to_json(sys.argv[1], sys.argv[2])
bse_ng.write_json_basis_file(sys.argv[2] + '.json',  bsjs)
