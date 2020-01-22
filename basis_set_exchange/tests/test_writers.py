"""
Tests for the BSE main API
"""

import basis_set_exchange as bse
import pytest
import os

from .common_testvars import bs_write_formats, ref_formats, bs_names_sample

my_formats = [x for x in bs_write_formats if x is not None]

@pytest.mark.parametrize('fmt', bs_write_formats)
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
@pytest.mark.parametrize('bs_fmt', my_formats)
@pytest.mark.parametrize('as_bz2', [True, False])
def test_write_basis_file(bs_name, bs_fmt, as_bz2, tmp_path):
    '''Test writing a basis set to a file'''

    tmp_path = str(tmp_path)  # Needed for python 3.5

    bs_data = bse.get_basis(bs_name)
    out_file = bse.misc.basis_name_to_filename(bs_name)
    out_file += bse.writers.get_format_extension(bs_fmt)

    if as_bz2:
        out_file += '.bz2'

    outfile_path = os.path.join(tmp_path, out_file)
    bse.writers.write_formatted_basis_file(bs_data, outfile_path, bs_fmt)
