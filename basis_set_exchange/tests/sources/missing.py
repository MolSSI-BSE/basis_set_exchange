# Copyright (c) 2017-2022 The Molecular Sciences Software Institute, Virginia Tech
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

'''
This script determines what basis sets are missing authoritative sources
that should be placed in this directory
'''

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

    if bsname not in missing:
        raise RuntimeError("Source {} does not correspond to a basis set in the library".format(bsname))
    if ver not in missing[bsname]:
        raise RuntimeError("Source {} version {} does not correspond to a basis set version in the library".format(
            bsname, ver))

    missing[bsname].remove(ver)

    # Also remove aliases
    for other_name in md[bsname]['other_names']:
        other_name = misc.transform_basis_name(other_name)
        missing[other_name].remove(ver)

missing = {k: v for k, v in missing.items() if v}

maxlen = max([len(k) for k in missing.keys()]) + 5

for k, v in missing.items():
    print('{:{maxlen}} {}'.format(k, ','.join(v), maxlen=maxlen))
