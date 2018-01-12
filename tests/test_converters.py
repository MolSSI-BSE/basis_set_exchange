"""
Tests for converting to basis set formats
"""

import bse
import pytest

#@pytest.mark.parametrize("basis_name", ["6-31G", "6-31GSS", "6-31PPGSS-AGG", "LANL2DZ"])
#def test_converters(basis_name):
#
#    formats = bse.converters.converter_map
#    bs = bse.get_basis_set(basis_name)
#
#    for name,func in formats.items():
#        func(bs)
