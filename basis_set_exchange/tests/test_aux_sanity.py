"""
Tests for sanity of auxiliary basis sets
"""

import basis_set_exchange as bse
import pytest

from .common_testvars import *

@pytest.mark.parametrize('basis_name', bs_names)
def test_aux_sanity(basis_name):
    """For all basis sets, check that

       1. All aux basis sets exist
       2. That the role of the aux basis set matches the role in
          the orbital basis
    """

    this_metadata = bs_metadata[basis_name]

    for role,aux in this_metadata['auxiliaries'].items():
        assert(aux in bs_metadata)
        aux_metadata = bs_metadata[aux]

        assert(role == aux_metadata['role'])

