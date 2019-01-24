"""
Tests for sanity of auxiliary basis sets
"""

import basis_set_exchange as bse
import pytest

from .common_testvars import bs_names, bs_metadata


@pytest.mark.parametrize('basis_name', bs_names)
def test_aux_sanity(basis_name):
    """For all basis sets, check that

       1. All aux basis sets exist
       2. That the role of the aux basis set matches the role in
          the orbital basis
    """

    this_metadata = bs_metadata[basis_name]

    for role, aux in this_metadata['auxiliaries'].items():
        assert aux in bs_metadata
        aux_metadata = bs_metadata[aux]

        assert role == aux_metadata['role']


@pytest.mark.parametrize('basis_name', bs_names)
def test_aux_reverse(basis_name):
    """Make sure all aux basis sets are paired with at least one orbital basis set
    """

    this_metadata = bs_metadata[basis_name]
    r = this_metadata['role']
    if r == 'orbital':
        return

    # Find where this basis set is listed as an auxiliary
    found = False
    for k, v in bs_metadata.items():
        aux = v['auxiliaries']
        for ak, av in aux.items():
            if av == basis_name:
                assert ak == r
                found = True

    assert found
