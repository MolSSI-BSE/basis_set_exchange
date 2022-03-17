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

"""
Tests BSE curation functions
"""

import os
import pytest

from basis_set_exchange import api, readers, curate, manip, sort
from .common_testvars import bs_names_sample

# NOTE: CFour reader does not currently support ECP
roundtrip_formats = ['turbomole', 'gaussian94', 'nwchem']


@pytest.mark.parametrize('basis', bs_names_sample)
@pytest.mark.parametrize('fmt', roundtrip_formats)
def test_curate_roundtrip(tmp_path, basis, fmt):
    tmp_path = str(tmp_path)  # Needed for python 3.5

    # Many formats have limitations on general contractions
    if fmt == 'gaussian94':
        uncontract_general = True
        make_general = False
        uncontract_spdf = 1
    if fmt == 'turbomole':
        uncontract_general = True
        make_general = False
        uncontract_spdf = 0
    if fmt == 'nwchem':
        uncontract_general = False
        make_general = False
        uncontract_spdf = 1
    if fmt == 'cfour':
        uncontract_general = False
        make_general = True
        uncontract_spdf = 0

    bse_formatted = api.get_basis(basis, fmt=fmt)
    bse_dict = api.get_basis(basis, uncontract_general=uncontract_general, make_general=make_general)
    bse_dict = manip.uncontract_spdf(bse_dict, uncontract_spdf)

    outfile_path = os.path.join(tmp_path, 'roundtrip.txt')
    with open(outfile_path, 'w', encoding='utf-8') as outfile:
        outfile.write(bse_formatted)

    test_dict = readers.read_formatted_basis_file(outfile_path, fmt)

    test_dict = sort.sort_basis(test_dict)
    bse_dict = sort.sort_basis(bse_dict)

    # Compare, ignoring metadata (not stored in most formats)
    assert curate.compare_basis(bse_dict, test_dict, rel_tol=0.0)
