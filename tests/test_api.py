"""
Tests for the BSE exposed API
"""

import bse
import pytest

@pytest.mark.parametrize("basis_name", ["6-31G", "6-31GSS", "6-31PPGSS", "LANL2DZ"])
def test_get_basis_set(basis_name):
    bse.get_basis_set(basis_name)
