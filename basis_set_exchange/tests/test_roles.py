"""
Tests for sanity of auxiliary basis sets
"""

import basis_set_exchange as bse
import pytest

from .common_testvars import bs_names, all_roles, bs_metadata


@pytest.mark.parametrize('basis_name', bs_names)
def test_roles(basis_name):
    """Make sure all basis sets have a role that is in api.get_roles()
    """

    bs_role = bs_metadata[basis_name]['role']
    assert bs_role in all_roles
