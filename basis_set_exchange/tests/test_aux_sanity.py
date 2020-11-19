"""
Tests for sanity of auxiliary basis sets
"""

import pytest

from .common_testvars import bs_names, bs_metadata
from ..misc import transform_basis_name


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
    role = this_metadata['role']
    if role == 'orbital' or role == 'guess':
        return

    # All possible names for this auxiliary set
    # We only have to match one
    all_aux_names = this_metadata["other_names"] + [basis_name]
    all_aux_names = [transform_basis_name(x) for x in all_aux_names]

    # Find where this basis set is listed as an auxiliary
    found = False
    for k, v in bs_metadata.items():
        aux = v['auxiliaries']
        for aux_role, aux_name in aux.items():
            if aux_name in all_aux_names:
                assert aux_role == role
                found = True

    assert found
