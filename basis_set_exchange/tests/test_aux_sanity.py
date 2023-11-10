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
Tests for sanity of auxiliary basis sets
"""

import pytest

from .common_testvars import bs_names, bs_metadata
from ..misc import transform_basis_name


@pytest.mark.parametrize('basis_name', bs_names)
def test_aux_sanity(basis_name):
    """For all basis sets, check that

       1. All aux basis sets exist
       2. That the role of the aux basis set matches the role in
          the orbital basis
    """

    this_metadata = bs_metadata[basis_name]

    for role, auxs in this_metadata['auxiliaries'].items():
        if isinstance(auxs, str):
            auxs = [auxs]

        for aux in auxs:
            assert aux in bs_metadata
            aux_metadata = bs_metadata[aux]

            assert role == aux_metadata['role']


@pytest.mark.parametrize('basis_name', bs_names)
def test_aux_reverse(basis_name):
    """Make sure all aux basis sets are paired with at least one orbital basis set
    """

    this_metadata = bs_metadata[basis_name]
    role = this_metadata['role']
    if role == 'orbital' or role == 'guess':
        return

    # All possible names for this auxiliary set
    # We only have to match one
    all_aux_names = this_metadata["other_names"] + [basis_name]
    all_aux_names = [transform_basis_name(x) for x in all_aux_names]

    # Find where this basis set is listed as an auxiliary
    found = False
    for k, v in bs_metadata.items():
        aux = v['auxiliaries']
        for aux_role, aux_names in aux.items():
            if isinstance(aux_names, str):
                aux_names = [aux_names]

            for aux_name in aux_names:
                if aux_name in all_aux_names:
                    assert aux_role == role
                    found = True

    assert found
