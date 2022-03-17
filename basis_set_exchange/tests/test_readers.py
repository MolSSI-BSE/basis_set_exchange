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
Tests functions for reading in formatted basis sets
"""

import bz2
import os
import pytest

from basis_set_exchange import readers
from .common_testvars import reader_test_data_dir

subdirs = [x for x in os.listdir(reader_test_data_dir)]
subdirs = [os.path.join(reader_test_data_dir, x) for x in subdirs]
subdirs = [x for x in subdirs if os.path.isdir(x)]

test_files = []
for subdir in subdirs:
    subfiles = os.listdir(subdir)
    subfiles = [os.path.join(subdir, x) for x in subfiles if x.endswith('.bz2')]
    subfiles = [os.path.relpath(x, reader_test_data_dir) for x in subfiles]
    test_files.extend(subfiles)


@pytest.mark.parametrize('file_rel_path', test_files)
def test_reader(file_rel_path):
    file_path = os.path.join(reader_test_data_dir, file_rel_path)
    is_bad = ".bad." in os.path.basename(file_path)

    if is_bad:
        # Read the first line of the file. This will contain the string
        # that should match the exception
        with bz2.open(file_path, 'rt', encoding='utf-8') as tf:
            match = tf.readline()

        # Get what we want to match as part of the exception
        match = match[8:].strip()

        with pytest.raises(Exception, match=match):
            readers.read_formatted_basis_file(file_path)
    else:
        # Also validate the result (as both component and minimal)
        readers.read_formatted_basis_file(file_path, validate=True, as_component=True)
        readers.read_formatted_basis_file(file_path, validate=True, as_component=False)


def test_reader_equivalent():
    # Test the two dalton formats. These two files are the same basis in the two slightly-different
    # format.
    file1 = os.path.join(reader_test_data_dir, 'dalton', '6-31g.good.1.mol.bz2')
    file2 = os.path.join(reader_test_data_dir, 'dalton', '6-31g.good.2.mol.bz2')
    data1 = readers.read_formatted_basis_file(file1)
    data2 = readers.read_formatted_basis_file(file2)

    assert data1 == data2
