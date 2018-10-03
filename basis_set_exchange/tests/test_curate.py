"""
Tests BSE curation functions
"""

import os

import pytest
from basis_set_exchange import api, curate, fileio

_data_dir = api._default_data_dir


@pytest.mark.parametrize('basis1, basis2, element, expected', [
                              ['6-31g', '6-31g*', '6', True],
                              ['6-31g', '6-31g**', '6', True],
                              ['6-31g*', '6-31g*', '6', True],
                              ['6-31g*', '6-31g', '6', False],
                              ['6-31g*', '6-31g', '1', True],
                              ['6-31g**', '6-31g','1', False],
                              ['cc-pvtz', 'aug-cc-pvtz', '13', True]
                         ]) 
def test_electron_subset(basis1, basis2, element, expected):
    el1 = api.get_basis(basis1)['basis_set_elements'][element]
    el2 = api.get_basis(basis2)['basis_set_elements'][element]
    shells1 = el1['element_electron_shells']
    shells2 = el2['element_electron_shells']
    assert curate.electron_shells_are_subset(shells1, shells2, True) == expected


@pytest.mark.parametrize('basis1, basis2, element, expected', [
                              ['6-31g', '6-31g', '8', True],
                              ['6-31g', '6-31g*', '8', False],
                              ['6-31g', '6-31g**', '8', False],
                              ['6-31g', '6-31g**', '1', False],
                              ['6-31g', '6-31g*', '1', True],
                              ['cc-pvtz', 'aug-cc-pvtz', '13', False]
                         ]) 
def test_electron_equal(basis1, basis2, element, expected):
    el1 = api.get_basis(basis1)['basis_set_elements'][element]
    el2 = api.get_basis(basis2)['basis_set_elements'][element]
    shells1 = el1['element_electron_shells']
    shells2 = el2['element_electron_shells']
    assert curate.electron_shells_are_equal(shells1, shells2, True) == expected
    assert curate.electron_shells_are_equal(shells2, shells1, True) == expected


@pytest.mark.parametrize('basis1, basis2, element, expected', [
                              ['CRENBL', 'CRENBL', '78', True],
                              ['CRENBL', 'CRENBL', '92', True],
                              ['CRENBL', 'CRENBL', '118', True],
                              ['LANL2DZ', 'LANL2DZ', '78', True],
                              ['CRENBL', 'LANL2DZ', '78', False],
                              ['LANL2DZ', 'CRENBL', '78', False]
                         ]) 
def test_ecp_equal(basis1, basis2, element, expected):
    el1 = api.get_basis(basis1)['basis_set_elements'][element]
    el2 = api.get_basis(basis2)['basis_set_elements'][element]
    ecps1 = el1['element_ecp']
    ecps2 = el2['element_ecp']
    assert curate.ecp_pots_are_equal(ecps1, ecps2, True) == expected


@pytest.mark.parametrize('basis1, basis2, element, expected', [
                              ['6-31g', '6-31g', '8', True],
                              ['6-31g', '6-31g*', '8', False],
                              ['6-31g', '6-31g**', '8', False],
                              ['6-31g', '6-31g**', '1', False],
                              ['6-31g', '6-31g*', '1', True],
                              ['aug-cc-pvtz', 'aug-cc-pvqz', '15', False],
                              ['aug-cc-pvtz', 'aug-cc-pvdz', '18', False],
                              ['CRENBL', 'CRENBL', '78', True],
                              ['CRENBL', 'CRENBL', '92', True],
                              ['CRENBL', 'CRENBL', '118', True],
                              ['CRENBL', 'LANL2DZ', '78', False],
                              ['LANL2DZ', 'CRENBL', '78', False]
                         ]) 
def test_compare_elements(basis1, basis2, element, expected):
    el1 = api.get_basis(basis1)['basis_set_elements'][element]
    el2 = api.get_basis(basis2)['basis_set_elements'][element]
    assert curate.compare_elements(el1, el2, True, True, True) == expected
    assert curate.compare_elements(el2, el1, True, True, True) == expected


@pytest.mark.parametrize('basis, element', [
                              ['6-31g', '8'],
                              ['CRENBL', '3'],
                              ['CRENBL', '92'],
                              ['LANL2DZ', '78']
                         ])
def test_printing(basis, element):
    el = api.get_basis(basis)['basis_set_elements'][element]

    shells = el['element_electron_shells']
    curate.print_electron_shell(shells[0])

    if 'element_ecp' in el:
        ecps = el['element_ecp']
        curate.print_ecp_pot(ecps[0])

    curate.print_element(element, el)


@pytest.mark.parametrize('file_path', [
                              'dunning/cc-pVDZ_dunning1989a.1.json',
                              'crenb/CRENBL_ross1994a.0.json',
                              'crenb/CRENBL-ECP_ross1994a.0.json'
                         ])
def test_print_component_basis(file_path):
    full_path = os.path.join(_data_dir, file_path)
    comp = fileio.read_json_basis(full_path)
    curate.print_component_basis(comp)


@pytest.mark.parametrize('file_path', [
                              'dunning/cc-pVDZ.1.element.json',
                              'crenb/CRENBL.0.element.json'
                         ])
def test_print_elemental_basis(file_path):
    full_path = os.path.join(_data_dir, file_path)
    el = fileio.read_json_basis(full_path)
    curate.print_element_basis(el)


@pytest.mark.parametrize('file_path', [
                              'cc-pVDZ.1.table.json',
                              'CRENBL.0.table.json'
                         ])
def test_print_table_basis(file_path):
    full_path = os.path.join(_data_dir, file_path)
    tab = fileio.read_json_basis(full_path)
    curate.print_table_basis(tab)
