#!/usr/bin/env python3

# This script determines what basis sets are missing authoritative sources
# that should be placed in this directory

import os
from basis_set_exchange import get_metadata, misc

my_dir = os.path.dirname(os.path.abspath(__file__))
auth_sources = [x for x in os.listdir(my_dir) if x.endswith('.bz2')]

md = get_metadata()

found_ver = {}

# Start with everything in the metadata, removing what we find
# in this directory
missing = {k: list(v['versions'].keys()) for k, v in md.items()}

for s in auth_sources:
    bsname, ver, _, _ = s.split('.')
    bsname = misc.basis_name_from_filename(bsname)

    if not bsname in missing:
        raise RuntimeError("Source {} does not correspond to a basis set in the library".format(bsname))
    if not ver in missing[bsname]:
        raise RuntimeError("Source {} version {} does not correspond to a basis set version in the library".format(
            bsname, ver))

    missing[bsname].remove(ver)

    # Also remove aliases
    for other_name in md[bsname]['other_names']:
        other_name = misc.transform_basis_name(other_name)
        missing[other_name].remove(ver)

missing = {k: v for k, v in missing.items() if len(v) > 0}

maxlen = max([len(k) for k in missing.keys()]) + 5

for k, v in missing.items():
    print('{:{maxlen}} {}'.format(k, ','.join(v), maxlen=maxlen))
