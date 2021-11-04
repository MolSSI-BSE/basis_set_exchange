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
Tests for lookups of elemental data
"""

import pytest
from basis_set_exchange import lut, api
from .common_testvars import bs_metadata

ecp_basis_sets = [k for k, v in bs_metadata.items() if 'scalar_ecp' in v['function_types']]


@pytest.mark.slow
@pytest.mark.parametrize('basis_name', ecp_basis_sets)
def test_stored_nelec_start_slow(basis_name):
    bs_data = api.get_basis(basis_name)

    for el in bs_data['elements'].values():
        if 'ecp_electrons' not in el:
            continue

        ecp_electrons = el['ecp_electrons']
        starting_shells = lut.electron_shells_start(ecp_electrons, 8)

        # Make sure the number of covered electrons matches
        nelec_sum = 0
        for am, count in enumerate(starting_shells):
            # How many shells of AM are covered by the ECP
            covered = count - 1

            # Adjust for the principal quantum number where the shells for the AM start
            # (ie, p start at 2, d start at 3)
            covered -= am

            # Number of orbs = 2*am+1. Multiply by 2 to get electrons
            nelec_sum += (2 * am + 1) * 2 * covered

        assert nelec_sum == ecp_electrons
