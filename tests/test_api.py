"""
Tests for the BSE exposed API
"""

import bse
import pytest

def test_get_basis_set():
    bs_metadata = bse.get_metadata()
    formats = bse.get_formats()

    for basis_name in bs_metadata.keys():
        # Test combinations of contration options
        unc_comb = [(False, False, False),
                    (False, False, True),
                    (False, True, False),
                    (False, True, True),
                    (True, False, False),
                    (True, False, True),
                    (True, True, False),
                    (True, True, True)]

        # TODO - test getting subsets of elements
        for f in formats:
            for unc in unc_comb:
                bse.get_basis_set(basis_name, elements=None, fmt=f,
                                  uncontract_general=unc[0],
                                  uncontract_segmented=unc[1],
                                  uncontract_spdf=unc[2])



def test_get_references():
    bs_metadata = bse.get_metadata()
    formats = bse.get_reference_formats()

    for basis_name in bs_metadata.keys():
        # TODO - test getting subsets of elements
        for f in formats:
            bse.get_references(basis_name, elements=None, fmt=f)


# TODO - Add keys to test (when filtering is available)
@pytest.mark.parametrize("keys", [None])
def test_get_metadata(keys):
    bse.get_metadata(keys=keys, key_filter=None)
