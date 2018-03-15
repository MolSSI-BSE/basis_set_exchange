"""
Tests for the BSE exposed API
"""

import bse
import pytest

@pytest.mark.parametrize('unc_general', [True, False])
@pytest.mark.parametrize('unc_seg', [True, False])
@pytest.mark.parametrize('unc_spdf', [True, False])
def test_get_basis_set(unc_general, unc_seg, unc_spdf):
    bs_metadata = bse.get_metadata()
    formats = bse.get_formats()

    for basis_name in bs_metadata.keys():
        for ver in bs_metadata[basis_name]['versions'].keys():

            # TODO - test getting subsets of elements
            for f in formats.keys():
                bse.get_basis_set(basis_name, elements=None, fmt=f,
                                  version=ver,
                                  uncontract_general=unc_general,
                                  uncontract_segmented=unc_seg,
                                  uncontract_spdf=unc_spdf)



def test_get_references():
    bs_metadata = bse.get_metadata()
    formats = bse.get_reference_formats()

    for basis_name in bs_metadata.keys():
        # TODO - test getting subsets of elements
        for f in formats.keys():
            bse.get_references(basis_name, elements=None, fmt=f)
