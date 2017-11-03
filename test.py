#!/usr/bin/env python3

import sys
import json
import bse_ng

def pprint(d):
    print(json.dumps(d, indent=4))


#bse_ng.validate_basis_file('test.json')

#bsjs = bse_ng.get_atom_basis('6-31g')
#pprint(bsjs['elements'][8])
#print()

#bsjs = bse_ng.get_atom_basis('6-31gs')
#pprint(bsjs['elements'][8])
#print()

bsjs = bse_ng.get_atom_basis('6-31gss')
#pprint(bsjs['elements'][1])
pprint(bsjs)
print()

#print("---------------")
#bsjs = bse_ng.get_atom_basis('6-31g')
#bsjs2 = bse_ng.uncontract_basis_general(bsjs)
#pprint(bsjs['elements'][8])
#print("---------------")
#pprint(bsjs2['elements'][8])
