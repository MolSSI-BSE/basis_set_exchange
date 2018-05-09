"""
Tests BSE curation functions
"""

import bse
import pytest

data_dir = bse.default_data_dir


@pytest.mark.parametrize('basis1, basis2, element, expected', [
                              ['6-31g', '6-31g*', 6, True],
                              ['6-31g', '6-31g**', 6, True],
                              ['6-31g*', '6-31g*', 6, True],
                              ['6-31g*', '6-31g', 6, False],
                              ['6-31g*', '6-31g', 1, True],
                              ['6-31g**', '6-31g', 1, False],
                              ['cc-pvtz', 'aug-cc-pvtz', 13, True]
                         ]) 
def test_electron_subset(basis1, basis2, element, expected):
    el1 = bse.get_basis_set(basis1)['basis_set_elements'][element]
    el2 = bse.get_basis_set(basis2)['basis_set_elements'][element]
    shells1 = el1['element_electron_shells']
    shells2 = el2['element_electron_shells']
    assert bse.curate.electron_shells_are_subset(shells1, shells2) == expected


@pytest.mark.parametrize('basis1, basis2, element, expected', [
                              ['6-31g', '6-31g', 8, True],
                              ['6-31g', '6-31g*', 8, False],
                              ['6-31g', '6-31g**', 8, False],
                              ['6-31g', '6-31g**', 1, False],
                              ['6-31g', '6-31g*', 1, True],
                              ['cc-pvtz', 'aug-cc-pvtz', 13, False]
                         ]) 
def test_electron_equal(basis1, basis2, element, expected):
    el1 = bse.get_basis_set(basis1)['basis_set_elements'][element]
    el2 = bse.get_basis_set(basis2)['basis_set_elements'][element]
    shells1 = el1['element_electron_shells']
    shells2 = el2['element_electron_shells']
    assert bse.curate.electron_shells_are_equal(shells1, shells2) == expected
    assert bse.curate.electron_shells_are_equal(shells2, shells1) == expected


@pytest.mark.parametrize('basis1, basis2, element, expected', [
                              ['CRENBL', 'CRENBL', 78, True],
                              ['CRENBL', 'CRENBL', 92, True],
                              ['CRENBL', 'CRENBL', 118, True],
                              ['LANL2DZ', 'LANL2DZ', 78, True],
                              ['CRENBL', 'LANL2DZ', 78, False],
                              ['LANL2DZ', 'CRENBL', 78, False]
                         ]) 
def test_ecp_equal(basis1, basis2, element, expected):
    el1 = bse.get_basis_set(basis1)['basis_set_elements'][element]
    el2 = bse.get_basis_set(basis2)['basis_set_elements'][element]
    shells1 = el1['element_ecp']
    shells2 = el2['element_ecp']
    assert bse.curate.ecp_pots_are_equal(shells1, shells2) == expected


@pytest.mark.parametrize('basis1, basis2, element, expected', [
                              ['6-31g', '6-31g', 8, True],
                              ['6-31g', '6-31g*', 8, False],
                              ['6-31g', '6-31g**', 8, False],
                              ['6-31g', '6-31g**', 1, False],
                              ['6-31g', '6-31g*', 1, True],
                              ['aug-cc-pvtz', 'aug-cc-pvqz', 15, False],
                              ['aug-cc-pvtz', 'aug-cc-pvdz', 18, False],
                              ['CRENBL', 'CRENBL', 78, True],
                              ['CRENBL', 'CRENBL', 92, True],
                              ['CRENBL', 'CRENBL', 118, True],
                              ['CRENBL', 'LANL2DZ', 78, False],
                              ['LANL2DZ', 'CRENBL', 78, False]
                         ]) 
def test_compare_elements(basis1, basis2, element, expected):
    el1 = bse.get_basis_set(basis1)['basis_set_elements'][element]
    el2 = bse.get_basis_set(basis2)['basis_set_elements'][element]
    assert bse.curate.compare_elements(el1, el2) == expected
    assert bse.curate.compare_elements(el2, el1) == expected
