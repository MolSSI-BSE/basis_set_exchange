"""
Tests BSE manip functions
"""

import os
import pytest

from basis_set_exchange import api, curate, manip
from .common_testvars import bs_names_sample, bs_names

@pytest.mark.parametrize('basis', bs_names_sample)
def test_manip_roundtrip(basis):
    bse_dict = api.get_basis(basis, uncontract_general=True, uncontract_spdf=True)
    bse_dict_gen = manip.make_general(bse_dict)
    bse_dict_unc = manip.uncontract_general(bse_dict_gen)

    assert curate.compare_basis(bse_dict, bse_dict_unc, rel_tol=0.0)


@pytest.mark.slow
@pytest.mark.parametrize('basis', bs_names)
def test_manip_roundtrip_slow(basis):
    bse_dict = api.get_basis(basis, uncontract_general=True, uncontract_spdf=True)
    bse_dict_gen = manip.make_general(bse_dict)
    bse_dict_unc = manip.uncontract_general(bse_dict_gen)
    bse_dict_unc = manip.prune_basis(bse_dict_unc)

    assert curate.compare_basis(bse_dict, bse_dict_unc, rel_tol=0.0)
