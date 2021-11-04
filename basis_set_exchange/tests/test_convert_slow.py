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

import basis_set_exchange as bse
import os
import pytest

from basis_set_exchange import convert
from .common_testvars import bs_read_formats, bs_write_formats, bs_names_sample

# We only want formats that we can actually write out and read from
my_write_formats = [x for x in bs_write_formats if x is not None]
my_read_formats = [x for x in bs_read_formats if x in my_write_formats]

# TODO - molcas inline vs. separate file
my_read_formats.remove('molcas')


@pytest.mark.parametrize('basis_name', bs_names_sample)
@pytest.mark.parametrize('fmt_from', my_read_formats)
@pytest.mark.parametrize('fmt_to', my_write_formats)
def test_convert_slow(basis_name, fmt_from, fmt_to, tmp_path):
    tmp_path = str(tmp_path)  # Needed for python 3.5

    # First, get the basis set in the format we want to read from
    bs_data = bse.get_basis(basis_name)
    in_file = bse.misc.basis_name_to_filename(basis_name)
    in_file += '.{}{}'.format(fmt_from, bse.writers.get_format_extension(fmt_from))
    in_file_path = os.path.join(tmp_path, in_file)
    bse.writers.write_formatted_basis_file(bs_data, in_file_path, fmt_from)

    # Now attempt the conversion
    out_file_path = in_file_path + '.{}{}'.format(fmt_to, bse.writers.get_format_extension(fmt_to))

    convert.convert_formatted_basis_file(in_file_path, out_file_path, fmt_from, fmt_to)
