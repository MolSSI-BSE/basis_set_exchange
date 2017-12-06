"""
Tests for the BSE exposed API
"""

import bse
import pytest

@pytest.mark.parametrize("basis_name", ["6-31G"])
def test_get_basis_set(basis_name):
    bse.get_basis_set(basis_name)
