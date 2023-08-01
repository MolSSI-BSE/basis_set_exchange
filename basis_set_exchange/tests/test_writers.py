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

import basis_set_exchange as bse
import pytest
import os

from .common_testvars import bs_write_formats_ecp, bs_write_formats_noecp, ref_formats, bs_names_sample_noecp, bs_names_sample

my_formats_ecp = [x for x in bs_write_formats_ecp if x is not None]
my_formats_noecp = [x for x in bs_write_formats_noecp if x is not None]


@pytest.mark.parametrize('fmt', bs_write_formats_ecp)
def test_get_format_extensions(fmt):
    """For all basis set formats, get the extension
    """
    bse.writers.get_format_extension(fmt)


@pytest.mark.parametrize('fmt', ref_formats)
def test_get_refformat_extensions(fmt):
    """For all basis set formats, get the extension
    """
    bse.refconverters.get_format_extension(fmt)


@pytest.mark.parametrize('bs_name', bs_names_sample)
@pytest.mark.parametrize('bs_fmt', my_formats_ecp)
@pytest.mark.parametrize('as_bz2', [True, False])
def test_write_basis_file_ecp(bs_name, bs_fmt, as_bz2, tmp_path):
    '''Test writing a basis set to a file'''

    tmp_path = str(tmp_path)  # Needed for python 3.5

    bs_data = bse.get_basis(bs_name)
    out_file = bse.misc.basis_name_to_filename(bs_name)
    out_file += bse.writers.get_format_extension(bs_fmt)

    if as_bz2:
        out_file += '.bz2'

    outfile_path = os.path.join(tmp_path, out_file)

    # Bit of a hack - crystal does not support > g projectors
    if bs_fmt == 'crystal' and bs_name == 'def2-tzvp':
        return

    bse.writers.write_formatted_basis_file(bs_data, outfile_path, bs_fmt)


@pytest.mark.parametrize('bs_name', bs_names_sample_noecp)
@pytest.mark.parametrize('bs_fmt', my_formats_noecp)
@pytest.mark.parametrize('as_bz2', [True, False])
def test_write_basis_file_noecp(bs_name, bs_fmt, as_bz2, tmp_path):
    '''Test writing a basis set to a file'''

    # bit of a hack - velox doesn't support cartesian
    if bs_fmt == 'veloxchem' and bs_name.startswith("6-31"):
        return

    tmp_path = str(tmp_path)  # Needed for python 3.5

    bs_data = bse.get_basis(bs_name)
    out_file = bse.misc.basis_name_to_filename(bs_name)
    out_file += bse.writers.get_format_extension(bs_fmt)

    if as_bz2:
        out_file += '.bz2'

    outfile_path = os.path.join(tmp_path, out_file)
    bse.writers.write_formatted_basis_file(bs_data, outfile_path, bs_fmt)
