"""
Tests for the BSE main API
"""

import random

import basis_set_exchange as bse
import pytest
from basis_set_exchange import lut

from .common_testvars import *

# Use random for getting sets of elements
random.seed(rand_seed, version=2)

@pytest.mark.parametrize('basis_name', bs_names)
def test_get_basis_1(basis_name):
    """For all versions of basis sets, test a simple get_basis
    """
    this_metadata = bs_metadata[basis_name]
    for ver in this_metadata['versions'].keys():
        bse.get_basis(basis_name, version=ver)


@pytest.mark.parametrize('basis_name', bs_names)
def test_get_basis_2(basis_name):
    """For all versions of basis sets, test a simple get_basis
       with different element selections
    """
    this_metadata = bs_metadata[basis_name]
    latest = this_metadata['latest_version']
    avail_elements = this_metadata['versions'][latest]['elements']
    nelements = random.randint(1, len(avail_elements))
    selected_elements = random.sample(avail_elements, nelements)

    # Change some selected elements to strings 
    for idx in range(len(selected_elements)):
        if idx % 3 == 1:
            selected_elements[idx] = lut.element_sym_from_Z(selected_elements[idx])
        elif idx % 3 == 2:
            selected_elements[idx] = str(selected_elements[idx])

    bs = bse.get_basis(basis_name, elements=selected_elements)
    assert len(bs['basis_set_elements']) == len(selected_elements)


@pytest.mark.parametrize('basis_name', bs_names_sample)
@pytest.mark.parametrize('bool_opts', bool_matrix(5))
def test_get_basis_3(basis_name, bool_opts):
    """For a sample of basis sets, test different options
    """
    bse.get_basis(basis_name,
                  uncontract_general=bool_opts[0],
                  uncontract_segmented=bool_opts[1],
                  uncontract_spdf=bool_opts[2],
                  make_general=bool_opts[3],
                  optimize_general=bool_opts[4])


@pytest.mark.parametrize('basis_name', bs_names_sample)
@pytest.mark.parametrize('fmt', bs_formats)
def test_get_basis_4(basis_name, fmt):
    """For a sample of basis sets, test getting different formats
       of the latest version
    """
    bse.get_basis(basis_name, fmt=fmt)


@pytest.mark.parametrize('basis_name', bs_names_sample)
def test_get_basis_memo(basis_name):
    """For a sample of basis sets, test memoization
    """
    bs1 = bse.get_basis(basis_name)
    bs2 = bse.get_basis(basis_name)

    # Should be equal, but not aliased
    assert bs1 == bs2
    assert bs1['basis_set_elements'] is not bs2['basis_set_elements']


@pytest.mark.parametrize('basis_name', bs_names)
@pytest.mark.parametrize('fmt', ref_formats)
def test_get_references_1(basis_name, fmt):
    """ Tests getting references for all basis sets
    """
    this_metadata = bs_metadata[basis_name]
    for ver in this_metadata['versions'].keys():
        bse.get_references(basis_name, fmt=fmt, version=ver)

        avail_elements = this_metadata['versions'][ver]['elements']
        nelements = random.randint(1, len(avail_elements))
        selected_elements = random.sample(avail_elements, nelements)
        bse.get_references(basis_name, elements=selected_elements, fmt=fmt, version=ver)


@pytest.mark.parametrize('primary_basis,role,expected', role_tests)
def test_lookup_by_role(primary_basis, role, expected):
    """Test looking up data by role
    """
    bs = bse.lookup_basis_by_role(primary_basis, role)
    assert bs.lower() == expected.lower()


@pytest.mark.parametrize('basis_name', bs_names)
def test_notes(basis_name):
    """Test getting family, family notes, and basis set notes
    """
    bse.get_basis_notes(basis_name)
    fam = bse.get_basis_family(basis_name)
    bse.get_family_notes(fam)

