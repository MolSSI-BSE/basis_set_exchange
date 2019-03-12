"""
Tests for lookups of elemental data
"""

import pytest
from basis_set_exchange import lut

_all_elements = list(range(1, 119))
_all_elements_str = [str(x) for x in _all_elements]
_all_elements.extend(_all_elements_str)
_all_am = list(range(1, 13))


@pytest.mark.parametrize('Z', _all_elements)
def test_element_data(Z):
    # Cycle through the elements and check that
    # the info returned from the functions is consistent
    data = lut.element_data_from_Z(Z)
    assert data[1] == int(Z)

    assert data == lut.element_data_from_sym(data[0])
    assert data == lut.element_data_from_name(data[2])

    assert data[0] == lut.element_sym_from_Z(Z)
    assert data[2] == lut.element_name_from_Z(Z)

    nsym = lut.element_sym_from_Z(Z, True)
    nname = lut.element_name_from_Z(Z, True)

    assert int(Z) == lut.element_Z_from_sym(nsym.upper())

    # Check capitalization
    assert nsym[0] == data[0][0].upper()
    assert nname[0] == data[2][0].upper()


@pytest.mark.parametrize('am', _all_am)
def test_amchar(am):
    # Check that converting am characters, etc, is consistent
    s = lut.amint_to_char([am])
    assert am == lut.amchar_to_int(s)[0]

    combined = list(range(am + 1))
    s = lut.amint_to_char(combined)
    assert combined == lut.amchar_to_int(s)


def test_amchar_special():
    s = lut.amint_to_char([5, 6, 7])
    assert s == 'hik'
    s = lut.amint_to_char([5, 6, 7], hij=True)
    assert s == 'hij'
    s = lut.amint_to_char([0, 1])
    assert s == 'sp'
    s = lut.amint_to_char([0, 1], use_L=True)
    assert s == 'l'


@pytest.mark.parametrize('Z', [150, '150'])
def test_element_data_fail(Z):
    with pytest.raises(KeyError, match=r'No element data for Z'):
        lut.element_data_from_Z(Z)


@pytest.mark.parametrize('am', [[1, -1], [1, 100]])
def test_amint_to_char_fail(am):
    with pytest.raises(IndexError, match=r'Angular momentum.*(out of range|must be a positive)'):
        lut.amint_to_char(am)
