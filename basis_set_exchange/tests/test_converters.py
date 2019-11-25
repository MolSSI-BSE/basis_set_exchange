"""
Tests for the BSE main API
"""

import basis_set_exchange as bse
import pytest

from .common_testvars import bs_formats, ref_formats


@pytest.mark.parametrize('fmt', bs_formats)
def test_get_format_extensions(fmt):
    """For all basis set formats, get the extension
    """
    bse.converters.get_format_extension(fmt)


@pytest.mark.parametrize('fmt', ref_formats)
def test_get_refformat_extensions(fmt):
    """For all basis set formats, get the extension
    """
    bse.refconverters.get_format_extension(fmt)
