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
