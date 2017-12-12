"""
Tests for the BSE exposed API
"""

import bse
import pytest

@pytest.mark.parametrize("basis_name,elements", [("6-31G", None),
                                                 ("6-31G", [1,2,3,4,5]),
                                                 ("6-31GSS", [6,7,8,9,10]),
                                                 ("6-31PPGSS-AGG", None),
                                                 ("LANL2DZ", None),
                                                 ("LANL2DZ", [24,25,26,92])])
def test_get_basis_set(basis_name, elements):
    bse.get_basis_set(basis_name, elements=elements)

    unc_comb = [(False, False, False),
                (False, False, True),
                (False, True, False),
                (False, True, True),
                (True, False, False),
                (True, False, True),
                (True, True, False),
                (True, True, True)]

    formats = bse.get_formats()
    for f in formats:
        for unc in unc_comb:
            bse.get_basis_set(basis_name, elements=elements, fmt=f,
                              uncontract_general=unc[0],
                              uncontract_segmented=unc[0],
                              uncontract_spdf=unc[0])


@pytest.mark.parametrize("basis_name,unc",
                         [("LANL2DZ", (False, False, False)),
                          ("LANL2DZ", (False, False, True)),
                          ("LANL2DZ", (False, True, False)),
                          ("LANL2DZ", (False, True, True)),
                          ("LANL2DZ", (True, False, False)),
                          ("LANL2DZ", (True, False, True)),
                          ("LANL2DZ", (True, True, False)),
                          ("LANL2DZ", (True, True, True))])
def test_get_basis_set_uncontract(basis_name, unc):
    bse.get_basis_set(basis_name,
                      uncontract_general=unc[0],
                      uncontract_segmented=unc[1],
                      uncontract_spdf=unc[2])




@pytest.mark.parametrize("keys", [None])
def test_get_metadata(keys):
    bse.get_metadata(keys=keys, key_filter=None)
