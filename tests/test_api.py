"""
Tests for the BSE exposed API
"""

import bse
import pytest

# Load all the metadata once
_bs_metadata = bse.get_metadata()
_bs_names = bse.get_all_basis_names()
_bs_formats = list(bse.get_formats().keys())
_ref_formats = list(bse.get_reference_formats().keys())
_true_false = [ True, False ]

@pytest.mark.parametrize('basis_name', _bs_names)
@pytest.mark.parametrize('fmt', _bs_formats)
@pytest.mark.parametrize('unc_general', _true_false)
@pytest.mark.parametrize('unc_seg', _true_false)
@pytest.mark.parametrize('unc_spdf', _true_false)
def test_get_basis_set(basis_name, fmt, unc_general, unc_seg, unc_spdf):
    for ver in _bs_metadata[basis_name]['versions'].keys():
        # TODO - test getting subsets of elements
        bse.get_basis_set(basis_name, elements=None, fmt=fmt,
                          version=ver,
                          uncontract_general=unc_general,
                          uncontract_segmented=unc_seg,
                          uncontract_spdf=unc_spdf)


@pytest.mark.parametrize('basis_name', _bs_names)
@pytest.mark.parametrize('fmt', _ref_formats)
def test_get_references(basis_name, fmt):
    # TODO - test getting subsets of elements
    bse.get_references(basis_name, elements=None, fmt=fmt)
