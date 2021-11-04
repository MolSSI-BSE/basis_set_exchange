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
Tests BSE curation functions
"""

import os
import pytest
import shutil

from basis_set_exchange import api, curate, readers, fileio
from .common_testvars import data_dir, curate_test_data_dir


# yapf: disable
@pytest.mark.parametrize('basis1, basis2, element, expected', [
                              ['6-31g', '6-31g*', '6', True],
                              ['6-31g', '6-31g**', '6', True],
                              ['6-31g*', '6-31g*', '6', True],
                              ['6-31g*', '6-31g', '6', False],
                              ['6-31g*', '6-31g', '1', True],
                              ['6-31g**', '6-31g','1', False],
                              ['cc-pvtz', 'aug-cc-pvtz', '13', True]
                         ])
# yapf: enable
def test_electron_subset(basis1, basis2, element, expected):
    el1 = api.get_basis(basis1)['elements'][element]
    el2 = api.get_basis(basis2)['elements'][element]
    shells1 = el1['electron_shells']
    shells2 = el2['electron_shells']
    assert curate.electron_shells_are_subset(shells1, shells2, True) == expected


# yapf: disable
@pytest.mark.parametrize('basis1, basis2, element, expected', [
                              ['6-31g', '6-31g', '8', True],
                              ['6-31g', '6-31g*', '8', False],
                              ['6-31g', '6-31g**', '8', False],
                              ['6-31g', '6-31g**', '1', False],
                              ['6-31g', '6-31g*', '1', True],
                              ['cc-pvtz', 'aug-cc-pvtz', '13', False]
                         ])
# yapf: enable
def test_electron_equal(basis1, basis2, element, expected):
    el1 = api.get_basis(basis1)['elements'][element]
    el2 = api.get_basis(basis2)['elements'][element]
    shells1 = el1['electron_shells']
    shells2 = el2['electron_shells']
    assert curate.electron_shells_are_equal(shells1, shells2, True) == expected
    assert curate.electron_shells_are_equal(shells2, shells1, True) == expected


# yapf: disable
@pytest.mark.parametrize('basis1, basis2, element, expected', [
                              ['CRENBL', 'CRENBL', '78', True],
                              ['CRENBL', 'CRENBL', '92', True],
                              ['CRENBL', 'CRENBL', '118', True],
                              ['LANL2DZ', 'LANL2DZ', '78', True],
                              ['CRENBL', 'LANL2DZ', '78', False],
                              ['LANL2DZ', 'CRENBL', '78', False]
                         ])
# yapf: enable
def test_ecp_equal(basis1, basis2, element, expected):
    el1 = api.get_basis(basis1)['elements'][element]
    el2 = api.get_basis(basis2)['elements'][element]
    ecps1 = el1['ecp_potentials']
    ecps2 = el2['ecp_potentials']
    assert curate.ecp_pots_are_equal(ecps1, ecps2, True) == expected


# yapf: disable
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
# yapf: enable
def test_compare_elements(basis1, basis2, element, expected):
    el1 = api.get_basis(basis1)['elements'][element]
    el2 = api.get_basis(basis2)['elements'][element]
    assert curate.compare_elements(el1, el2, True, True, True) == expected
    assert curate.compare_elements(el2, el1, True, True, True) == expected


def test_diff_json_files_same(tmp_path):
    tmp_path = str(tmp_path)  # Needed for python 3.5

    filename = 'def2-SV-base.1.json'
    file1 = os.path.join(data_dir, 'ahlrichs', 'SV', filename)
    tmpfile = os.path.join(tmp_path, filename)
    shutil.copyfile(file1, tmpfile)

    curate.diff_json_files([tmpfile], [tmpfile])

    diff_file = tmpfile + '.diff'
    assert os.path.isfile(diff_file)

    diff_data = fileio.read_json_basis(diff_file)
    assert len(diff_data['elements']) == 0


def test_diff_json_files(tmp_path):
    tmp_path = str(tmp_path)  # Needed for python 3.5

    filename1 = '6-31G_s_s-full.json.bz2'
    filename2 = '6-31G-full.json.bz2'

    file1 = os.path.join(curate_test_data_dir, filename1)
    file2 = os.path.join(curate_test_data_dir, filename2)

    tmpfile1 = os.path.join(tmp_path, filename1)
    tmpfile2 = os.path.join(tmp_path, filename2)

    shutil.copyfile(file1, tmpfile1)
    shutil.copyfile(file2, tmpfile2)

    curate.diff_json_files([tmpfile1], [tmpfile2])
    curate.diff_json_files([tmpfile2], [tmpfile1])

    diff1 = fileio.read_json_basis(tmpfile1 + '.diff')
    diff2 = fileio.read_json_basis(tmpfile2 + '.diff')

    assert len(diff1['elements']) == 36
    assert len(diff2['elements']) == 0

    reffilename = '6-31G_s_s-polarization.json.bz2'
    reffile = os.path.join(curate_test_data_dir, reffilename)
    refdata = fileio.read_json_basis(reffile)

    assert curate.compare_basis(diff1, refdata, rel_tol=0.0)


def test_g94_scaling(tmp_path):
    tmp_path = str(tmp_path)  # Needed for python 3.5

    filename1 = 'sbo4-dz-scaled.gbs.bz2'
    filename2 = 'sbo4-dz-unscaled.gbs.bz2'

    file1 = os.path.join(curate_test_data_dir, filename1)
    file2 = os.path.join(curate_test_data_dir, filename2)

    bs1 = readers.read_formatted_basis_file(file1)
    bs2 = readers.read_formatted_basis_file(file2)

    assert curate.compare_basis(bs1, bs2, rel_tol=1.0e-14)
