# Copyright (c) 2017-2022 The Molecular Sciences Software Institute, Virginia Tech
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

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


#yapf: disable
@pytest.mark.parametrize('nelectrons,expected', [[0, [1,2,3,4]],
                                                 [2, [2,2,3,4]],
                                                 [12, [4,3,3,4]],
                                                 [18, [4,4,3,4]],
                                                 [48, [6,5,5,4]],
                                                 [56, [7,6,5,4]],
                                                 [88, [8,7,6,5]],
                                                 [118, [8,8,7,6]],
                                                ])
#yapf: enable
def test_electron_shells_start(nelectrons, expected):
    assert expected == lut.electron_shells_start(nelectrons, 3)
    expected.extend([5, 6, 7, 8, 9])
    assert expected == lut.electron_shells_start(nelectrons, 8)


@pytest.mark.parametrize('nelectrons', [1, 13, 31, 34, 43, 75, 106])
def test_electron_shells_start_fail(nelectrons):
    with pytest.raises(RuntimeError, match=r'Electrons cover a partial shell'):
        lut.electron_shells_start(nelectrons)
    with pytest.raises(RuntimeError, match=r'negative number of electrons'):
        lut.electron_shells_start(-nelectrons)
    with pytest.raises(NotImplementedError, match=r'Too many electrons'):
        lut.electron_shells_start(nelectrons + 120)
