"""
Tests for the BSE exposed API
"""

import bse
import pytest

@pytest.mark.parametrize("basis_name,elements", [("6-31G", None),
                                                 ("6-31G", [1,2,3,4,5]),
                                                 ("6-31GSS", [6,7,8,9,10]),
                                                 ("6-31PPGSS", None),
                                                 ("LANL2DZ", None),
                                                 ("LANL2DZ", [24,25,26,92])])
def test_get_basis_set(basis_name, elements):
    bse.get_basis_set(basis_name, elements=elements)

@pytest.mark.parametrize("keys", [None])
def test_get_metadata(keys):
    bse.get_metadata(keys=keys, key_filter=None)
