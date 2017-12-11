"""
Tests for converting to basis set formats
"""

import bse
import pytest

@pytest.mark.parametrize("basis_name", ["6-31G", "6-31GSS", "6-31PPGSS", "LANL2DZ"])
def test_converters(basis_name):
    bse.converters.write_g94(bse.get_basis_set(basis_name))
    bse.converters.write_nwchem(bse.get_basis_set(basis_name))
