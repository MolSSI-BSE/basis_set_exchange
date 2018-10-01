"""
Tests for lookups of elemental data
"""

import pytest
from basis_set_exchange import lut

_all_elements = list(range(1,119))
_all_am = list(range(1, 13))

@pytest.mark.parametrize('Z', _all_elements)
def test_element_data(Z):
    # Cycle through the elements and check that 
    # the info returned from the functions is consistent
    data = lut.element_data_from_Z(Z)
    assert data[1] == Z

    assert data == lut.element_data_from_sym(data[0])
    assert data == lut.element_data_from_name(data[2])

    assert data[0] == lut.element_sym_from_Z(Z)
    assert data[2] == lut.element_name_from_Z(Z)

    nsym = lut.element_sym_from_Z(Z, True)
    nname = lut.element_name_from_Z(Z, True)

    assert nsym[0] == data[0][0].upper()
    assert nname[0] == data[2][0].upper()


@pytest.mark.parametrize('am', _all_am)
def test_amchar(am):
    # Check that converting am characters, etc, is consistent
    s = lut.amint_to_char([am])
    assert am == lut.amchar_to_int(s)[0]

    combined = list(range(am+1))
    s = lut.amint_to_char(combined)
    assert combined == lut.amchar_to_int(s)
