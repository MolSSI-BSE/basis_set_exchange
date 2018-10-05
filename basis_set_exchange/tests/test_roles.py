"""
Tests for sanity of auxiliary basis sets
"""

import basis_set_exchange as bse

from .common_testvars import *

def test_roles():
    """Make sure all basis sets have a role that is in api.get_roles()
    """

    roles = bse.get_roles()

    # All the roles in the metadata
    for k,v in bs_metadata.items():
        r = v['role']
        assert(r in roles)
