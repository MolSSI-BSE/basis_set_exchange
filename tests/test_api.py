"""
Tests for the BSE main API
"""

import bse
from bse import lut
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
@pytest.mark.parametrize('opt_gen', _true_false)
def test_get_basis(basis_name, fmt, unc_general, unc_seg, unc_spdf, opt_gen):
    this_metadata = _bs_metadata[basis_name]
    for ver in this_metadata['versions'].keys():
        bs = bse.get_basis(basis_name, elements=None, fmt=fmt,
                           version=ver,
                           uncontract_general=unc_general,
                           uncontract_segmented=unc_seg,
                           uncontract_spdf=unc_spdf,
                           optimize_general=opt_gen)

        # Get subset of elements
        avail_elements = this_metadata['versions'][ver]['elements']
        nelements = random.randint(1, len(avail_elements))
        selected_elements = random.sample(avail_elements, nelements)

        # Change some selected elements to strings 
        for idx in range(len(selected_elements)):
            if idx % 2 == 0:
                selected_elements[idx] = lut.element_sym_from_Z(selected_elements[idx])
            
        bs = bse.get_basis(basis_name, elements=selected_elements,
                           fmt=fmt,
                           version=ver,
                           uncontract_general=unc_general,
                           uncontract_segmented=unc_seg,
                           uncontract_spdf=unc_spdf,
                           optimize_general=opt_gen)


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


_role_tests = [ ('cc-pvdz', 'mp2fit', 'cc-pvdz-mp2fit'),
                ('cc-pvtz', 'mp2fit', 'cc-pvtz-mp2fit'),
                ('cc-pvqz', 'mp2fit', 'cc-pvqz-mp2fit'),
                ('aug-cc-pvdz', 'mp2fit', 'aug-cc-pvdz-mp2fit'),
                ('aug-cc-pvtz', 'mp2fit', 'aug-cc-pvtz-mp2fit'),
                ('aug-cc-pvqz', 'mp2fit', 'aug-cc-pvqz-mp2fit')
              ]

@pytest.mark.parametrize('primary_basis,role,expected', _role_tests)
def test_lookup_by_role(primary_basis, role, expected):
    bs = bse.lookup_basis_by_role(primary_basis, role)
    assert bs.lower() == expected.lower()
