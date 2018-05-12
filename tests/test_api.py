"""
Tests for the BSE exposed API
"""

import bse
import pytest
import random

# Use random for getting sets of elements
_rand_seed = 39466 # from random.org
random.seed(_rand_seed, version=2)

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
    this_metadata = _bs_metadata[basis_name]
    for ver in this_metadata['versions'].keys():
        bs = bse.get_basis_set(basis_name, elements=None, fmt=fmt,
                               version=ver,
                               uncontract_general=unc_general,
                               uncontract_segmented=unc_seg,
                               uncontract_spdf=unc_spdf)

        # Get subset of elements
        avail_elements = this_metadata['versions'][ver]['elements']
        nelements = random.randint(1, len(avail_elements))
        selected_elements = random.sample(avail_elements, nelements)
        bs = bse.get_basis_set(basis_name, elements=selected_elements,
                               fmt=fmt,
                               version=ver,
                               uncontract_general=unc_general,
                               uncontract_segmented=unc_seg,
                               uncontract_spdf=unc_spdf)
        


@pytest.mark.parametrize('basis_name', _bs_names)
@pytest.mark.parametrize('fmt', _ref_formats)
def test_get_references(basis_name, fmt):
    this_metadata = _bs_metadata[basis_name]
    for ver in this_metadata['versions'].keys():
        bse.get_references(basis_name, elements=None, fmt=fmt, version=ver)

        avail_elements = this_metadata['versions'][ver]['elements']
        nelements = random.randint(1, len(avail_elements))
        selected_elements = random.sample(avail_elements, nelements)
        bse.get_references(basis_name, elements=selected_elements, fmt=fmt, version=ver)
