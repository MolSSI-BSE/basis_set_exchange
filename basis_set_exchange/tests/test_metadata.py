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
Tests for BSE metadata
"""

import os
import pytest
import glob

from basis_set_exchange import api, curate, fileio
from .common_testvars import data_dir, all_table_files, all_metadata_files


def test_get_metadata():
    '''Test the get_metadata function in the API'''

    api.get_metadata(data_dir)


def test_metadata_uptodate(tmp_path):
    '''Tests that the METADATA.json file is up to date'''

    tmp_path = str(tmp_path)  # Needed for python 3.5
    old_path = os.path.join(data_dir, 'METADATA.json')

    # Create a temporary file
    new_path = os.path.join(tmp_path, 'NEW_METADATA.json')
    curate.create_metadata_file(str(new_path), data_dir)

    old_metadata = fileio.read_metadata(old_path)
    new_metadata = fileio.read_metadata(new_path)
    assert old_metadata == new_metadata


@pytest.mark.parametrize('meta_file_path', all_metadata_files)
def test_basis_metadata_pair1(meta_file_path):
    '''Test that each metadata file is paired with a table basis
       in the same directory
    '''

    bsname = os.path.basename(meta_file_path).split('.')[0]
    meta_subdir = os.path.dirname(meta_file_path)
    test_path = os.path.join(data_dir, meta_subdir, bsname)
    test_files = glob.glob(test_path + '.*.table.json')
    assert len(test_files) > 0


@pytest.mark.parametrize('table_file_path', all_table_files)
def test_basis_metadata_pair2(table_file_path):
    '''Test that each table basis is paired with a metadata file
       in the same directory
    '''

    bsname = os.path.basename(table_file_path).split('.')[0]
    table_subdir = os.path.dirname(table_file_path)
    test_file = os.path.join(table_subdir, bsname) + '.metadata.json'
    assert test_file in all_metadata_files


@pytest.mark.parametrize('bs1,bs2', [('6-311g**', '6-311g(d,p)')])
def test_basis_metadata_duplicate(bs1, bs2):
    bsdata1 = api.get_basis(bs1)
    bsdata2 = api.get_basis(bs2)

    # The names are going to be different
    n1 = bsdata1.pop('name')
    n2 = bsdata2.pop('name')

    assert n1 != n2
    assert bsdata1 == bsdata2
