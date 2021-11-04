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
Tests for the BSE main API
"""

import pytest

import basis_set_exchange as bse


@pytest.mark.parametrize('basis_name', ['cc-pv0z', 'madeup_name'])
def test_get_basis_fail_name(basis_name):
    """Test get_basis with bad names """

    with pytest.raises(KeyError, match=r'Basis set.*does not exist'):
        bse.get_basis(basis_name)


@pytest.mark.parametrize('elements', [100, '100', [1, 100], [1, '100']])
def test_get_basis_fail_elements(elements):
    """Test get_basis with bad elements """

    with pytest.raises(KeyError, match=r'Element.*not found in basis'):
        bse.get_basis('cc-pvdz', elements=elements)


@pytest.mark.parametrize('fmt', ['nwchemm', 'nofmt'])
def test_get_basis_fail_fmt(fmt):
    """Test get_basis with bad formats """

    with pytest.raises(RuntimeError, match=r'Unknown basis set format'):
        bse.get_basis('cc-pvdz', fmt=fmt)


@pytest.mark.parametrize('version', ['v1', -1, '-1', 100])
def test_get_basis_fail_version(version):
    """Test get_basis with bad versions """

    with pytest.raises(KeyError, match=r'Version .* does not exist for basis'):
        bse.get_basis('cc-pvdz', version=version)


def test_get_basis_fail_data_dir(tmp_path):
    """Test get_basis with bad data dir """

    tmp_path = str(tmp_path)  # Needed for python 3.5

    with pytest.raises(FileNotFoundError, match=r'JSON file .* does not exist'):
        bse.get_basis('cc-pvdz', data_dir=tmp_path)


def test_get_all_basis_names_fail(tmp_path):
    """Test get_all_basis_names with bad data dir """

    tmp_path = str(tmp_path)  # Needed for python 3.5

    with pytest.raises(FileNotFoundError, match=r'JSON file .* does not exist'):
        bse.get_all_basis_names(tmp_path)


@pytest.mark.parametrize('basis_name', ['cc-pv0z', 'madeup_name'])
def test_lookup_role_fail_name(basis_name):
    """Test get_basis with bad versions """

    with pytest.raises(KeyError, match=r'Basis set.*does not exist'):
        bse.lookup_basis_by_role(basis_name, 'rifit')


@pytest.mark.parametrize('role', ['madeup_name', 'admmfit'])
def test_lookup_role_fail_role(role):
    """Test get_basis with bad role """

    with pytest.raises(RuntimeError, match=r'Role.*(not a valid role|exist for)'):
        bse.lookup_basis_by_role('def2-tzvp', role)


# yapf: disable
@pytest.mark.parametrize('substr,family,role', [['def2', 'ahlrichsx', 'jkfit'],
                                                ['qqqqq', None, 'notarole'],
                                                ['6-31', 'poplexx,', 'admmfit']])
# yapf: enable
def test_filter_fail(substr, family, role):
    """Test filtering basis set (returning zero results)"""

    with pytest.raises(RuntimeError, match=r'(Family|Role).*not a valid (family|role)'):
        md = bse.filter_basis_sets(substr, family, role)
