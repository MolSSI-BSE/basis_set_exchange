"""
Tests for the BSE main API
"""

import random
import pytest

import basis_set_exchange as bse

from .common_testvars import *

# Use random for getting sets of elements
random.seed(rand_seed, version=2)

# To test role lookup
# yapf: disable
role_tests = [('cc-pvdz', 'rifit', 'cc-pvdz-rifit'),
              ('def2-tzvp', 'jfit', 'def2-universal-jfit'),
              ('aug-cc-pv5z', 'jkfit', 'cc-pv5z-jkfit'),
              ('aug-cc-pv5z', 'jkfit', 'cc-pv5z-jkfit'),
              ('aug-pcseg-1', 'admmfit', 'aug-admm-1')]
# yapf: enable


@pytest.mark.parametrize("basis_name, basis_ver", bs_names_vers)
def test_get_basis_1(basis_name, basis_ver):
    """For all versions of basis sets, test a simple get_basis"""
    bse.get_basis(basis_name, version=basis_ver)


@pytest.mark.parametrize("basis_name", bs_names)
def test_get_basis_2(basis_name):
    """For all versions of basis sets, test a simple get_basis
    with different element selections
    """
    this_metadata = bs_metadata[basis_name]
    latest = this_metadata["latest_version"]
    avail_elements = this_metadata["versions"][latest]["elements"]
    nelements = random.randint(1, len(avail_elements))
    selected_elements = random.sample(avail_elements, nelements)

    # Change some selected elements to strings
    for idx in range(len(selected_elements)):
        if idx % 3 == 1:
            selected_elements[idx] = bse.lut.element_sym_from_Z(selected_elements[idx])
        elif idx % 3 == 2:
            selected_elements[idx] = str(selected_elements[idx])

    bs = bse.get_basis(basis_name, elements=selected_elements)
    assert len(bs["elements"]) == len(selected_elements)

    # Try to get as an integer
    bs = bse.get_basis(basis_name, elements=int(selected_elements[0]))
    assert len(bs["elements"]) == 1


@pytest.mark.parametrize("basis_name", bs_names_sample)
@pytest.mark.parametrize("bool_opts", bool_matrix(5))
def test_get_basis_3(basis_name, bool_opts):
    """For a sample of basis sets, test different options"""
    bse.get_basis(
        basis_name,
        uncontract_general=bool_opts[0],
        uncontract_segmented=bool_opts[1],
        uncontract_spdf=bool_opts[2],
        make_general=bool_opts[3],
        optimize_general=bool_opts[4],
    )


@pytest.mark.parametrize("basis_name", bs_names_sample)
@pytest.mark.parametrize("fmt", bs_write_formats)
def test_get_basis_4(basis_name, fmt):
    """For a sample of basis sets, test getting different formats
    of the latest version
    """
    bse.get_basis(basis_name, fmt=fmt)


@pytest.mark.parametrize("basis_name", bs_names)
@pytest.mark.parametrize("fmt", ref_formats)
def test_get_references_1(basis_name, fmt):
    """Tests getting references for all basis sets

    Also test getting references for a random selection of elements
    """
    this_metadata = bs_metadata[basis_name]
    for ver in this_metadata["versions"].keys():
        bse.get_references(basis_name, fmt=fmt, version=ver)

        avail_elements = this_metadata["versions"][ver]["elements"]
        nelements = random.randint(1, len(avail_elements))
        selected_elements = random.sample(avail_elements, nelements)
        bse.get_references(basis_name, elements=selected_elements, fmt=fmt, version=ver)


@pytest.mark.parametrize("primary_basis,role,expected", role_tests)
def test_lookup_by_role(primary_basis, role, expected):
    """Test looking up data by role"""
    bs = bse.lookup_basis_by_role(primary_basis, role)
    assert bs.lower() == expected.lower()


@pytest.mark.parametrize("basis_name", bs_names)
def test_notes(basis_name):
    """Test getting family, family notes, and basis set notes"""
    bse.get_basis_notes(basis_name)
    bse.has_basis_notes(basis_name)


@pytest.mark.parametrize("basis_name", bs_names)
def test_get_family(basis_name):
    """Test getting family"""

    fam = bse.get_basis_family(basis_name)
    assert fam in all_families


@pytest.mark.parametrize("family", all_families)
def test_family_notes(family):
    """Test getting family notes"""
    bse.has_family_notes(family)
    bse.get_family_notes(family)


# yapf: disable
@pytest.mark.parametrize('substr,family,role', [['def2', 'ahlrichs', 'orbital'],
                                                ['pVDz', None, None],
                                                [None, None, 'jkfit'],
                                                [None, 'pople', None]])
# yapf: enable
def test_filter(substr, family, role):
    """Test filtering basis set"""
    md = bse.filter_basis_sets(substr, family, role)
    assert len(md) > 0


# yapf: disable
@pytest.mark.parametrize('substr,family,role', [['def2', 'ahlrichs', 'jkfit'],
                                                ['qqqqq', None, None],
                                                ['6-31', None, 'admmfit']])
# yapf: enable
def test_filter_0(substr, family, role):
    """Test filtering basis set (returning zero results)"""
    md = bse.filter_basis_sets(substr, family, role)
    assert len(md) == 0


# yapf: disable
@pytest.mark.parametrize('fmts', [None,
                                  ['gto_spherical', 'scalar_ecp'],
                                  ['CARTESIAN_gto']])
# yapf: enable
def test_get_formats(fmts):
    """Test the get_formats function"""
    ret = bse.get_formats(fmts)

    # JSON is always supported
    assert len(ret) > 1


def test_get_reader_formats():
    """Test the get_reader_formats function"""
    bse.get_reference_formats()
