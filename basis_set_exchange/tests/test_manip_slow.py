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
Tests BSE manipulation functions (manip)
"""

import pytest

from basis_set_exchange import api, curate, manip, sort
from .common_testvars import bs_names


@pytest.mark.slow
@pytest.mark.parametrize('basis', bs_names)
def test_manip_roundtrip_slow(basis):
    bse_dict = api.get_basis(basis)
    bse_dict_gen = manip.make_general(bse_dict)
    bse_dict_unc = manip.uncontract_general(bse_dict_gen)
    bse_dict_unc = manip.prune_basis(bse_dict_unc)
    bse_dict_sort = sort.sort_basis(bse_dict_unc)

    bse_dict = manip.uncontract_general(bse_dict)
    bse_dict = manip.uncontract_spdf(bse_dict)
    assert curate.compare_basis(bse_dict, bse_dict_unc, rel_tol=0.0)
    assert curate.compare_basis(bse_dict, bse_dict_sort, rel_tol=0.0)

    bse_dict_gen = manip.prune_basis(bse_dict_gen)
    bse_dict_gen2 = manip.make_general(bse_dict_unc)
    bse_dict_gen2 = manip.prune_basis(bse_dict_gen2)
    assert curate.compare_basis(bse_dict_gen, bse_dict_gen2, rel_tol=0.0)
